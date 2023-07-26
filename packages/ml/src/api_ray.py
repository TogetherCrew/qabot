import gc
import os
import time
import traceback

import ray

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import torch

dc = torch.cuda.device_count()
print('dc', dc)


import asyncio
import requests
from web3 import Web3
from functools import lru_cache
from typing import Annotated, AsyncGenerator
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import BackgroundTasks, Depends, FastAPI, Request, status
from fastapi.responses import StreamingResponse
from fastapi import HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from starlette.responses import Response

from server.callback import AsyncChunkIteratorCallbackHandler, InfoChunk, TextChunk
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware
from server.callback import AsyncChunkIteratorCallbackHandler


from asgi_correlation_id import correlation_id
from logging.config import dictConfig

from login import User, get_current_user, router as loginRouter

import logging

from ray import serve

ray.init()

logging.basicConfig(level=logging.DEBUG)

qabot_logger = logging.getLogger("ray.serve")
qabot_logger.setLevel(logging.DEBUG)

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


#
# @app.exception_handler(Exception)
# async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
#     return await http_exception_handler(
#         request,
#         HTTPException(
#             500,
#             'Internal server error',
#             headers={'X-Request-ID': correlation_id.get() or ""}
#         ))

class Settings(BaseModel):
    ENVIRONMENT: str = 'local'


settings = Settings()


def configure_logging() -> None:
    dictConfig(
        {
            'version': 1,
            'disable_existing_loggers': False,
            'filters': {  # correlation ID filter must be added here to make the %(correlation_id)s formatter work
                'correlation_id': {
                    '()': 'asgi_correlation_id.CorrelationIdFilter',
                    'uuid_length': 8 if not settings.ENVIRONMENT == 'local' else 32,
                    'default_value': '-',
                },
            },
            'formatters': {
                'console': {
                    'class': 'logging.Formatter',
                    'datefmt': '%H:%M:%S',
                    # formatter decides how our console logs look, and what info is included.
                    # adding %(correlation_id)s to this format is what make correlation IDs appear in our logs
                    'format': '%(levelname)s:\t\b%(asctime)s %(name)s:%(lineno)d [%(correlation_id)s] %(message)s',
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    # Filter must be declared in the handler, otherwise it won't be included
                    'filters': ['correlation_id'],
                    'formatter': 'console',
                },
            },
            # Loggers can be specified to set the log-level to log, and which handlers to use
            'loggers': {
                # project logger
                'app': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True},
                # third-party package loggers
                'databases': {'handlers': ['console'], 'level': 'WARNING'},
                'httpx': {'handlers': ['console'], 'level': 'INFO'},
                'asgi_correlation_id': {'handlers': ['console'], 'level': 'WARNING'},
            },
        }
    )


class AsyncResponse(BaseModel):
    background_tasks: BackgroundTasks
    callback_handler = AsyncChunkIteratorCallbackHandler()
    total_tokens = 0

    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def get_agent():
        from main import load
        return load()

    async def generate_response(self, request: Request, question: str, user: User) -> AsyncGenerator[str, None]:
        run: asyncio.Task | None = None
        try:
            session = f"{request.headers['x-request-id']}"
            print("session", session)
            agent = AsyncResponse.get_agent()
            run = asyncio.create_task(agent.run(question, self.callback_handler))
            qabot_logger.info('Running...')
            print("Running")
            async for response in self.callback_handler.aiter():
                # check token type
                qabot_logger.info(response.__dict__)
                if isinstance(response, TextChunk):
                    yield response.token + "\n\n"
                elif isinstance(response, InfoChunk):
                    self.total_tokens += response.count_tokens
                    print("Info:", response)

            await run
            del agent
            gc.collect()
            print("Run Done")
        except Exception as e:
            print("Caught Exception:", e)
            print(traceback.format_exc())
            logging.exception('Something got wrong')
        except BaseException as e:  # asyncio.CancelledError
            print("Caught BaseException:", e)
            print(traceback.format_exc())
            logging.exception('Something got wrong')
        finally:
            # async def charge_user():
            #     print("Charging user:", user.address, self.total_tokens)
            #     if await user.charge(self.total_tokens):
            #         await user.stake_balance()
            #
            # if self.total_tokens > 0:
            #     stake_balance = await user.stake_balance()
            #     if stake_balance >= self.total_tokens:
            #         self.background_tasks.add_task(charge_user)
            #     else:
            #         print(f'Not enough stake_balance {stake_balance} for total_tokens: {self.total_tokens}')
            # else:
            #     print('Not enough tokens consumed to charge:', self.total_tokens)
            if run:
                run.cancel()
                del run

    @staticmethod
    async def streamer(gen: AsyncGenerator[str, None]):
        try:
            async for i in gen:
                yield i
                await asyncio.sleep(0.25)
        except asyncio.CancelledError:
            print("caught cancelled error")


class Ask(BaseModel):
    question: str


@serve.deployment(route_prefix="/", num_replicas=1)
@serve.ingress(app)
class FastAPIWrapper:

    @app.post("/ask/")
    async def ask(self, request: Request, body: Ask, current_user: Annotated[User, Depends(get_current_user)],
                  background_tasks: BackgroundTasks) -> StreamingResponse:
        print("Received question:", body.question)
        qabot_logger.info(f"Received question:{body.question}")
        print(f'current_user:{current_user.address}')
        session = f"{request.headers['x-request-id']}"
        print("session", session)
        print(f'{request.client.host}:{request.client.port}')
        qabot_logger.debug(f'address:{current_user.address} ip:{request.client.host}:{request.client.port}')
        # get ip from request
        if await current_user.stake_balance() < Web3.to_wei(5000, "ether"):
            # raise ValueError("Not enough stake balance, need at least 5000 BOT tokens")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not enough stake balance, need at least 5000 BOT tokens",
            )

        ar = AsyncResponse(background_tasks=background_tasks)
        return StreamingResponse(AsyncResponse.streamer(ar.generate_response(request, body.question, current_user)))

    @app.on_event("startup")
    async def startup():
        configure_logging()
        print("Server Startup!")
        # try:
        #     await call_contract_stake()
        #     # await charge_stake(address="0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266",amount_in_ethers=100)
        #     # await staked_balance_for(address="0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266")
        # except Exception as e:
        #     print("Error calling contract:", e)
        #     print("Probably RPC node it's down")

    @app.on_event("shutdown")
    async def shutdown():
        print("Server Shutdown!")


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
