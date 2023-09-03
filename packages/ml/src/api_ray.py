import os
import time

import ray

from utils.util import configure_logging

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import torch

dc = torch.cuda.device_count()
print('dc', dc)

import requests
from typing import Annotated
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import  Depends, FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi import Request


from login import User, get_current_user

import logging

from ray import serve
from .api import Ask, ask, startup, shutdown

ray.init()

logging.basicConfig(level=logging.DEBUG)


app = FastAPI()

# app.include_router(loginRouter)

origins = ["*"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_origin_regex=".*",
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=['X-Request-ID'],
# )
#
app.add_middleware(CorrelationIdMiddleware)


@serve.deployment(route_prefix="/", num_replicas=1)
@serve.ingress(app)
class FastAPIWrapper:

    @app.post("/ask/")
    async def ask(self, request: Request, body: Ask, current_user: Annotated[User, Depends(get_current_user)]) -> StreamingResponse:
        return await ask(request, body, current_user)

    @app.on_event("startup")
    async def startup(self):
        await startup()

    @app.on_event("shutdown")
    async def shutdown(self):
        await shutdown()


serve.run(FastAPIWrapper.bind())

r = requests.post("http://localhost:8000/ask", json={
    'question': 'Who is Amin?'
}, headers={
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIweGYzOWZkNmU1MWFhZDg4ZjZmNGNlNmFiODgyNzI3OWNmZmZiOTIyNjYiLCJleHAiOjE2ODc4OTc2MjR9.zIu7wnT2WjX0PRnnVcCvxRKhfgqB3OnWi-lExjAHdjk'},
                  stream=True)

start = time.time()
r.raise_for_status()
for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
    print(f"Got result {round(time.time() - start, 1)}s after start: '{chunk}'")
