class JsonSchema:
    schema = {
        "observation": "observation of [RECENT EPISODES]",
        "thoughts": {
            "task": "description of [YOUR TASK] assigned to you",
            "knowledge": "if there is any helpful knowledge in [RELATED KNOWLEDGE] for the task, summarize the key points here",
            "past_events": "if there is any helpful past events in [RELATED PAST EPISODES] for the task, summarize the key points here",
            # "past_tool_used": "observe in [RELATED PAST EPISODES] what tools with args already used to avoid re-use",
            "idea": "thought to complete the task",
            "reasoning": "reasoning of the thought",
            # "criticism": "constructive self-criticism",
            "criticism": "constructive self-criticism towards to complete the task, avoid infinite loops and avoid use tool that does not exist",
            "summary": "thoughts summary to say to user"
        },
        "action": {
            "tool_name": "Only one of the tool names included in [TOOLS] section.",
            "args": {
                "arg name": "value",
                "arg name": "value"
            }
        }
    }
