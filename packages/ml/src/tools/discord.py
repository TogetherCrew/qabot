from enum import Enum

# import inspect
import json
import os
from langchain.vectorstores import DeepLake
from langchain.embeddings.base import Embeddings
from langchain.schema import Document

from tools.base import AgentTool
from utils.constants import DEEPLAKE_RAW_PATH, DEEPLAKE_SUMMARY_PATH
from utils.util import async_post_request


class ConversationType(Enum):
    RAW = "raw"
    SUMMARY = "summary"


# VECSTORE_DIR = os.path.join(os.path.dirname(__file__), "../_vector_store/")


class DiscordTool(AgentTool):
    # create a enum with raw or summary option

    # override constructor

    def __init__(
        self,
        name: str,
        convo_type: ConversationType,
        description: str,
        embeddings: Embeddings,
        user_permission_required: bool = False,
        **kwargs,
    ):
        super().__init__(
            name=name,
            func=self.a_conversation_search_server,
            description=description,
            user_permission_required=user_permission_required,
            **kwargs,
        )

        # self._db = DeepLake(
        #     dataset_path=os.path.join(VECSTORE_DIR, DEEPLAKE_RAW_PATH if convo_type == ConversationType.RAW else DEEPLAKE_SUMMARY_PATH),
        #     read_only=True,
        #     embedding=embeddings,
        # )

    # metadata:{"date": "2023-05-01", "channel": "back_end", "thread": "123", "author": "n", "index": "1"}

    # def convo_raw(self, query: str, filter: Optional[Dict[str, str]]) -> str:
    async def a_conversation_search_server(self, query: str) -> str:
        json_response = await async_post_request('http://localhost:3333/ask', {
                                                    'question': 'Who is Amin?'
                                                })
    def conversation_search(self, query: str) -> str:

        list_doc = self._db.similarity_search(query=query, k=5)

        new_list_doc = [
            Document(
                page_content=doc.page_content.replace("\n", " "), metadata=doc.metadata
            )
            for doc in list_doc
        ]

        # AttributeError: 'dict' object has no attribute 'page_content'
        # how build dict with page_content and metadata attributes

        # print(new_list_doc)

        l = ("\n").join(
            [
                f'message:"{doc.page_content}"\n metadata:{json.dumps(doc.metadata)}'
                for i, doc in enumerate(new_list_doc)
            ]
        )
        # do for each doc getting page content
        return l
