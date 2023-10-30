class JsonSchema:
    schema = {
        "observation": "Observation of [RELATED PAST EPISODES]",
        "thoughts": {
            "task": "Make a description of the question under [QUESTION] and the related task assigned to you under [TASK]",
            "knowledge": "If there is any helpful information related to task in [RELATED KNOWLEDGE], summarize the key points here in one sentence. Otherwise respond 'N/A'",
            "past_events": "If there is any helpful information related to task in [RELATED PAST EPISODES], summarize the key points here. Otherwise respond 'N/A'",
            "reasoning": "Reasoning about the action to complete the task based on information in knowledge and past_events and using one of the tools in [TOOLS]. If the task can be completed, always use the task_complete tool. Don't ever answer questions based on prior knowledge only",
            "idea": "Idea for an action using one of the tools in [TOOLS] to complete the task based on information in knowledge and past_events. If the task can be completed, always use the task_complete tool.",
            "criticism": "If the task can be completed based on the previously gathered information summarized under knowledge and past_events, respond 'The task_complete tool must be used. This decision overrides reasoning and idea'. Otherwise respond 'N/A'",
            "summary": "Summary of the reasoning, action idea and criticism for the task based on knowledge and past_events",
        },
        "action": {
            "tool_name": "Only one of the tool names included in [TOOLS] section. Never come up with tools that do not exist in the [TOOLS] section. If the task in [TASK] can be completed with the information in [RELATED KNOWLEDGE] or [RELATED PAST EPISODES], always choose to use the task_complete tool and provide the date, channel and author in your answer.",
            "args": {"arg name": "value", "arg name": "value"},
        },
    }

