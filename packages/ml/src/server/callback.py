from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Dict, List, Literal, Union, cast

from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult
from pydantic import BaseModel


# TODO If used by two LLM runs in parallel this won't work as expected


class ResponseChunkBase(BaseModel):
    pass


class TextChunk(ResponseChunkBase):
    token: str


class InfoChunk(ResponseChunkBase):
    count_tokens: int
    model_name: str | None = None


class AsyncChunkIteratorCallbackHandler(AsyncCallbackHandler):
    """Callback handler that returns an async iterator."""

    queue: asyncio.Queue[ResponseChunkBase]

    done: asyncio.Event

    @property
    def always_verbose(self) -> bool:
        return True

    def __init__(self) -> None:
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()

    async def on_llm_start(
            self, serialized: Dict[ResponseChunkBase, Any], prompts: List[ResponseChunkBase], **kwargs: Any
    ) -> None:
        # If two calls are made in a row, this resets the state
        self.done.clear()

    async def on_llm_new_token(self, token: ResponseChunkBase, **kwargs: Any) -> None:
        self.queue.put_nowait(token)

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.done.set()

    async def on_llm_error(
            self, error: BaseException | KeyboardInterrupt, **kwargs: Any
    ) -> None:
        self.done.set()

    # TODO implement the other methods

    async def aiter(self) -> AsyncIterator[ResponseChunkBase]:
        while not self.queue.empty() or not self.done.is_set():
            # Wait for the next token in the queue,
            # but stop waiting if the done event is set
            done, other = await asyncio.wait(
                [
                    # NOTE: If you add other tasks here, update the code below,
                    # which assumes each set has exactly one task each
                    asyncio.ensure_future(self.queue.get()),
                    asyncio.ensure_future(self.done.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel the other task
            if other:
                other.pop().cancel()

            # Extract the value of the first completed task
            token_or_done = cast(Union[ResponseChunkBase, Literal[True]], done.pop().result())

            # If the extracted value is the boolean True, the done event was set
            if token_or_done is True:
                break

            # Otherwise, the extracted value is a token, which we yield
            yield token_or_done
