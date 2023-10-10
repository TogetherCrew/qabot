import os
from typing import Any

from pydantic.main import BaseModel

from server.broker import EventBroker
from utils.constants import OPENAI_API_KEY, DB_CONNECTION_STR, DB_GUILD

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# import torch


# dc = torch.cuda.device_count()
# print('dc', dc)
if __name__ == "__main__":
    import uvicorn
    API_PORT = os.getenv('PORT', 1234)
    uvicorn.run("main:app", host="0.0.0.0", port=API_PORT, reload=True)
else:
    from starlette.background import BackgroundTasks
    from starlette.responses import Response

    from logger.embedding_logger import get_logger

    # from utils.util import configure_logging
    # import requests
    from asgi_correlation_id import CorrelationIdMiddleware
    from fastapi import FastAPI, Request, HTTPException
    from fastapi import Request

    import logging

    # from ray import serve

    logger = get_logger("vector_server")

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("pika").setLevel(logging.WARNING)

    eb = EventBroker()

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

    from redis import Redis, ConnectionError as RedisConnectionError
    from redis.lock import Lock as RedisLock
    from celery.result import AsyncResult

    from tasks import celery as task

    redis_instance = Redis.from_url(task.redis_url)
    lock = RedisLock(redis_instance, name="task_id")

    # REDIS_TASK_KEY = "current_task"


    class TaskOut(BaseModel):
        id: str
        result: Any | None
        traceback: str | None
        status: str | None
        meta: str | None


    def _to_task_out(r: AsyncResult) -> TaskOut:
        return TaskOut(id=r.task_id, status=r.status,result=r.result,traceback=r.traceback,meta=str(r._get_task_meta()))


    @app.get("/")
    async def status(request: Request) -> Response:
        return Response(content="OK")


    @app.get("/update/")
    def vectorstore_update(request: Request, background_tasks: BackgroundTasks) -> Any:
        logger.info("vectorstore_update:")

        try:
            session = f"{request.headers['x-request-id']}"
            eb.publish("HIVEMIND_API", "UPDATED_STORE",
                    {"uuid": session, "data": '/update', "status": "STARTING"})

            logger.debug(f'session: {session} | ip:{request.client.host}:{request.client.port}')

            if not lock.acquire(blocking_timeout=4):
                raise HTTPException(status_code=500, detail="Could not acquire lock")

            if task.is_active_empty():
                # task_id = redis_instance.get(REDIS_TASK_KEY)

                # if task_id is None or task.celery.AsyncResult(task_id).ready():
                # no task was ever run, or the last task finished already
                r = task.vector_store_update.delay(session, OPENAI_API_KEY, DB_CONNECTION_STR, DB_GUILD)

                # redis_instance.set(REDIS_TASK_KEY, r.task_id)

                return _to_task_out(r)
            else:
                # the last task is still running!
                raise HTTPException(
                    status_code=400, detail="A task is already being executed"
                )
        except RedisConnectionError as rce:
            msg = f'RedisConnectionError: {rce}'
            logger.debug(msg)
            return Response(content=msg, status_code=503)
        except ConnectionError as ce: # TODO: ConnectionError should be custom error inside the broker tc lib, but its builtins
            msg = f'ConnectionError: {ce}'
            logger.debug(msg)
            return Response(content=msg, status_code=503)
        finally:
            try:
                lock.release()
            except:
                logger.debug('ConnectionError at lock release')


    @app.get("/status/{task_id}")
    def status(task_id: str = None) -> TaskOut:

        stats = task.celery.control.inspect().stats()

        logger.info(f'STATS {stats}')

        if stats and task.CELERY_HOSTNAME in stats:
            logger.info(f'STATS in {stats[task.CELERY_HOSTNAME]}')

        # if not task.has_active_task_id(task_id):
        #     # task_id = task_id or redis_instance.get(REDIS_TASK_KEY)
        #     # if task_id is None:
        #     raise HTTPException(
        #         status_code=400, detail=f"Could not determine task {task_id}"
        #     )
        r = task.celery.AsyncResult(task_id)
        return _to_task_out(r)


    @app.get("/kill/{task_id}")
    def kill(task_id: str) -> Response:
        if task_id is None:
            raise HTTPException(
                status_code=400, detail=f"Could not determine task {task_id}"
            )
        r = task.celery.AsyncResult(task_id)
        task.celery.control.revoke(task_id, terminate=True, signal="SIGKILL")
        return Response(content=f'Killing {task_id}')


    @app.on_event("startup")
    def startup():
        logger.info("started")


    @app.on_event("shutdown")
    def shutdown():
        logger.info("shutdown")
