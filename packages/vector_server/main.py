import os
from typing import Any, Optional, List, Annotated

from langchain.schema import Document
from pydantic.main import BaseModel

from utils.constants import OPENAI_API_KEY, DB_CONNECTION_STR, DB_GUILD, \
    DEFAULT_EMBEDDINGS, HIVEMIND_VS_PORT, DEEPLAKE_FOLDER, DEEPLAKE_PLATFORM_FOLDER, DEEPLAKE_RAW_FOLDER, \
    DEEPLAKE_SUMMARY_FOLDER
from langchain.vectorstores import DeepLake

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0",
                port=int(HIVEMIND_VS_PORT),
                reload=False)
else:
    from starlette.responses import Response

    from logger.embedding_logger import get_logger

    from asgi_correlation_id import CorrelationIdMiddleware
    from fastapi import FastAPI, Request, HTTPException, Query

    import logging

    logger = get_logger("VECTOR_SERVER")

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("pika").setLevel(logging.WARNING)

    # eb = EventBroker()

    app = FastAPI()

    app.add_middleware(CorrelationIdMiddleware)

    from redis import Redis, ConnectionError as RedisConnectionError
    from redis.lock import Lock as RedisLock
    from celery.result import AsyncResult

    from tasks import celery as task


    # redis_instance = Redis.from_url(task.REDIS_URI)
    # lock = RedisLock(redis_instance, name="task_id")

    class TaskOut(BaseModel):
        id: str
        result: Any | None
        traceback: str | None
        status: str | None
        meta: str | None


    def _to_task_out(r: AsyncResult) -> TaskOut:
        return TaskOut(id=r.task_id, status=r.status,
                       result=r.result, traceback=r.traceback,
                       meta=str(r._get_task_meta()))


    @app.get("/")
    async def status() -> Response:
        return Response(content="OK")


    # TODO maybe create another route using POST and query as body to avoid url encoding
    # TODO we should secure that endpoint with a token and/or IP allowlist
    @app.get("/search/{where}/{query}")
    def search(where: str = None, query: str = None, index: Optional[int] = 0, k: Optional[int] = 5) -> list[Document]:
        relevant_documents = None
        try:
            logger.info(f"search: where:{where} query :'{query}' index:{index} k:{k}")

            PATH_INDEX = f"_{index}"

            DEEPLAKE_RAW_PATH = os.path.join(DEEPLAKE_FOLDER, f"{DEEPLAKE_PLATFORM_FOLDER}{PATH_INDEX}",
                                             DEEPLAKE_RAW_FOLDER)
            DEEPLAKE_SUMMARY_PATH = os.path.join(DEEPLAKE_FOLDER, f"{DEEPLAKE_PLATFORM_FOLDER}{PATH_INDEX}",
                                                 DEEPLAKE_SUMMARY_FOLDER)

            path_to_use = DEEPLAKE_SUMMARY_PATH if where == '1' else DEEPLAKE_RAW_PATH

            if not os.path.exists(path_to_use):
                raise HTTPException(status_code=404, detail=f"Deeplake path not found: {path_to_use}")

            db = DeepLake(dataset_path=(path_to_use),
                          read_only=True,
                          embedding=DEFAULT_EMBEDDINGS
                          )
            relevant_documents = db.similarity_search(query=query, k=k)
            logger.debug(f"relevant_documents: {relevant_documents}")
        except BaseException as e:
            logger.error(e)
            raise HTTPException(status_code=404, detail=f"Error: {e}")

        return relevant_documents


    @app.get("/update/")
    def vectorstore_update(request: Request, dates: Annotated[List[str] | None, Query(description="List of dates to "
                                                                                                  "be collected")] =
    None
                           , channels: Annotated[List[str] | None, Query(description="List channels ids to be collected")] = None
                           , index: Annotated[int | None, Query(description="Indicate where store, if -1 automatic "
                                                                            "find next index, otherwise index choose,"
                                                                            " note it can append over the current "
                                                                            "store")] = -1) -> Any:
        try:
            session = f"{request.headers['x-request-id']}"
            # eb.publish("HIVEMIND_API", "UPDATED_STORE",
            #         {"uuid": session, "data": '/update', "status": "STARTING"})

            logger.debug(f'session: {session}')
            if index is None:
                index = -1
            # if not lock.acquire(blocking_timeout=4):
            #     raise HTTPException(status_code=500, detail="Could not acquire lock")
            if task.is_active_empty():
                r = task.vector_store_update.delay(session, OPENAI_API_KEY, DB_CONNECTION_STR, DB_GUILD, dates, channels, index)
                return _to_task_out(r)
            else:
                # the last task is still running!
                raise HTTPException(
                    status_code=400, detail=f"A task is already being executed id:{task.take_active_at(0)['id']}"
                )
        except RedisConnectionError as rce:
            msg = f'RedisConnectionError: {rce}'
            logger.debug(msg)
            return Response(content=msg, status_code=503)
        except ConnectionError as ce:
            # TODO: ConnectionError should be custom error inside the broker tc lib, but its builtins
            msg = f'ConnectionError: {ce}'
            logger.debug(msg)
            return Response(content=msg, status_code=503)
        # finally:
        #     try:
        #         lock.release()
        #     except BaseException:
        #         logger.debug('ConnectionError at lock release')


    @app.get("/status/{task_id}")
    def status(task_id: str = None) -> Any:
        try:
            stats = task.celery.control.inspect().stats()

            logger.info(f'STATS {stats}')

            if stats and task.CELERY_HOSTNAME in stats:
                logger.info(f'STATS in {stats[task.CELERY_HOSTNAME]}')

            if task.is_active_empty():
                return Response(content="Task list its empty", status_code=503)
            else:
                _, list = task.count_actives()
                # ['id']
                # check if task_id is in list using for and check against task['id']
                found = None
                for _task in list:
                    if 'id' in _task and _task['id'] == task_id:
                        found = _task
                        break

                if found is None:
                    return Response(content="Task not found", status_code=404)

                r = task.celery.AsyncResult(task_id)

                return _to_task_out(r)
        except RedisConnectionError as rce:
            msg = f'RedisConnectionError: {rce}'
            logger.debug(msg)
            return Response(content=msg, status_code=503)
        except ConnectionError as ce:
            # TODO: ConnectionError should be custom error inside the broker tc lib, but its builtins
            msg = f'ConnectionError: {ce}'
            logger.debug(msg)
            return Response(content=msg, status_code=503)


    @app.get("/kill/{task_id}")
    def kill(task_id: str) -> Response:
        if task_id is None:
            raise HTTPException(
                status_code=400, detail=f"Could not determine task {task_id}"
            )
        # r = task.celery.AsyncResult(task_id)
        task.celery.control.revoke(task_id, terminate=True, signal="SIGKILL")
        return Response(content=f'Killing {task_id}')


    @app.on_event("startup")
    def startup():
        logger.info("started")


    @app.on_event("shutdown")
    def shutdown():
        logger.info("shutdown")
