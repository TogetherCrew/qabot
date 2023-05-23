
from typing import List
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

# Convert the schema object to a string
BASE_TEMPLATE = """
[THOUGHTS]
{thoughts}

[ACTION]
{action}

[RESULT OF ACTION]
{result}

[INSTRUCTION]
Using above [THOUGHTS], [ACTION], and [RESULT OF ACTION], please summarize the event.

[SUMMARY]
"""

FINAL_ANSWER_TEMPLATE = """
You are {name}, {role}
You are working on {goal} and have completed all tasks but need find the final answer for the [GOAL].

[GOAL]
{goal}

[COMPLETED TASKS]
{completed_tasks}

[RESULTS OF COMPLETED TASKS]
{results_of_completed_tasks}

[NEXT POSSIBLE TASKS]
{next_possible_tasks}

[RELATED KNOWLEDGE] 
This reminds you of related knowledge:
{related_knowledge}

[RELATED PAST EPISODES]
This reminds you of related past events summarized:
{related_past_episodes}

[INSTRUCTION]
 - Using above [RESULTS OF COMPLETED TASKS], [RELATED KNOWLEDGE], and [RELATED PAST EPISODES], answer the [GOAL].
 - If not possible find the answer, return just: 'I don't know'.
 - If you think answering the [NEXT POSSIBLE TASKS] could definitely help you find the answer, return just: 'I don't know'. 

[FINAL ANSWER]
"""


def get_template() -> PromptTemplate:
    template = BASE_TEMPLATE
    prompt_template = PromptTemplate(
        input_variables=["thoughts", "action", "result"], template=template)
    return prompt_template


def get_final_answer_template() -> PromptTemplate:
    """ Use "name", "role", "goal", "completed_tasks", "results_of_completed_tasks", "related_knowledge", "related_past_episodes", "next_possible_tasks" """
    template = FINAL_ANSWER_TEMPLATE
    prompt_template = PromptTemplate(
        input_variables=["name", "role", "goal", "completed_tasks", "results_of_completed_tasks", "related_knowledge", "related_past_episodes","next_possible_tasks"], template=template)
    return prompt_template


# def get_chat_templatez() -> ChatPromptTemplate:
#     messages = []
#     messages.append(SystemMessagePromptTemplate.from_template(BASE_TEMPLATE))
#     return ChatPromptTemplate.from_messages(messages)
