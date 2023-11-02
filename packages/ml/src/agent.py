import os
import json
import traceback

import aiofiles
import tiktoken
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from llm.summarize.prompt import get_final_answer_template
from logger.hivemind_logger import logger
from memory.procedual_memory import ProcedualMemory, ToolNotFoundException
from memory.episodic_memory import EpisodicMemory, Episode
from memory.semantic_memory import SemanticMemory
from manager.serializer_manager import SerializationManager
from utils.constants import DEFAULT_AGENT_DIR, BASE_PATH_SERIALIZATION
from utils.util import atimeit
from ui.cui import CommandlineUserInterface
import llm.reason.prompt as ReasonPrompt
from manager.task_manager import TaskManager
from llm.json_output_parser import FixJsonException, LLMJsonOutputParser
from llm.reason.schema import JsonSchema as ReasonSchema
from langchain.llms.base import BaseLLM
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI

from server.callback import AsyncChunkIteratorCallbackHandler

# Define the schema for the llm output
REASON_JSON_SCHEMA_STR = json.dumps(ReasonSchema.schema)


class Agent(BaseModel):
    """
    This is the main class for the Agent. It is responsible for managing the tools and the agent.
    """

    # Define the tools
    dir: Optional[str] = Field(
        DEFAULT_AGENT_DIR,
        description="The folder path to the directory where the agent data is stored and saved",
    )
    name: str = Field(..., description="The name of the agent")
    role: str = Field(..., description="The role of the agent")
    question: Optional[str] = Field(..., description="The question of the agent")
    ui: CommandlineUserInterface = Field(
        CommandlineUserInterface(), description="The user interface for the agent"
    )
    llm: BaseLLM = Field(..., description="llm class for the agent")
    openaichat: Optional[ChatOpenAI] = Field(
        None, description="ChatOpenAI class for the agent"
    )
    prodedural_memory: Optional[ProcedualMemory] = Field(
        ProcedualMemory(), description="The procedural memory about tools agent uses"
    )
    episodic_memory: Optional[EpisodicMemory] = Field(
        None, description="The short term memory of the agent"
    )
    semantic_memory: Optional[SemanticMemory] = Field(
        None, description="The long term memory of the agent"
    )
    task_manager: TaskManager = Field(
        None, description="The task manager for the agent"
    )

    sm: SerializationManager = Field(
        SerializationManager(base_path=BASE_PATH_SERIALIZATION),
        description="The serialization manager for the agent",
    )

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

        self.task_manager = TaskManager(llm=self.llm)

        self.episodic_memory = EpisodicMemory(llm=self.llm, ui=self.ui)
        self.semantic_memory = SemanticMemory(llm=self.llm, openaichat=self.openaichat, ui=self.ui)

        self._get_absolute_path()
        self._create_dir_if_not_exists()

    def __del__(self):
        del self.task_manager
        del self.episodic_memory
        del self.semantic_memory

    def _get_absolute_path(self):
        return os.path.abspath(self.dir)

    def _create_dir_if_not_exists(self) -> None:
        absolute_path = self._get_absolute_path()
        if not os.path.exists(absolute_path):
            os.makedirs(absolute_path)

    @atimeit
    async def run(
            self,
            question: str | None = None,
            callback: AsyncChunkIteratorCallbackHandler | None = None,
    ):

        """
        This method runs the agent.
        """
        if question is not None:
            self.question = question
        if self.question is None:
            await self.ui.notify("ERROR", "Question is not set.")
            return
        if callback is not None:
            self.ui.callback = callback

        try:

            tm = self.sm.load_and_deserialize(f"task_manager::{self.question}")
            if tm is not None:
                # self.ui.notify("INFO", "Task Manager loaded.")
                print("INFO", "Task Manager loaded.")
                self.task_manager = tm
            else:
                # self.ui.notify("INFO", "Task Manager not loaded.")
                print("INFO", "Task Manager not loaded.")

            tool_info = self.prodedural_memory.tools_to_prompt(
                self.prodedural_memory.remember_all_tools()
            )

            if len(self.task_manager.tasks) == 0:
                await self.ui.notify(stream=True, message="Generating subtasks...")

                await self.task_manager.generate_task_plan(
                    name=self.name,
                    role=self.role,
                    question=self.question,
                    tool_info=tool_info,
                )

                await self.sm.serialize_and_save(self.task_manager, f"task_manager::{self.question}")

            await self.ui.notify(
                title="ALL TASKS",
                message=self.task_manager.get_incomplete_tasks_string(),
                title_color="BLUE",
            )

            while True:
                current_task = self.task_manager.get_current_task_string()
                if current_task:
                    await self.ui.notify(
                        title="CURRENT TASK", message=current_task, title_color="BLUE"
                    )
                else:
                    await self.ui.notify(
                        title="FINISH",
                        message=f"All tasks are completed. {self.name} will end the operation.",
                        title_color="RED",
                    )

                    await self.ui.notify(message="Final answer...")
                    await self._final_answer()
                    break

                # ReAct: Reasoning
                await self.ui.notify(message="Thinking...")
                should_try_complete = False
                should_summary = True
                keep_it = True
                tool_name = None
                while keep_it:
                    keep_it = False
                    reasoning_result: Dict[str, Any] | str | None = None
                    try:
                        reasoning_result = await self._reason(
                            should_try_complete=should_try_complete,
                            should_summary=should_summary
                        )  # type: ignore
                        thoughts = reasoning_result["thoughts"]  # type: ignore
                        action = reasoning_result["action"]  # type: ignore
                        tool_name = action["tool_name"]  # type: ignore
                        args = action["args"]  # type: ignore

                        def empty_for_non_existing_key(key: str, default: Any = "") -> Any:
                            if key not in thoughts:
                                logger.warning(f"Key {key} not found in 'thoughts'")
                                return default
                            return thoughts[key]

                        thoughts["criticism"] = empty_for_non_existing_key("criticism")
                        thoughts["summary"] = empty_for_non_existing_key("summary")


                        # if tool_name != 'task_complete':
                        #     tool_name = "conversations_raw"
                        #     args = {'query':'Amin'}
                        await self.ui.notify(title="TASK", message=thoughts["task"])  # type: ignore
                        await self.ui.notify(
                            title="OBSERVATION", message=reasoning_result["observation"]  # type: ignore
                        )
                        await self.ui.notify(title="IDEA", message=thoughts["idea"])  # type: ignore
                        await self.ui.notify(
                            title="REASONING", message=thoughts["reasoning"]  # type: ignore
                        )
                        await self.ui.notify(
                            title="CRITICISM", message=thoughts["criticism"]  # type: ignore
                        )
                        await self.ui.notify(title="THOUGHT", message=thoughts["summary"])  # type: ignore
                        await self.ui.notify(title="NEXT ACTION", message=action)
                    except BaseException as e:
                        await self.ui.notify(
                            title="REASONING ERROR",
                            message=str(reasoning_result),
                            title_color="RED",
                        )
                        await self.ui.notify(
                            title="ERROR",
                            message=e.__dict__.__str__(),
                            title_color="RED",
                        )
                        print(traceback.format_exc())

                        raise e

                    # check if the tool_name and args already was used in the past in that task.
                    # if so, skip the action.
                    if self.task_manager.is_action_already_used_in_current_task(
                            tool_name, args
                    ):  # TODO FIX: should be a list of args instead of the last one
                        await self.ui.notify(
                            title="SKIP ACTION",
                            title_color="RED",
                            message=f"{tool_name} {args} is already used in the current task. Try complete the task!",
                        )
                        should_try_complete = True
                        keep_it = True
                    else:
                        await self.ui.notify(
                            title="Tool first time used?", title_color="RED", message="Continue"
                        )

                    if tool_name == "task_complete":
                        await self.ui.notify(
                            title="BREAK?",
                            title_color="RED",
                            message="Task is completed.",
                        )
                        await self.ui.notify(
                            stream=True,
                            message=f"Completed subtask {self.task_manager.current_task_id}",
                        )
                        break
                    if tool_name == "discard_task":
                        await self.ui.notify(
                            title="BREAK?",
                            title_color="RED",
                            message="Discard Task.",
                        )
                        self.task_manager.discard_current_task()
                        break

                # Task Complete
                if tool_name == "task_complete":
                    action_result = args["result"]  # todo: check if result is correct
                    # todo: check if list of TASK need be updated
                    await self._task_complete(action_result)

                    # run final prompt here

                    await self.ui.notify(message="Try final answer...")
                    result = await self._final_answer()

                    # save agent data
                    # await self.ui.notify(message="Save agent data...")
                    # await self.save_agent()

                    # trim result
                    if result and result.strip() != "I don't know.":
                        await self.ui.notify(title="END", message="")
                        await self.ui.call_callback_end()
                        break

                # Action with tools
                else:
                    tool = None
                    try:
                        tool = self.prodedural_memory.remember_tool_by_name(tool_name)

                        if not tool:
                            raise Exception(
                                f"Tool {tool_name} is not found in the procedural memory."
                            )

                        async def act(_tool_name, _args):
                            try:
                                act_result = await self._act(_tool_name, _args)
                                if act_result is None:
                                    raise Exception("The result is None")
                            except BaseException as e_act:
                                raise e_act
                            await self.ui.notify(
                                title="ACTION RESULT", message=act_result
                            )
                            return act_result

                        await self.ui.notify(
                            title="LOG",
                            message=f"Tool: {tool_name} user_permission_required:{tool.user_permission_required}",
                        )
                        if tool.user_permission_required:
                            # Ask for permission to run the action
                            user_permission = self.ui.get_binary_user_input(
                                "Do you want to continue?"
                            )
                            if not user_permission:
                                action_result = "User Denied to run Action"
                                await self.ui.notify(
                                    title="USER INPUT", message=action_result
                                )
                            else:
                                action_result = await act(tool_name, args)
                        else:
                            action_result = await act(tool_name, args)
                    except ToolNotFoundException:
                        await self.ui.notify(
                            title="LOG",
                            message=f"Tool {tool_name} not exist. Pick one tool [TOOL] from the list.",
                        )
                        action_result = f"Tool {tool_name} not exist. Pick one tool [TOOL] from the list."

                episode = Episode(
                    question=self.question, task=self.task_manager.get_current_task_string(),
                    thoughts=thoughts, action=action, result=action_result
                )  # type: ignore

                summary = await self.episodic_memory.summarize_and_memorize_episode(episode)
                await self.ui.notify(
                    title="MEMORIZE NEW EPISODE", message=summary, title_color="blue"
                )

                entities = await self.semantic_memory.extract_entity(
                    action_result,
                    question=self.question,
                    task=self.task_manager.get_current_task_string(),
                )
                await self.ui.notify(
                    title="MEMORIZE NEW KNOWLEDGE",
                    message=entities.__str__(),
                    title_color="blue",
                )
        except BaseException as e_run:
            full_trace = traceback.format_exc()
            logger.error(f"An exception occurred. Traceback:\n{full_trace}")
            if callback:
                await self.ui.call_callback_error(e_run)
            raise e_run

    async def _final_answer(self) -> str:
        final_prompt = get_final_answer_template()

        completed_tasks = self.task_manager.get_completed_tasks()
        all_related_knowledge = dict()
        for task in completed_tasks:
            related_knowledge = self.semantic_memory.remember_related_knowledge(
                task.description, k=5
            )
            all_related_knowledge.update(related_knowledge)

        all_related_past_episodes = ""
        for task in completed_tasks:
            related_past_episodes = self.episodic_memory.remember_related_episodes(
                task.description, k=2
            )
            summary_of_related_past_episodes = ("\n").join(
                [past.summary for past in related_past_episodes]
            )
            all_related_past_episodes += f"\n{summary_of_related_past_episodes}"

        input_variables = {
            "name": self.name,
            "role": self.role,
            "question": self.question,
            "completed_tasks": self.task_manager.get_completed_tasks_as_string(),
            "results_of_completed_tasks": self.task_manager.get_results_completed_tasks_as_string(),
            # "related_knowledge": all_related_knowledge,
            # "related_past_episodes": all_related_past_episodes,
            "next_possible_tasks": self.task_manager.get_incomplete_tasks_string(),
        }

        final_prompt_formatted = final_prompt.format_prompt(**input_variables)
        # await self.ui.notify(
        #     title="FINAL PROMPT", message=final_prompt_formatted.to_string()
        # )

        llm_chain = LLMChain(prompt=final_prompt, llm=self.llm)
        try:
            # result = await llm_chain.apredict(**input_variables)
            llm_result = await llm_chain.agenerate([input_variables])

            #  llm_result = await self.openaichat._agenerate(
            #         messages=prompt_msg
            #     )

            result = llm_result.generations[0][0].text

            await self.ui.call_callback_info_llm_result(llm_result)
        except BaseException as e:
            raise Exception(f"Error: {e}")

        # # measure the time since start of function and print it
        # end = time.time()
        # # format it in hours, minutes, seconds
        # total_time = time.strftime("%H:%M:%S", time.gmtime(end - self.start_time))
        # await self.ui.notify(
        #     title="FINAL ANSWER TIME",
        #     message=f"Time to get final answer: {total_time}",
        # )
        if result:
            await self.ui.notify(stream=True, title="Final Answer", message=result, title_color="RED")  # type: ignore
        return result

    async def _reason(self, should_try_complete=False, should_summary=False):
        keep_it = True
        while keep_it:
            keep_it = False
            current_task_description = self.task_manager.get_current_task_string()

            # Retrie task related memories
            await self.ui.notify(message="Retrieving memory...")
            # Retrieve memories related to the task.
            related_past_episodes = self.episodic_memory.remember_related_episodes(
                current_task_description, k=2
            )

            # Get the recent episodes
            memory = self.episodic_memory.remember_recent_episodes(2)

            # remove from memory the episodes equals in the related_past_episodes
            memory = [m for m in memory if m not in related_past_episodes]

            if len(related_past_episodes) > 0:
                await self.ui.notify(
                    title="TASK RELATED EPISODE", message=str(related_past_episodes)
                )

                if should_summary:
                    summary_of_related_past_episodes = Episode.get_summary_of_episodes(
                        related_past_episodes
                    )
                    await self.ui.notify(
                        title="SUMMARY OF TASK RELATED EPISODES",
                        message=summary_of_related_past_episodes,
                    )
                    related_past_episodes = summary_of_related_past_episodes

            # Retrieve concepts related to the task.
            related_knowledge = self.semantic_memory.remember_related_knowledge(
                current_task_description, k=5
            )
            if len(related_knowledge) > 0:
                await self.ui.notify(
                    title="TASK RELATED KNOWLEDGE", message=related_knowledge.__str__()
                )

            tool_info = "\n You should use task_complete to complete the task now."
            if not should_try_complete:
                # Get the relevant tools
                # If agent has to much tools, use "remember_relevant_tools"
                # because too many tool information will cause context windows overflow.
                tools = self.prodedural_memory.remember_all_tools()

                # Set up the prompt
                tool_info = self.prodedural_memory.tools_to_prompt(tools)

            # If OpenAI Chat is available, it is used for higher accuracy results.
            if self.openaichat:
                await self.ui.notify(stream=True, message="Reasoning...")
                prompt = ReasonPrompt.get_chat_template(
                    memory=memory, should_summary=should_summary
                ).format_prompt(
                    name=self.name,
                    role=self.role,
                    question=self.question,
                    related_past_episodes=related_past_episodes,
                    related_knowledge=related_knowledge,
                    task=current_task_description,
                    tool_info=tool_info,
                )
                prompt_msg = prompt.to_messages()

                full_prompt = " ".join([msg.content for msg in prompt_msg])

                # await self.ui.notify(title="REASONING PROMPT", message=full_prompt)
                try:
                    enc = tiktoken.encoding_for_model(self.openaichat.model_name)
                    token_count = len(enc.encode(full_prompt))
                    print("token_count", token_count)
                    if token_count > 4096:
                        await self.ui.notify(
                            title="TOKEN EXCEEDS",
                            title_color="red",
                            message=f"Token count {token_count} exceeds 4096. Trying again with summary.",
                        )
                        # result = self._reason(should_try_complete=should_try_complete, should_summary=True)
                        should_summary = True
                        keep_it = True
                        continue
                    else:
                        llm_result = await self.openaichat._agenerate(
                            messages=prompt_msg
                        )
                        await self.ui.call_callback_info_llm_result(llm_result)

                        # await self.ui.notify(
                        #     title="LLM RESULT",
                        #     message=llm_result.generations[0].message.content,
                        # )
                        result = llm_result.generations[0].message.content
                    # openai.error.InvalidRequestError: This model's maximum context length is 4097 tokens. However,
                    # your messages resulted in 4879 tokens. Please reduce the length of the messages.
                except BaseException as e:
                    raise Exception(f"Error: {e}")

            # Parse and validate the result
            try:
                # self.ui.notify(title="PARSE AND VALIDATE", message=result)
                result_json_obj = LLMJsonOutputParser.parse_and_validate(
                    json_str=result, json_schema=REASON_JSON_SCHEMA_STR, llm=self.llm
                )
                return result_json_obj
            except FixJsonException:
                should_summary = True
                keep_it = True
                continue
            except BaseException as e:
                raise Exception(f"Error: {e}")

    async def _act(self, tool_name: str, args: Dict) -> str:
        # Get the tool to use from the procedural memory
        try:
            tool = self.prodedural_memory.remember_tool_by_name(tool_name)
        except BaseException as e:
            raise Exception("Invalid command: " + str(e))
        try:
            result = await tool.run(**args)
            return result
        except BaseException as e:
            raise Exception("Could not run tool: " + str(e))

    async def _task_complete(self, result: str) -> str:
        current_task = self.task_manager.get_current_task_string()
        await self.ui.notify(
            title="COMPLETED TASK", message=f"TASK:{current_task}", title_color="BLUE"
        )
        await self.ui.notify(title="RESULT", message=f"{result}", title_color="RED")

        self.task_manager.complete_current_task(result)

        return result