class JsonSchema:
    schema = {
        "observation": "observation of [RECENT EPISODES]",
        "thoughts": {
            "task": "description of [YOUR TASK] assigned to you",
            "knowledge": "if there is any helpful knowledge in [RELATED KNOWLEDGE] for the task, summarize the key points here",
            "past_events": "if there is any helpful past events in [RELATED PAST EPISODES] for the task, summarize the key points here",
            # "past_tool_used": "observe in [RELATED PAST EPISODES] what tools with args were already used to avoid re-use them in action",
            "idea": "thought to complete the task",
            "reasoning": "reasoning of the thought",
            "criticism": "constructive self-criticism",
            # "criticism": "constructive self-criticism towards to complete the task",
            "summary": "thoughts summary to say to user, not mention about tools",
        },
        "action": {
            "tool_name": "Only one of the tool names included in [TOOLS] section. Avoid use tool that does not exist in [TOOLS] section",
            "args": {"arg name": "value", "arg name": "value"},
        },
    }
