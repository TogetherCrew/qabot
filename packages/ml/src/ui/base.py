from pydantic import BaseModel, Extra
from abc import abstractmethod
from typing import ContextManager, Union

from langchain.callbacks import AsyncIteratorCallbackHandler


class BaseHumanUserInterface(BaseModel):
    """Base class for human user interface."""

    callback: Union[AsyncIteratorCallbackHandler, None] = None

    class Config:
        extra = Extra.forbid
        arbitrary_types_allowed = True

    @abstractmethod
    def get_user_input(self) -> str:
        # waiting for user input
        pass

    @abstractmethod
    def get_binary_user_input(self, message: str) -> bool:
        # get user permission
        pass

    @abstractmethod
    async def notify(self, title: str, message: str):
        # notify user
        pass

    @abstractmethod
    async def loading(self) -> ContextManager:
        # waiting for AI to respond
        pass
