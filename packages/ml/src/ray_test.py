import asyncio
import logging
import time

from ray.serve._private.constants import SERVE_LOGGER_NAME

logging.getLogger(SERVE_LOGGER_NAME).setLevel(logging.DEBUG)

import time
from typing import Generator

import requests
from starlette.responses import StreamingResponse
from starlette.requests import Request

from fastapi import FastAPI
from ray import serve
import ray

ray.init()

app = FastAPI()



@serve.deployment(route_prefix="/")
@serve.ingress(app)
class FastAPIWrapper:

    @app.get("/")
    def f(self):
        return "Hello from the root!"

    def generate_numbers(self, max: int) -> Generator[str, None, None]:
        for i in range(max):
            yield str(i)
            time.sleep(5)

    @app.get("/ss")
    def ss(self, request: Request) -> StreamingResponse:
        max = request.query_params.get("max", "25")
        gen = self.generate_numbers(int(max))
        return StreamingResponse(gen, status_code=200, media_type="text/plain")

serve.run(FastAPIWrapper.bind())
# serve.run(StreamingResponder.bind())

r = requests.get("http://localhost:8000/", stream=False)
print(r.json())

async def runSync():
    r = requests.get("http://localhost:8000/ss?max=10", stream=True)
    start = time.time()
    r.raise_for_status()
    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
        print(f"Got result {round(time.time() - start, 1)}s after start: '{chunk}'")

async def main():
    return await  asyncio.gather(asyncio.create_task(runSync()),asyncio.create_task(runSync()))


asyncio.run(main())