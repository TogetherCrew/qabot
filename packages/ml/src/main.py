# first import
import os
import asyncio

# os.environ["LANGCHAIN_HANDLER"] = "langchain"

from tools.discord import ConvoType, DiscordTool
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from ui.cui import CommandlineUserInterface
from agent import Agent
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings


# first import


# Set API Keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
assert OPENAI_API_KEY, "OPENAI_API_KEY environment variable is missing from .env"
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
assert GOOGLE_CSE_ID, "GOOGLE_CSE_ID environment variable is missing from .env"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Set Agent Settings
AGENT_NAME = os.getenv("AGENT_NAME", "")
assert AGENT_NAME, "AGENT_NAME variable is missing from .env"
AGENT_ROLE = os.getenv("AGENT_ROLE", "")
assert AGENT_ROLE, "AGENT_ROLE variable is missing from .env"
AGENT_OBJECTIVE = os.getenv("AGENT_OBJECTIVE", "")
assert AGENT_OBJECTIVE, "AGENT_OBJECTIVE variable is missing from .env"
# AGENT_DIRECTORY = os.getenv("AGENT_DIRECTORY", "")
# assert AGENT_DIRECTORY, "AGENT_DIRECTORY variable is missing from .env"

# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"


def load():
    llm = OpenAI(temperature=0.0, openai_api_key=OPENAI_API_KEY)  # type: ignore
    openaichat = ChatOpenAI(
        temperature=0.0, openai_api_key=OPENAI_API_KEY
    )  # type: ignore # Optional

    ### 1.Create Agent ###
    # dir = AGENT_DIRECTORY

    ### 2. Set up tools for agent ###
    # search = GoogleSearchAPIWrapper()

    # search_tool = AgentTool(
    #     name="google_search",
    #     func=search.run,
    #     description="""
    #         "With this tool, you can search the web using Google search engine"
    #         "It is a great way to quickly find information on the web.""",
    #     user_permission_required=True,
    # )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    # model_name="sentence-transformers/all-mpnet-base-v2", model_kwargs={'device': 'cpu'})

    convo_tool = DiscordTool(
        name="conversations_raw",
        convo_type=ConvoType.RAW,
        embeddings=embeddings,
        args={"query": "<Best query possible to get the desire result>"},
        description="With this tool, you can find out history messages happen in diverse channels and threads in Discord. It is a great way to find information. That use similarity embedding search",
        user_permission_required=False,
    )

    convo_tool_summary = DiscordTool(
        name="conversations_summary",
        convo_type=ConvoType.SUMMARY,
        embeddings=embeddings,
        args={"query": "<Best query possible to get the desire result>"},
        description="With this tool, you can find out summary of messages happen in diverse channels and threads in Discord. It is a great way to find information.",
        user_permission_required=False,
    )

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
        goal=AGENT_OBJECTIVE,
        ui=CommandlineUserInterface(),
        llm=llm,
        openaichat=openaichat,
        # dir=dir
    )
    ## 3. Momoize usage of tools to agent ###
    agent.prodedural_memory.memorize_tools([convo_tool_summary, convo_tool])

    return agent


if __name__ == "__main__":
    asyncio.run(load().run())
