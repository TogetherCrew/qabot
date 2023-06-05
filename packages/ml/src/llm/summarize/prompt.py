from langchain.prompts import PromptTemplate

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

You are working on finding an answer to the question in [QUESTION].
You have completed all tasks to get to the answer. Now you need to find a final answer based on the results from the completed tasks in [COMPLETED TASKS].

[QUESTION]
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
 - Using above [RESULTS OF COMPLETED TASKS], [RELATED KNOWLEDGE], and [RELATED PAST EPISODES], answer the [QUESTION].
 - If you are not able to fully answer the question and you think that performing [NEXT POSSIBLE TASKS] will lead to a better answer, answer "continue"
 - If it's not possible to find the answer, answer "I don't know"

[FINAL ANSWER]
"""


def get_template() -> PromptTemplate:
    template = BASE_TEMPLATE
    prompt_template = PromptTemplate(
        input_variables=["thoughts", "action", "result"], template=template
    )
    return prompt_template


def get_final_answer_template() -> PromptTemplate:
    """Use "name", "role", "goal", "completed_tasks", "results_of_completed_tasks", "related_knowledge", "related_past_episodes", "next_possible_tasks" """
    template = FINAL_ANSWER_TEMPLATE
    prompt_template = PromptTemplate(
        input_variables=[
            "name",
            "role",
            "goal",
            "completed_tasks",
            "results_of_completed_tasks",
            "related_knowledge",
            "related_past_episodes",
            "next_possible_tasks",
        ],
        template=template,
    )
    return prompt_template


# def get_chat_templatez() -> ChatPromptTemplate:
#     messages = []
#     messages.append(SystemMessagePromptTemplate.from_template(BASE_TEMPLATE))
#     return ChatPromptTemplate.from_messages(messages)
