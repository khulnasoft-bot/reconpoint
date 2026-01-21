import abc
import json
import logging
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional
from .state import AgentState, AgentStateManager
from .registry import IntelligenceRegistry
from ..tools.registry import get_tool

@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    id: str
    name: str
    arguments: dict

@dataclass
class ToolResult:
    """Result from a tool execution."""
    tool_call_id: str
    tool_name: str
    result: Optional[str] = None
    error: Optional[str] = None
    success: bool = True

@dataclass
class AgentMessage:
    """A message in the agent conversation."""
    role: str  # "user", "assistant", "tool_result", "system"
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_results: Optional[List[ToolResult]] = None
    metadata: dict = field(default_factory=dict)
    usage: Optional[dict] = None

    def to_llm_format(self) -> dict:
        msg = {"role": self.role, "content": self.content}
        if self.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else tc.arguments,
                    },
                }
                for tc in self.tool_calls
            ]
        return msg

class BaseAgent(abc.ABC):
    """Base class for all reconPoint agents."""

    def __init__(
        self,
        llm: Any,
        tools: List[Any],
        runtime: Any,
        max_iterations: int = 10,
    ):
        self.llm = llm
        self.runtime = runtime
        self.max_iterations = max_iterations
        self.state_manager = AgentStateManager()
        self.conversation_history: List[AgentMessage] = []
        self.tools = list(tools)

    @property
    def state(self) -> AgentState:
        return self.state_manager.current_state

    @state.setter
    def state(self, value: AgentState):
        self.state_manager.transition_to(value)

    @abc.abstractmethod
    def get_system_prompt(self, mode: str = "agent") -> str:
        pass

    async def run(self, initial_message: str) -> AsyncIterator[AgentMessage]:
        """Main execution loop for the agent."""
        self.state_manager.transition_to(AgentState.THINKING)
        self.conversation_history.append(
            AgentMessage(role="user", content=initial_message)
        )

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            
            response = await self.llm.generate(
                system_prompt=self.get_system_prompt(),
                messages=[m.to_llm_format() for m in self.conversation_history],
                tools=self.tools,
            )

            if response.tool_calls:
                # Add assistant message with tool calls to history
                assistant_msg = AgentMessage(
                    role="assistant",
                    content=response.content or "",
                    tool_calls=response.tool_calls
                )
                self.conversation_history.append(assistant_msg)
                yield assistant_msg

                # Execute tools
                for tc in response.tool_calls:
                    # Check Cache
                    tool_hash = IntelligenceRegistry.generate_tool_hash(
                        agent_role=self.__class__.__name__,
                        tool_name=tc.name,
                        arguments=tc.arguments,
                        context=self.get_system_prompt()[:500]  # Use prefix of prompt as context
                    )
                    
                    cached_result = IntelligenceRegistry.get_tool_result(tool_hash)
                    if cached_result:
                        logger.info(f"Cache hit for tool {tc.name}")
                        tool_res = ToolResult(
                            tool_call_id=tc.id,
                            tool_name=tc.name,
                            result=cached_result,
                            success=True
                        )
                    else:
                        tool = get_tool(tc.name)
                        if tool:
                            try:
                                result = await tool.execute(tc.arguments, self.runtime)
                                IntelligenceRegistry.cache_tool_result(tool_hash, result)
                                tool_res = ToolResult(
                                    tool_call_id=tc.id,
                                    tool_name=tc.name,
                                    result=result,
                                    success=True
                                )
                            except Exception as e:
                                tool_res = ToolResult(
                                    tool_call_id=tc.id,
                                    tool_name=tc.name,
                                    error=str(e),
                                    success=False
                                )
                        else:
                            tool_res = ToolResult(
                                tool_call_id=tc.id,
                                tool_name=tc.name,
                                error=f"Tool '{tc.name}' not found.",
                                success=False
                            )
                    
                    res_msg = AgentMessage(
                        role="tool_result",
                        content=tool_res.result or tool_res.error,
                        tool_results=[tool_res]
                    )
                    self.conversation_history.append(res_msg)
                    yield res_msg

            if not response.tool_calls:
                msg = AgentMessage(role="assistant", content=response.content)
                self.conversation_history.append(msg)
                yield msg
                break
