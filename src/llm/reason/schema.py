class JsonSchema:
    schema = {
        "observation": "observation of [RECENT EPISODES]",
        "thoughts": {
            "task": "description of [YOUR TASK] assigned to you",
            "knowledge": "if there is any helpful knowledge in [RELATED KNOWLEDGE] for the task, summarize the key points here",
            "past_events": "if there is any helpful past events in [RELATED PAST EPISODES] for the task, summarize the key points here",
            "idea": "thought to complete the task",
            "reasoning": "reasoning of the thought",
            "criticism": "constructive self-criticism",
            # "criticism": "constructive self-criticism towards to complete the task and avoid infinite loops",
            "summary": "thoughts summary to say to user"
        },
        "action": {
            "tool_name": "One of the tool names included in [TOOLS]",
            "args": {
                "arg name": "value",
                "arg name": "value"
            }
        }
    }
