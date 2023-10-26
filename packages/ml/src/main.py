import os

from logger.hivemind_logger import logger

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import asyncio

from utils.util import timeit
from utils.constants import AGENT_NAME, AGENT_ROLE, AGENT_OBJECTIVE, OPENAI_API_KEY, \
    OPENAI_API_MODEL

from tools.discord import ConversationType, DiscordTool
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from ui.cui import CommandlineUserInterface
from agent import Agent

convo_tool = DiscordTool(
    name="conversations_raw",
    convo_type=ConversationType.RAW,
    args={"query": "<Best query possible to get the desired result>"},
    description="With this tool, you can search all messages from the different channels and threads in the Discord server. Use this tool to find precise information using a similarity embedding search",
    user_permission_required=False,
)

convo_tool_summary = DiscordTool(
    name="conversations_summary",
    convo_type=ConversationType.SUMMARY,
    args={"query": "<Best query possible to get the desired result>"},
    description="With this tool, you can search daily summaries per thread and per channel of messages in the Discord server. Use this tool to find general information about conversations using similarity embedding search.",
    user_permission_required=False,
)

llm = OpenAI(temperature=0.0, openai_api_key=OPENAI_API_KEY)  # type: ignore
openaichat = ChatOpenAI(
    temperature=0.0, openai_api_key=OPENAI_API_KEY, model=OPENAI_API_MODEL
)  # type: ignore # Optional


@timeit
def load():
    agent = Agent(
        name=AGENT_NAME,
        role=AGENT_ROLE,
        question=AGENT_OBJECTIVE,
        ui=CommandlineUserInterface(),
        llm=llm,
        openaichat=openaichat,
    )

    agent.prodedural_memory.memorize_tools([convo_tool_summary, convo_tool])

    return agent


if __name__ == "__main__":
    logger.debug('running __main__')
    asyncio.run(load().run())
