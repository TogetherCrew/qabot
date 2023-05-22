import os
import json
from typing import Dict, Any, Optional, Set, Union
from pydantic import BaseModel, Field
from llm.summarize.prompt import get_final_answer_template
from memory.procedual_memory import ProcedualMemory, ToolNotFoundException
from memory.episodic_memory import EpisodicMemory, Episode
from memory.semantic_memory import SemanticMemory
from ui.base import BaseHumanUserInterface
from ui.cui import CommandlineUserInterface
import llm.reason.prompt as ReasonPrompt
from task_manager import Task
from task_manager import TaskManager
from llm.json_output_parser import LLMJsonOutputParser
from llm.reason.schema import JsonSchema as ReasonSchema
from langchain.llms.base import BaseLLM
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI

# Define the default values
DEFAULT_AGENT_NAME = "AI"
DEFAULT_AGENT_ROLE = "Autonomous AI agent that uses both inference and tools to answer many things"
DEFAULT_AGENT_GOAL = "Ending world hunger"
DEFAULT_AGENT_DIR = "./agent_data"


# Define the schema for the llm output
REASON_JSON_SCHEMA_STR = json.dumps(ReasonSchema.schema)


class Agent(BaseModel):
    """
    This is the main class for the Agent. It is responsible for managing the tools and the agent.
    """
    # Define the tools
    dir: str = Field(
        DEFAULT_AGENT_DIR, description="The folder path to the directory where the agent data is stored and saved")
    name: str = Field(DEFAULT_AGENT_NAME, description="The name of the agent")
    role: str = Field(DEFAULT_AGENT_ROLE, description="The role of the agent")
    goal: str = Field(DEFAULT_AGENT_GOAL, description="The goal of the agent")
    ui: BaseHumanUserInterface = Field(
        CommandlineUserInterface(), description="The user interface for the agent")
    llm: BaseLLM = Field(..., description="llm class for the agent")
    openaichat: Optional[ChatOpenAI] = Field(
        None, description="ChatOpenAI class for the agent")
    prodedural_memory: ProcedualMemory = Field(
        ProcedualMemory(), description="The procedural memory about tools agent uses")
    episodic_memory: EpisodicMemory = Field(
        None, description="The short term memory of the agent")
    semantic_memory: SemanticMemory = Field(
        None, description="The long term memory of the agent")
    task_manager: TaskManager = Field(
        None, description="The task manager for the agent")

    def __init__(self, openai_api_key: str, dir: str, **data: Any) -> None:
        super().__init__(**data)
        self.task_manager = TaskManager(llm=self.llm)
        self.episodic_memory = EpisodicMemory(llm=self.llm)
        self.semantic_memory = SemanticMemory(llm=self.llm, openaichat=self.openaichat)

        self._get_absolute_path()
        self._create_dir_if_not_exists()

        if self._agent_data_exists():
            load_data = self.ui.get_binary_user_input(
                "Agent data already exists. Do you want to load the data?\n"
                "If you choose 'Yes', the data will be loaded.\n"
                "If you choose 'No', the data will be overwritten."
            )
            if load_data:
                self.load_agent()
            else:
                self.ui.notify("INFO", "Agent data will be overwritten.")
        self.ui.notify(
            "START", f"Hello, I am {self.name}. {self.role}. My goal is {self.goal}.")

    def _get_absolute_path(self) -> None:
        return os.path.abspath(self.dir)

    def _create_dir_if_not_exists(self) -> None:
        absolute_path = self._get_absolute_path()
        if not os.path.exists(absolute_path):
            os.makedirs(absolute_path)

    def _agent_data_exists(self) -> bool:
        absolute_path = self._get_absolute_path()
        return "agent_data.json" in os.listdir(absolute_path)

    def run(self):
        with self.ui.loading("Generate Subquestions..."):
            # Get the relevant tools
            # If agent has to much tools, use "remember_relevant_tools"
            # because too many tool information will cause context windows overflow.
            # Set up the prompt
            tool_info = self.prodedural_memory.tools_to_prompt(
                self.prodedural_memory.remember_all_tools())

            self.task_manager.generate_subquestions(
                name=self.name,
                role=self.role,
                goal=self.goal,
                tool_info=tool_info,
            )
        self.ui.notify(title="SUBQUESTIONS",
                       message=self.task_manager.subquestions,
                       title_color="RED")
        with self.ui.loading("Generate Task Plan..."):
            self.task_manager.generate_task_plan(
                name=self.name,
                role=self.role,
                goal=self.goal
            )
        self.ui.notify(title="ALL TASKS",
                       message=self.task_manager.get_incomplete_tasks_string(),
                       title_color="BLUE")

        while True:
            current_task = self.task_manager.get_current_task_string()
            if current_task:
                self.ui.notify(title="CURRENT TASK",
                               message=current_task,
                               title_color="BLUE")
            else:
                self.ui.notify(title="FINISH",
                               message=f"All tasks are completed. {self.name} will end the operation.",
                               title_color="RED")
                with self.ui.loading("Final answer..."):
                    final_prompt = get_final_answer_template()

                    completed_tasks = self.task_manager.get_completed_tasks()
                    all_related_knowledge = dict()
                    for task in completed_tasks:
                        related_knowledge = self.semantic_memory.remember_related_knowledge(
                            task.description,
                            k=5
                        )
                        all_related_knowledge.update(related_knowledge)

                    all_related_past_episodes = ""
                    for task in completed_tasks:
                        related_past_episodes = self.episodic_memory.remember_related_episodes(
                            task.description,
                            k=2
                        )
                        summary_of_related_past_episodes = ("\n").join(
                            [past.summary for past in related_past_episodes])
                        all_related_past_episodes += f"\n{summary_of_related_past_episodes}"

                    input_variables = {"name": self.name,
                                       "role": self.role,
                                       "goal": self.goal,
                                       "completed_tasks": self.task_manager.get_completed_tasks_as_string(),
                                       "results_of_completed_tasks": self.task_manager.get_results_completed_tasks_as_string(),
                                       "related_knowledge": all_related_knowledge,
                                       "related_past_episodes": all_related_past_episodes}

                    final_prompt_formatted = final_prompt.format_prompt(
                        **input_variables)
                    self.ui.notify(title="FINAL PROMPT",
                                   message=final_prompt_formatted.to_string())

                    llm_chain = LLMChain(prompt=final_prompt, llm=self.llm)
                    try:
                        result = llm_chain.predict(**input_variables)
                    except Exception as e:
                        raise Exception(f"Error: {e}")

                    if result:
                        self.ui.notify(title="FINAL ANSWER",
                                       message=result,
                                       title_color="RED")
                break

            # ReAct: Reasoning
            with self.ui.loading("Thinking..."):
                try:
                    reasoning_result = self._reason()
                    thoughts = reasoning_result["thoughts"]
                    action = reasoning_result["action"]
                    tool_name = action["tool_name"]
                    args = action["args"]
                except Exception as e:
                    raise e
            self.ui.notify(title="TASK", message=thoughts["task"])
            self.ui.notify(title="OBSERVATION", message=reasoning_result["observation"])
            self.ui.notify(title="IDEA", message=thoughts["idea"])
            self.ui.notify(title="REASONING", message=thoughts["reasoning"])
            self.ui.notify(title="CRITICISM", message=thoughts["criticism"])
            self.ui.notify(title="THOUGHT", message=thoughts["summary"])
            self.ui.notify(title="NEXT ACTION", message=action)

            # Task Complete
            if tool_name == "task_complete":
                action_result = args["result"]  # todo: check if result is correct
                # todo: check if list of TASK need be updated
                self._task_complete(action_result)
                # save agent data
                with self.ui.loading("Save agent data..."):
                    self.save_agent()

            # Action with tools
            else:
                tool = None
                try:
                    tool = self.prodedural_memory.remember_tool_by_name(tool_name)

                    if not tool:
                        raise Exception(
                            f"Tool {tool_name} is not found in the procedural memory.")

                    def act(tool_name, args):
                        try:
                            action_result = self._act(tool_name, args)
                        except Exception as e:
                            raise e
                        self.ui.notify(title="ACTION RESULT", message=action_result)
                        return action_result

                    self.ui.notify(
                        title="LOG", message=f"Tool: {tool_name} user_permission_required:{tool.user_permission_required}")
                    if tool.user_permission_required:
                        # Ask for permission to run the action
                        user_permission = self.ui.get_binary_user_input(
                            "Do you want to continue?")
                        if not user_permission:
                            action_result = "User Denied to run Action"
                            self.ui.notify(title="USER INPUT", message=action_result)
                        else:
                            action_result = act(tool_name, args)
                    else:
                        action_result = act(tool_name, args)
                except ToolNotFoundException as e:
                    self.ui.notify(
                        title="LOG", message=f"Tool {tool_name} not exist. Pick one tool [TOOL] from the list.")
                    action_result = f"Tool {tool_name} not exist. Pick one tool [TOOL] from the list."
                    pass
                except Exception as e:
                    raise e

            episode = Episode(
                thoughts=thoughts,
                action=action,
                result=action_result
            )

            summary = self.episodic_memory.summarize_and_memorize_episode(episode)
            self.ui.notify(title="MEMORIZE NEW EPISODE",
                           message=summary, title_color="blue")

            entities = self.semantic_memory.extract_entity(action_result)
            self.ui.notify(title="MEMORIZE NEW KNOWLEDGE",
                           message=entities, title_color="blue")

    def _reason(self) -> Union[str, Dict[Any, Any]]:
        current_task_description = self.task_manager.get_current_task_string()

        # Retrie task related memories
        with self.ui.loading("Retrieve memory..."):
            # Retrieve memories related to the task.
            related_past_episodes = self.episodic_memory.remember_related_episodes(
                current_task_description,
                k=2)
            if len(related_past_episodes) > 0:
                # self.ui.notify(title="TASK RELATED EPISODE",
                #                message=related_past_episodes)
                summary_of_related_past_episodes = ("\n").join(
                    [past.summary for past in related_past_episodes])
                self.ui.notify(title="SUMMARY OF TASK RELATED EPISODES",
                               message=summary_of_related_past_episodes)
                related_past_episodes = summary_of_related_past_episodes

            # Retrieve concepts related to the task.
            related_knowledge = self.semantic_memory.remember_related_knowledge(
                current_task_description,
                k=5
            )
            if len(related_knowledge) > 0:
                self.ui.notify(title="TASK RELATED KNOWLEDGE",
                               message=related_knowledge)

        # Get the relevant tools
        # If agent has to much tools, use "remember_relevant_tools"
        # because too many tool information will cause context windows overflow.
        tools = self.prodedural_memory.remember_all_tools()

        # Set up the prompt
        tool_info = self.prodedural_memory.tools_to_prompt(tools)

        # Get the recent episodes
        memory = self.episodic_memory.remember_recent_episodes(2)

        # If OpenAI Chat is available, it is used for higher accuracy results.
        if self.openaichat:
            prompt = ReasonPrompt.get_chat_template(memory=memory).format_prompt(
                name=self.name,
                role=self.role,
                goal=self.goal,
                related_past_episodes=related_past_episodes,
                related_knowledge=related_knowledge,
                task=current_task_description,
                tool_info=tool_info
            )
            prompt_msg = prompt.to_messages()

            # self.ui.notify(title="REASONING PROMPT",
            #                message=" ".join([msg.content for msg in prompt_msg]))
            try:
                result = self.openaichat(prompt_msg).content
                # openai.error.InvalidRequestError: This model's maximum context length is 4097 tokens. However, your messages resulted in 4879 tokens. Please reduce the length of the messages.
            except Exception as e:
                raise Exception(f"Error: {e}")

        else:
            # Get the result from the LLM
            prompt = ReasonPrompt.get_template(memory=memory)
            llm_chain = LLMChain(prompt=prompt, llm=self.llm)
            try:
                result = llm_chain.predict(
                    name=self.name,
                    role=self.role,
                    goal=self.goal,
                    related_past_episodes=related_past_episodes,
                    elated_knowledge=related_knowledge,
                    task=current_task_description,
                    tool_info=tool_info
                )
            except Exception as e:
                raise Exception(f"Error: {e}")

        # Parse and validate the result
        try:
            # self.ui.notify(title="PARSE AND VALIDATE", message=result)
            result_json_obj = LLMJsonOutputParser.parse_and_validate(
                json_str=result,
                json_schema=REASON_JSON_SCHEMA_STR,
                llm=self.llm
            )
            return result_json_obj
        except Exception as e:
            raise Exception(f"Error: {e}")

    def _act(self, tool_name: str, args: Dict) -> str:
        # Get the tool to use from the procedural memory
        try:
            tool = self.prodedural_memory.remember_tool_by_name(tool_name)
        except Exception as e:
            raise Exception("Invalid command: " + str(e))
        try:
            result = tool.run(**args)
            return result
        except Exception as e:
            raise Exception("Could not run tool: " + str(e))

    def _task_complete(self, result: str) -> str:
        current_task = self.task_manager.get_current_task_string()
        self.ui.notify(title="COMPLETED TASK",
                       message=f"TASK:{current_task}",
                       title_color="BLUE")
        self.ui.notify(title="RESULT",
                       message=f"{result}",
                       title_color="RED")

        self.task_manager.complete_current_task(result)

        return result

    def save_agent(self) -> None:
        episodic_memory_dir = f"{self.dir}/episodic_memory"
        semantic_memory_dir = f"{self.dir}/semantic_memory"
        filename = f"{self.dir}/agent_data.json"
        self.episodic_memory.save_local(path=episodic_memory_dir)
        self.semantic_memory.save_local(path=semantic_memory_dir)

        data = {"name": self.name,
                "role": self.role,
                "episodic_memory": episodic_memory_dir,
                "semantic_memory": semantic_memory_dir
                }
        with open(filename, "w") as f:
            json.dump(data, f)

    def load_agent(self) -> None:
        absolute_path = self._get_absolute_path()
        if not "agent_data.json" in os.listdir(absolute_path):
            self.ui.notify("ERROR", "Agent data does not exist.", title_color="red")

        with open(os.path.join(absolute_path, "agent_data.json")) as f:
            agent_data = json.load(f)
            self.name = agent_data["name"]
            self.role = agent_data["role"]

            try:
                self.semantic_memory.load_local(agent_data["semantic_memory"])
            except Exception as e:
                self.ui.notify(
                    "ERROR", "Semantic memory data is corrupted.", title_color="red")
                raise e
            else:
                self.ui.notify(
                    "INFO", "Semantic memory data is loaded.", title_color="GREEN")

            try:
                self.episodic_memory.load_local(agent_data["episodic_memory"])
            except Exception as e:
                self.ui.notify(
                    "ERROR", "Episodic memory data is corrupted.", title_color="RED")
                raise e
            else:
                self.ui.notify(
                    "INFO", "Episodic memory data is loaded.", title_color="GREEN")
