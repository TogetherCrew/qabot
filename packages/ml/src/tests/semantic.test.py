from memory.semantic_memory import SemanticMemory


class Test:

    def __init__(self):
        self.semantic_memory = SemanticMemory(llm=self.llm, openaichat=self.openaichat, ui=self.ui)
        self.question = "Some question"
    async def run(self):
        entities = await self.semantic_memory.extract_entity(
                        action_result,
                        question=self.question,
                        task=self.task_manager.get_current_task_string(),
                    )