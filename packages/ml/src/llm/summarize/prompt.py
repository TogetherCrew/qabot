from langchain.prompts import PromptTemplate

# Convert the schema object to a string
BASE_TEMPLATE = """
[QUESTION]
{question}

[TASK]
{task}

[THOUGHTS]
{thoughts}

[ACTION]
{action}

[RESULT OF ACTION]
{result}

[INSTRUCTION]
Using only [THOUGHTS], [ACTION], and [RESULT OF ACTION] above, please summarize the event.
Only summarize information that is relevant to answering [QUESTION] or completing [TASK].
Include the date, channel and author for the message with the relevant information. Don't include which tool was used.

[SUMMARY]
"""

FINAL_ANSWER_TEMPLATE = """
You are {name}, {role}

You are working on finding an answer to the question in [QUESTION].
You have completed all tasks to get to the answer. Now you need to find a final answer based on the results from the completed tasks in [COMPLETED TASKS].

[QUESTION]
{question}

[COMPLETED TASKS]
{completed_tasks}

[RESULTS OF COMPLETED TASKS]
{results_of_completed_tasks}

[NEXT POSSIBLE TASKS]
{next_possible_tasks}

[INSTRUCTION]
 - Using only the information in [RESULTS OF COMPLETED TASKS] answer the [QUESTION].
 - If possible, include the date, channel and/or author in your answer.
 - If you are not able to fully answer the question and you think that performing [NEXT POSSIBLE TASKS] will lead to a better answer, answer "continue"
 - If it's not possible to find the answer, answer "I don't know" and say why you can't find the answer. If relevant, say what additional information is needed to answer the question.

[FINAL ANSWER]
"""


def get_template() -> PromptTemplate:
    template = BASE_TEMPLATE
    prompt_template = PromptTemplate(
        input_variables=["question" , "task", "thoughts", "action", "result"], template=template
    )
    return prompt_template


def get_final_answer_template() -> PromptTemplate:
    """Use "name", "role", "question", "completed_tasks", "results_of_completed_tasks", "related_knowledge", "related_past_episodes", "next_possible_tasks" """
    template = FINAL_ANSWER_TEMPLATE
    prompt_template = PromptTemplate(
        input_variables=[
            "name",
            "role",
            "question",
            "completed_tasks",
            "results_of_completed_tasks",
            # "related_knowledge",
            # "related_past_episodes",
            "next_possible_tasks",
        ],
        template=template,
    )
    return prompt_template
