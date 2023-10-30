# flake8: noqa
import json
import time
from langchain.prompts import PromptTemplate
from typing import List
from memory.episodic_memory import Episode
from llm.reason.schema import JsonSchema
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import SystemMessage

# Convert the schema object to a string
JSON_SCHEMA_STR = json.dumps(JsonSchema.schema, indent=4)

BASE_TEMPLATE = """
You are {name}, {role}

You should complete the task defined in [TASK] in order to find an answer to the question in [QUESTION]. 
Your decisions must always be made independently without seeking user assistance or asking for anyone to help. 
Base your actions on the information in [RELATED KNOWLEDGE] and [RELATED PAST EPISODES]. 
Use ONLY your [TOOLS] available to complete your task.

[QUESTION]
{question}

[PERFORMANCE EVALUATION]
1. Review and analyze your actions to ensure you are performing to the best of your abilities.
2. Constructively self-criticize your big-picture behavior constantly.
3. Reflect on past decisions and strategies to refine your approach.
4. Reflect on past episodes to avoid repeating the same mistakes.

[RELATED KNOWLEDGE] 
This reminds you of related knowledge:
{related_knowledge}

[RELATED PAST EPISODES]
This reminds you of related past events:
{related_past_episodes}

[TASK]
You are given the following task:
{task}

[TOOLS USAGE]
You can ONLY USE ONE TOOL at a time and only use tools that are listed below. 
Remember to use the task_complete tool to mark the task as done when you have completed [TASK] or know the answer to [QUESTION].
Format below:
tool name: "tool description", arg1: <arg1>, arg2: <arg2>

[TOOLS]
task_complete: "Use this tool to mark the task as done and include your answer to the task in the 'args' field. If possible, include the date, channel and author in your answer. Certainly use this tool when you know the answer to [QUESTION] or completed the [TASK].", result: <Answer to the assigned task>
{tool_info}
"""



RECENT_EPISODES_TEMPLATE = """
[RECENT EPISODES]
This reminds you of recent events:
"""

SCHEMA_TEMPLATE = f"""
[RULE]
Strictly adhere to [JSON RESPONSE FORMAT] for your response. 
Fill in unique values for each key based on the descriptions in [JSON RESPONSE FORMAT]. 
If you don't know what to fill in for a certain value, just say 'N/A'.  
Any additional text, explanations, or apologies outside of the JSON structure will not be accepted.
Failure to comply with this format will result in an invalid response.

[JSON RESPONSE FORMAT]
{JSON_SCHEMA_STR}

Determine which next [TOOL] to use. 
If the question in [QUESTION] can be answered or the task in [TASK] can be completed with the information in [RELATED KNOWLEDGE] or [RELATED PAST EPISODES], always choose to use the task_complete tool.
Respond using the format specified in [JSON RESPONSE FORMAT]:
""".replace(
    "{", "{{"
).replace(
    "}", "}}"
)

def get_chat_template(
    memory: List[Episode] = None, should_summary=False
) -> ChatPromptTemplate:
    messages = []
    messages.append(SystemMessagePromptTemplate.from_template(BASE_TEMPLATE))

    # If there are past conversation logs, append them
    if len(memory) > 0:
        # insert current time and date
        recent_episodes = RECENT_EPISODES_TEMPLATE
        # recent_episodes += f"The current time and date is {time.strftime('%c')}:\n"

        if should_summary:
            recent_episodes += Episode.get_summary_of_episodes(memory)
        else:
            # insert past conversation logs
            for episode in memory:
                thoughts_str = json.dumps(episode.thoughts)
                action_str = json.dumps(episode.action)
                result = episode.result
                recent_episodes += (
                    thoughts_str + "\n" + action_str + "\n" + result + "\n"
                )

        messages.append(SystemMessage(content=recent_episodes))
    messages.append(SystemMessage(content=SCHEMA_TEMPLATE))

    return ChatPromptTemplate.from_messages(messages)
