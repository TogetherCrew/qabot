from enum import Enum
import inspect
import json
from langchain.vectorstores import DeepLake
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from pydantic import Field, Extra, validator, BaseModel
from typing import Any, Callable, Dict, Optional

from tools.base import AgentTool


class ConvoType(Enum):
    RAW = "raw"
    SUMMARY = "summary"


VECSTORE_DIR = "vector_store/"


class DiscordTool(AgentTool):

    # create a enum with raw or summary option

    # override constructor

    def __init__(self, name: str, convo_type: ConvoType, description: str, embeddings: Embeddings, user_permission_required: bool = False, **kwargs):
        super().__init__(name=name, func=self.convo_raw, description=description,
                         user_permission_required=user_permission_required, **kwargs)

        if convo_type == ConvoType.RAW:
            self._db = DeepLake(dataset_path=f"{VECSTORE_DIR}DeepLake_VectorStore_413_419_raw_messages_HF",
                                read_only=True, embedding_function=embeddings)
        elif convo_type == ConvoType.SUMMARY:
            self._db = DeepLake(dataset_path=f"{VECSTORE_DIR}DeepLake_VectorStore_413_419_summaries_HF",
                                read_only=True, embedding_function=embeddings)

    # metadata:{"date": "2023-05-01", "channel": "back_end", "thread": "123", "author": "n", "index": "1"}

    # def convo_raw(self, query: str, filter: Optional[Dict[str, str]]) -> str:
    def convo_raw(self, query: str) -> str:
        list_doc = self._db.similarity_search(query=query, k=5)

        new_list_doc = [Document(page_content=doc.page_content.replace(
            "\n", " "), metadata=doc.metadata) for doc in list_doc]

        # AttributeError: 'dict' object has no attribute 'page_content'
        # how build dict with page_content and metadata attributes

        # print(new_list_doc)

        l = ("\n").join(
            [f"message:\"{doc.page_content}\"\n metadata:{json.dumps(doc.metadata)}" for i, doc in enumerate(new_list_doc)])
        # do for each doc getting page content
        return l
