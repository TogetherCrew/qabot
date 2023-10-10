import gc
import os
import traceback

from tc_messageBroker.rabbit_mq.queue import Queue
from logger.hivemind_logger import logger
from server.broker import EventBroker
from utils.constants import DB_CONNECTION_STR, DB_GUILD, OPENAI_API_KEY
from utils.util import configure_logging

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# import torch
#
# dc = torch.cuda.device_count()
# print('torch.cuda.device_count:', dc)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=3333, reload=True)
else:

    import asyncio
    from typing import Annotated, AsyncGenerator, Any
    from asgi_correlation_id import CorrelationIdMiddleware
    from fastapi import  Depends, FastAPI, Request
    from fastapi.responses import StreamingResponse
    from fastapi import HTTPException, Request
    from fastapi.exception_handlers import http_exception_handler
    from starlette.responses import Response

    from server.callback import AsyncChunkIteratorCallbackHandler, InfoChunk, TextChunk
    from pydantic import BaseModel

    from fastapi.middleware.cors import CORSMiddleware
    from server.callback import AsyncChunkIteratorCallbackHandler

    from asgi_correlation_id import correlation_id

    # from login import User, get_current_user, router as loginRouter

    eb = EventBroker()

    app = FastAPI()

    # app.include_router(loginRouter)

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=".*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=['X-Request-ID'],
    )
    #
    app.add_middleware(CorrelationIdMiddleware)


    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
        return await http_exception_handler(
            request,
            HTTPException(
                500,
                'Internal server error',
                headers={'X-Request-ID': correlation_id.get() or ""}
            ))


    class AsyncResponse(BaseModel):
        # background_tasks: BackgroundTasks
        callback_handler = AsyncChunkIteratorCallbackHandler()
        total_tokens = 0

        class Config:
            arbitrary_types_allowed = True

        @staticmethod
        def get_agent():
            from main import load
            return load()

        async def generate_response(self, request: Request, question: str) -> AsyncGenerator[str, None]:
        # async def generate_response(self, request: Request, question: str, user: User) -> AsyncGenerator[str, None]:
            run: asyncio.Task | None = None
            session = ''
            try:
                session = f"{request.headers['x-request-id']}"
                print("session", session)
                agent = AsyncResponse.get_agent()
                run = asyncio.create_task(agent.run(question, self.callback_handler))
                logger.info('Running...')
                print("Running")
                async for response in self.callback_handler.aiter():
                    # check token type
                    logger.info(response.__dict__)
                    if isinstance(response, TextChunk):
                        res_token = f'{response.token}\n\n'

                        # await a_publish(Queue.DISCORD_BOT, Event.DISCORD_BOT.SEND_MESSAGE,
                        # await eb.a_publish(Queue.DISCORD_BOT, "SEND_MESSAGE",
                        #                 {
                        #                     "uuid": f"s-{session}",
                        #                     "question": question,
                        #                     "streaming": res_token,
                        #                 })
                        yield res_token
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
                logger.exception('Something got wrong')
            except BaseException as e:  # asyncio.CancelledError
                print("Caught BaseException:", e)
                print(traceback.format_exc())
                logger.exception('Something got wrong')
            finally:

                logger.info(f'Total tokens used: {self.total_tokens}')
                # await eb.a_publish(Queue.DISCORD_BOT, "SEND_MESSAGE",
                #                 {"uuid": f"s-{session}",
                #                  "question": question,
                #                  "user": user.json(),
                #                  "total_tokens": self.total_tokens})

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


    @app.post("/ask/")
    async def ask(request: Request, body: Ask) -> StreamingResponse:

        logger.info(f"Received question:{body.question}")
        session = f"{request.headers['x-request-id']}"
        logger.debug(
            f'session: {session} ip:{request.client.host}:{request.client.port}')

        # await eb.a_publish(Queue.DISCORD_BOT, "SEND_MESSAGE",
        #                 {
        #                     "uuid": f"s-{session}",
        #                     "question": body.question,
        #                     "user": current_user.json(),
        #                 })

        ar = AsyncResponse()
        return StreamingResponse(AsyncResponse.streamer(ar.generate_response(request, body.question)))


    # def on_event(message: dict[str, Any]) -> None:
    #     logger.info("on_event %s", message)
    #     if message['event'] == "SEND_MESSAGE":
    #         logger.info("on_event %s", message['event'])
    #     elif message['event'] == "UPDATED_STORE":
    #         logger.info("UPDATED_STORE %s", message)
    #     else:
    #         logger.info("Event not registered: %s", message['event'])


    @app.on_event("startup")
    async def startup():
        configure_logging()
        # eb.connect()
        # Queue.HIVEMIND_API, Event.HIVEMIND_API.RECEIVED_MESSAGE
        # eb.t_listen("HIVEMIND_API", "RECEIVED_MESSAGE", on_event)
        eb.t_listen("HIVEMIND_API", "RUN", lambda msg : logger.info(f"msg:{msg}"))
        eb.t_listen("HIVEMIND_API", "UPDATED_STORE", lambda msg : logger.info(f"msg:{msg}"))

        print("Server Startup!")


    @app.on_event("shutdown")
    async def shutdown():
        print("Server Shutdown!")
