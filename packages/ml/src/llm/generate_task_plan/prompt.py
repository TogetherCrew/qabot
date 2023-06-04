from langchain.prompts import PromptTemplate

SUBQUESTIONS_TEMPLATE = """
You are {name}, an {role}.

To achieve this goal effectively, you should consider generating subquestions that will help break down the main question into smaller, more manageable parts.
These subquestions might involve understanding the context and the specific details related to goal question.

[TOOLS]
{tool_info}

[GOAL]
{goal}

Based on this goal, generate subquestions that will help you create a more detailed understanding of the situation and guide your future actions. 

Now, based on the goal, generate your own subquestions. Remember, these should help you break down the main question into smaller, more manageable parts.

[SUBQUESTIONS]
Return your subquestions as a list of strings.
- Max 2 best subsquestions
- Enclose each subquestion in double quotation marks.
- Separate subquestions with commas.
- Use [] only at the beginning and end.

["Subquestion 1","Subquestion 2", ...]

[RESPONSE]"
"""

# Convert the schema object to a string

BASE_TEMPLATE = """
You are {name}, {role}
You should create new tasks that can help archieve the [GOAL]

[GOAL]
{goal}

[TOOLS]
{tool_info}

[SUBQUESTIONS]
Those subquestions derived from the goal can help you create efficient tasks:
{subquestions_list}

[YOUR MISSION]
Based on the [GOAL] and [TOOLS], create new tasks to be completed by the AI system that do not overlap with incomplete tasks.
- Tasks should be calculated backward from the GOAL, and effective arrangements should be made.
- Take in considerations the available [TOOLS] and [SUBQUESTIONS] to create tasks that can be completed by the AI system.

[RESPONSE FORMAT]
Return the tasks as a list of string.
- Max 3 best tasks
- Enclose each task in double quotation marks.
- Separate tasks with Tabs.
- Use [] only at the beginning and end

["Task 1 that the AI assistant should perform"\t"Task 2 that the AI assistant should perform",\t ...]

[RESPONSE]
"""


def get_template() -> PromptTemplate:
    template = BASE_TEMPLATE
    PROMPT = PromptTemplate(
        input_variables=["name", "role", "goal", "subquestions_list", "tool_info"],
        template=template,
    )
    return PROMPT


def get_subquestions_template() -> PromptTemplate:
    template = SUBQUESTIONS_TEMPLATE
    PROMPT = PromptTemplate(
        input_variables=["name", "role", "goal", "tool_info"], template=template
    )
    return PROMPT


# def get_chat_template() -> ChatPromptTemplate:
#     messages = []
#     messages.append(SystemMessagePromptTemplate.from_template(BASE_TEMPLATE))
#     return ChatPromptTemplate.from_messages(messages)
