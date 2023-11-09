import gc
import os
import traceback
from asyncio import Task

from logger.hivemind_logger import logger
from server.async_broker import AsyncBroker
from utils.constants import HIVEMIND_API_PORT
from utils.util import configure_logging

import aiormq

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0",
                port=int(HIVEMIND_API_PORT),
                reload=False)
else:

    import asyncio
    from typing import AsyncGenerator
    from asgi_correlation_id import CorrelationIdMiddleware
    from fastapi import FastAPI, Request
    from fastapi.responses import StreamingResponse
    from fastapi import HTTPException, Request
    from fastapi.exception_handlers import http_exception_handler
    from starlette.responses import Response

    from server.callback import AsyncChunkIteratorCallbackHandler, InfoChunk, TextChunk
    from pydantic import BaseModel

    from fastapi.middleware.cors import CORSMiddleware
    from server.callback import AsyncChunkIteratorCallbackHandler

    from asgi_correlation_id import correlation_id

    ERROR_MESSAGE = f"An error occurred when trying to answer your question. An error report has been sent to " \
                    f"the developers."

    app = FastAPI()

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
                status_code=500,
                detail=f'Internal server error: {exc}',
                headers={'X-Request-ID': correlation_id.get() or ""}
            ))

    # create / route for health check
    @app.get("/")
    async def root():
        return "OK"

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
            run: asyncio.Task | None = None

            session = ''
            try:
                session = f"{request.headers['x-request-id']}"
                logger.debug(f"session: {session}")

                agent = AsyncResponse.get_agent()
                run = asyncio.create_task(agent.run(question, self.callback_handler))

                logger.info('Running...')

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
                logger.info("Run Done")
            except BaseException as e:  # asyncio.CancelledError
                logger.error(f"session:{session}  Caught BaseException: {str(e)}")
                print(traceback.format_exc())
                logger.exception('Something got wrong')
                yield ERROR_MESSAGE
            finally:
                logger.info(f'Total tokens used: {self.total_tokens}')
                # await eb.a_publish(Queue.DISCORD_BOT, "SEND_MESSAGE",
                #                 {"uuid": f"s-{session}",
                #                  "question": question,
                #                  "user": user.json(),
                #                  "total_tokens": self.total_tokens})

                # yield ERROR_MESSAGE

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
                logger.error("caught cancelled error", exc_info=True)

    class Ask(BaseModel):
        question: str


    @app.post("/ask/")
    async def ask(request: Request, body: Ask) -> StreamingResponse:

        logger.info(f"Received question:{body.question}")
        session = f"{request.headers['x-request-id']}"
        logger.debug(f'session: {session}')

        # await eb.a_publish(Queue.DISCORD_BOT, "SEND_MESSAGE",
        #                 {
        #                     "uuid": f"s-{session}",
        #                     "question": body.question,
        #                     "user": current_user.json(),
        #                 })

        ar = AsyncResponse()
        return StreamingResponse(AsyncResponse.streamer(ar.generate_response(request, body.question)))


    def log_event(msg: str, queue_name: str, event_name: str):
        logger.info(f"{queue_name}->{event_name}::{msg}")


    ######################################
    ### STARTUP GLOBALS VARIABLES HERE ###
    ######################################

    ab = AsyncBroker()
    hivemind_task: Task | None = None


    @app.on_event("startup")
    async def startup():
        configure_logging()

        try:
            await ab.connect()
            loop = asyncio.get_event_loop()
            loop.set_debug(True)
            # logger.info(loop)

            # hivemind_task = asyncio.get_event_loop().create_task(ab.listen(queue_name=Queue.HIVEMIND,
            #                                                                event_name=Event.HIVEMIND.GUILD_MESSAGES_UPDATED,
            #                                                                callback=log_event
            #                                                                ))
        except aiormq.exceptions.AMQPConnectionError as amqp:
            logger.error(amqp)

        print("Server Startup!")


    @app.on_event("shutdown")
    async def shutdown():
        if hivemind_task:
            hivemind_task.cancel()
        if ab and ab.connection:
            await ab.connection.close()
        print("Server Shutdown!")
