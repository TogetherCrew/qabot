import inspect
import traceback

import aiohttp
from pydantic import Field, Extra, validator, BaseModel
from typing import Any, Callable, Dict

from logger.hivemind_logger import logger


class AgentToolError(Exception):
    pass


class AgentTool(BaseModel):
    """
    Base class for agent tools.    
    """
    name: str
    description: str = Field(..., description="The description of the tool")
    func: Callable[..., Any] = Field(..., description="The function to execute")
    args: Dict[str, str] = Field(default={})
    user_permission_required: bool = Field(
        False, description="Whether the user permission is required before using this tool")

    class Config:
        extra = Extra.allow

    async def run(self, **kwargs: Any) -> str:
        """Run the tool."""
        result = None
        try:
            #  check if func is corountine
            if inspect.iscoroutinefunction(self.func):
                result = await self.func(**kwargs)
                if result is None:
                    raise Exception("The result from self.func async is None")
            else:
                result = self.func(**kwargs)
        except (BaseException, Exception, KeyboardInterrupt, aiohttp.ClientConnectorError) as e:
            logger.debug(f"Error in run the tool: {e}")
            raise e
        return result

    def get_tool_info(self, include_args=True) -> str:
        """Get the tool info."""
        args_str = ", ".join([f"{k}: <{v}>" for k, v in self.args.items()])

        if include_args:
            return f"""{self.name}: "{self.description}", args: {args_str}"""
        else:
            return f"""{self.name}: "{self.description}"""

    @property
    def args(self) -> Dict:
        """Get the argument name and argument type from the signature"""

        if self.__fields__.get('args', None) is not None:
            return self.__fields__.get('args', None)

        func_signature = inspect.signature(self.func)
        required_args = {}

        for param in func_signature.parameters.values():
            param_name = str(param.name)
            required_args[param_name] = f"<{param_name}>"

        return required_args

    @validator("name") # TODO: maybe I shouldn't modify name here, instead throw to inform how to normalize the variable
    def name_to_snake_case(name: str):
        """Convert the name to snake case."""
        if name is None:
            raise AttributeError("NoneType object has no attribute")

        s = str(name).strip()
        if not s:
            raise IndexError("Empty string")

        # Convert all uppercase letters to lowercase.
        s = s.lower()

        # Replace spaces, dashes, and other separators with underscores.
        s = s.replace(' ', '_')
        s = s.replace('-', '_')

        # Remove all characters that are not alphanumeric or underscore.
        s = ''.join(c for c in s if c.isalnum() or c == '_')

        # Replace multiple consecutive underscores with a single underscore.
        s = '_'.join(filter(None, s.split('_')))

        return s
