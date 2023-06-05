class JsonSchema:
    schema = {
        "observation": "observation of [RECENT EPISODES]",
        "thoughts": {
            "task": "description of [YOUR TASK] assigned to you",
            "knowledge": "if there is any helpful knowledge in [RELATED KNOWLEDGE] for the task, summarize the key points here",
            "past_events": "if there is any helpful past events in [RELATED PAST EPISODES] for the task, summarize the key points here",
            # "past_tool_used": "observe in [RELATED PAST EPISODES] what tools with args were already used to avoid re-use them in action",
            "idea": "thought to complete the task based on available knowledge",
            "reasoning": "reasoning of the thought",
            "criticism": "constructive self-criticism",
            # "criticism": "constructive self-criticism towards to complete the task",
            "summary": "thoughts summary to say to user, don't mention any tools",
        },
        "action": {
            "tool_name": "Only one of the tool names included in [TOOLS] section. Avoid using tools that do not exist in the [TOOLS] section. If the task in [TASK] can be completed with the information in [RELATED KNOWLEDGE] or [RELATED PAST EPISODES], always choose to use the task_complete tool.",
            "args": {"arg name": "value", "arg name": "value"},
        },
    }

