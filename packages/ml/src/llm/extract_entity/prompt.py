import json
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from llm.extract_entity.schema import JsonSchema
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)

# Convert the schema object to a string
JSON_SCHEMA_STR = json.dumps(JsonSchema.schema)

ENTITY_EXTRACTION_TEMPLATE = """
You are an AI assistant for extracting entities from a text [INPUT TEXT].
You are extracting information to complete task [TASK] in order to answer the question [QUESTION]. 
Extract ONLY proper nouns from [INPUT TEXT] that help complete the task [TASK] and return them as a JSON object following [JSON RESPONSE FORMAT]. 

[QUESTION]:
Where are the twitter crawler files stored?

[TASK]:
Find the location of the Twitter Crawler files

[INPUT TEXT]:
{text}

"""

SCHEMA_TEMPLATE = f"""
    [RULE]
    Your response must be provided exclusively in the JSON format outlined below, without any exceptions.
    Any additional text, explanations, or apologies outside of the JSON structure will not be accepted.
    Please ensure the response adheres to the specified format and can be successfully parsed by Python's json.loads function.

    Strictly adhere to the [JSON RESPONSE FORMAT] for your response.
    Failure to comply with this format will result in an invalid response.
    Please ensure your output strictly follows [JSON RESPONSE FORMAT].

    [JSON RESPONSE FORMAT]
    {JSON_SCHEMA_STR}

    [RESPONSE]""".replace("{", "{{").replace("}", "}}")


def get_template() -> PromptTemplate:
    template = f"{ENTITY_EXTRACTION_TEMPLATE}\n{SCHEMA_TEMPLATE}"
    return PromptTemplate(input_variables=["text"], template=template)


def get_chat_template() -> ChatPromptTemplate:
    messages = []
    messages.append(SystemMessagePromptTemplate.from_template(
        ENTITY_EXTRACTION_TEMPLATE))
    messages.append(SystemMessagePromptTemplate.from_template(SCHEMA_TEMPLATE))
    return ChatPromptTemplate.from_messages(messages)
