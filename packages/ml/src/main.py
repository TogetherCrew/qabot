# first import
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import asyncio


from utils.util import timeit
from utils.constants import DEFAULT_EMBEDDINGS, AGENT_NAME, AGENT_ROLE, AGENT_OBJECTIVE, OPENAI_API_KEY, \
    OPENAI_API_MODEL

# os.environ["LANGCHAIN_HANDLER"] = "langchain"

from tools.discord import ConversationType, DiscordTool
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from ui.cui import CommandlineUserInterface
from agent import Agent
from dotenv import load_dotenv


# first import


# os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
print('loading main.py')
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

    # search_tool = AgentTool(
    #     name="google_search",
    #     func=search.run,
    #     description="""
    #         "With this tool, you can search the web using Google search engine"
    #         "It is a great way to quickly find information on the web.""",
    #     user_permission_required=True,
    # )

    # model_name="sentence-transformers/all-mpnet-base-v2", model_kwargs={'device': 'cpu'})

    # convo_tool_filter = AgentTool(
    #     name="conversations_raw_with_filter",
    #     func=convo_raw,
    #     _args={"query": "<Best query possible to get the desire result>",
    #            "filter": "<Filter by metadata example data {'key': 'value'}>"},
    #     description="With this tool, you can find out history messages happen in diverse channels and threads in Discord. It is a great way to find information. That use similarity embedding search and have capabilities to filter metadata by keys as 'author', 'channel', 'thread' and 'date' only. Note filter its optional and query its required. ONLY use arg filter with known metadata keys",
    #     user_permission_required=True
    # )

    agent = Agent(
        name=AGENT_NAME,
        role=AGENT_ROLE,
        question=AGENT_OBJECTIVE,
        ui=CommandlineUserInterface(),
        llm=llm,
        openaichat=openaichat,
    )
    ## 3. Momoize usage of tools to agent ###
    agent.prodedural_memory.memorize_tools([convo_tool_summary, convo_tool])

    return agent


if __name__ == "__main__":
    print('running __main__')
    asyncio.run(load().run())
