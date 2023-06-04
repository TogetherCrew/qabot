import asyncio
from functools import lru_cache
from typing import Any, AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from langchain.callbacks import AsyncIteratorCallbackHandler
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

from main import load

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def generate_response(question: str) -> AsyncGenerator[Any, None]:
    run: asyncio.Task = None
    try:
        callback_handler = AsyncIteratorCallbackHandler()

        run = asyncio.create_task(get_agent().run(question, callback_handler))
        print("Running")
        async for token in callback_handler.aiter():
            # print("Yielding:", token)
            # yield {"done": "", "value": token}
            yield token + "\n\n"

        print("Done")
        await run
        print("Done2")
    except Exception as e:
        print("Caught Exception:", e)
    except BaseException as e:  # asyncio.CancelledError
        print("Caught BaseException:", e)
    finally:
        if run:
            run.cancel()


async def streamer(gen):
    try:
        async for i in gen:
            yield i
            await asyncio.sleep(0.25)
    except asyncio.CancelledError:
        print("caught cancelled error")


class Ask(BaseModel):
    question: str


@app.post("/ask/")
async def ask(request: Request, body: Ask):
    print("Received question:", body.question)

    return StreamingResponse(streamer(generate_response(body.question)))


@app.on_event("startup")
async def startup():
    print("Server Startup!")
    get_agent()


@lru_cache()
def get_agent():
    return load()


@app.on_event("shutdown")
async def shutdown():
    print("Server Shutdown!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=3333, reload=True)
