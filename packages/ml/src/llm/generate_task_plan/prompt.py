from langchain.prompts import PromptTemplate

SUBQUESTIONS_TEMPLATE = """
You are {name}, {role}.

You are answering the question [QUESTION] and you have the tools [TOOLS] to your availability to find the answer. 
To answer this question effectively, you should consider generating subquestions that will help break down the main question into smaller, more manageable parts.
These subquestions might involve understanding the context and the specific details related to the main question. 
Only create subquestions for complex main questions. Otherwise don't generate any subquestions.

[QUESTION]
{question}

[TOOLS]
{tool_info}

Based on this [QUESTION], generate subquestions that will help you create a more detailed understanding of the situation and guide your future actions.
 
[RESPONSE FORMAT]
Return your subquestions as a list of strings.
- Max 3 best subquestions
- Enclose each subquestion in double quotation marks.
- Separate subquestions with commas.
- Use [] only at the beginning and end.
- Return an empty list if no subquestions were generated
 
["Subquestion 1","Subquestion 2", ...]

Now, based on the main question [QUESTION], generate your own subquestions using [RESPONSE FORMAT]. 
Remember, only generate subquestions if necessary.
Subquestions should help you break down the main question into smaller, more manageable parts.

[RESPONSE] 
"""

# Convert the schema object to a string

BASE_TEMPLATE = """
You are {name}, {role}

You should create one or several new tasks that can help answer the main question [QUESTION]. 

[QUESTION]
{question}

[YOUR MISSION]
Based on the [QUESTION], create tasks following these rules: 
- Tasks should be defined to lead to a final answer to [QUESTION] and can be the same as [QUESTION].
- Tasks should be ordered so that tasks that depend on the output of other tasks are only listed later. 
- Tasks should specify what information needs to be collected, not how it needs to be done.

[RESPONSE FORMAT]
Return the tasks as a list of strings.
- Max 3 best tasks but ideally only 1 task. 
- Define tasks in a way that requires solving as little tasks as possible in order to find a final answer to [QUESTION].
- Enclose each task in double quotation marks.
- Separate tasks with Tabs.
- Use [] only at the beginning and end.

["Task 1 that the AI assistant should perform"\t"Task 2 that the AI assistant should perform",\t ...]

Now, based on the main question [QUESTION], generate the tasks that should be completed to answer the main question.

[RESPONSE]
"""


def get_template() -> PromptTemplate:
    template = BASE_TEMPLATE
    PROMPT = PromptTemplate(
        input_variables=["name", "role", "question"],
        template=template,
    )
    return PROMPT


def get_subquestions_template() -> PromptTemplate:
    template = SUBQUESTIONS_TEMPLATE
    PROMPT = PromptTemplate(
        input_variables=["name", "role", "question", "tool_info"], template=template
    )
    return PROMPT

