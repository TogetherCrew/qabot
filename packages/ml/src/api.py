import queue
import threading
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from main import agent

import uvicorn

app = FastAPI()

cb = BaseCallbackManager()


class ThreadedGenerator:
    def __init__(self):
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item is StopIteration:
            raise item
        return item

    def send(self, data):
        self.queue.put(data)

    def close(self):
        self.queue.put(StopIteration)


class ChainStreamHandler(StreamingStdOutCallbackHandler):
    def __init__(self, gen):
        super().__init__()
        self.gen = gen

    def on_llm_new_token(self, token: str, **kwargs):
        self.gen.send(token)


def ask_question(g: ThreadedGenerator, question: str):
    agent.run(f"Find the answer for the question if possible: '{question}'", callback=BaseCallbackManager([ChainStreamHandler(g)]))


def chat(prompt):
    g = ThreadedGenerator()
    g.send("#[Thinking]")
    threading.Thread(target=ask_question, args=(g, prompt)).start()
    return g


@app.get("/ask/{question}")
async def ask(question: str):
    return StreamingResponse(ask_question(question))


@app.on_event("startup")
async def startup():
    print("Server Startup!")


def start():
    uvicorn.run("main:app", host="0.0.0.0", port=3333, reload=True)
