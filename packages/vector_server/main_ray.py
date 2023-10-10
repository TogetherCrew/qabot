# import os
# # import time
#
# # import ray
# from starlette.background import BackgroundTasks
# from starlette.responses import Response
#
# from logger.hivemind_logger import get_logger
# # from server.broker import publish
# # from utils.constants import OPENAI_API_KEY, DB_CONNECTION_STR, DB_GUILD
# # from utils.util import configure_logging
#
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# # import torch
#
# # dc = torch.cuda.device_count()
# # print('dc', dc)
#
# import requests
# from asgi_correlation_id import CorrelationIdMiddleware
# from fastapi import FastAPI, Request
# from fastapi import Request
# from .main import status, vectorstore_update, startup as api_startup, shutdown as api_shutdown
# import logging
# # from ray import serve
#
# logger = get_logger("vector_server")
# ray.init()
#
# logging.basicConfig(level=logging.DEBUG)
#
# app = FastAPI()
#
# # app.include_router(loginRouter)
#
# origins = ["*"]
#
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=origins,
# #     allow_origin_regex=".*",
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# #     expose_headers=['X-Request-ID'],
# # )
# #
# app.add_middleware(CorrelationIdMiddleware)
#
#
# @serve.deployment(route_prefix="/", num_replicas=1, ray_actor_options={"resources": {"num_cpus": 1}})
# @serve.ingress(app)
# class EmbeddingServer:
#
#     @app.get("/status/")
#     async def status(self, request: Request, ) -> Response:
#         return await status(request)
#
#     @app.get("/update/")
#     def vectorstore_update(self, request: Request, background_tasks: BackgroundTasks) -> Response:
#         return vectorstore_update(request, background_tasks)
#
#
# @app.on_event("startup")
# def startup():
#     api_startup()
#
#
# @app.on_event("shutdown")
# def shutdown():
#     api_shutdown()
#
#
# serve.run(EmbeddingServer.bind())
#
# r = requests.get("http://localhost:8000/status")
#
# print(f"Result {r.text}")
