import gc
import os
import traceback

from tc_messageBroker.rabbit_mq.queue import Queue
from tc_messageBroker.rabbit_mq.event import Event
from logger.hivemind_logger import logger
from server.async_broker import AsyncBroker
from utils.util import configure_logging

import aiormq

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

    # from login import User, get_current_user, router as loginRouter

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
                logger.error("caught cancelled error")


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

    # def log_event(msg):
    #     logger.info(f"queue: {EventBroker.get_queue_by_event(msg['event'])} msg:{msg}")

    def log_event(msg: str, queue_name: str, event_name: str):
        logger.info(f"{queue_name}->{event_name}::{msg}")


    ab = AsyncBroker()

    @app.on_event("startup")
    async def startup():
        configure_logging()

        try:
            await ab.connect()
            loop = asyncio.get_event_loop()
            loop.set_debug(True)
            logger.info(loop)

            asyncio.get_event_loop().create_task(ab.listen(queue_name=Queue.DISCORD_ANALYZER,
                                                           event_name=Event.DISCORD_ANALYZER.RUN,
                                                           callback=log_event
                                                           ))

            asyncio.get_event_loop().create_task(ab.listen(queue_name=Queue.DISCORD_ANALYZER,
                                                           event_name=Event.DISCORD_ANALYZER.RUN_ONCE,
                                                           callback=log_event
                                                           ))

            asyncio.get_event_loop().create_task(ab.listen(queue_name=Queue.HIVEMIND,
                                                           event_name=Event.HIVEMIND.GUILD_MESSAGES_UPDATED,
                                                           callback=log_event
                                                           ))
        except aiormq.exceptions.AMQPConnectionError as amqp:
            logger.error(amqp)

        # test_broker_main()
        #
        # eb = EventBroker()
        # eb.t_listen(Queue.HIVEMIND)
        # eb.add_event(Event.HIVEMIND.GUILD_MESSAGES_UPDATED, log_event)
        # # eb.add_event(Event.HIVEMIND.INTERACTION_CREATED, log_event)
        #
        # eb2 = EventBroker()
        # eb2.t_listen(Queue.TWITTER_BOT)
        # eb2.add_event(Event.TWITTER_BOT.SEND_MESSAGE, log_event)
        # #
        # eb3 = EventBroker()
        # eb3.t_listen(Queue.DISCORD_ANALYZER)
        # eb3.add_event(Event.DISCORD_ANALYZER.RUN, log_event)
        # eb3.add_event(Event.DISCORD_ANALYZER.RUN_ONCE, log_event)

        # logger.info(f"QueueObj.DISCORD_ANALYZER.event.RUN: {QueueObj.DISCORD_ANALYZER.event.RUN}")

        print("Server Startup!")


    @app.on_event("shutdown")
    async def shutdown():
        if ab:
            await ab.connection.close()
        print("Server Shutdown!")
