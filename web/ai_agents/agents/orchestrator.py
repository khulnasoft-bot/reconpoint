from typing import Any, Dict, List, Optional, AsyncIterator, TYPE_CHECKING
import json
import asyncio
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ..prompts import pa_crew
from .models import CrewState, WorkerCallback
from .worker_pool import WorkerPool
from ..config.constants import ORCHESTRATOR_MAX_ITERATIONS

if TYPE_CHECKING:
    from ..llm.llm import LLM
    from ..runtime.runtime import Runtime
    from ..tools.registry import Tool
    from ..mcp.manager import MCPManager

class CrewOrchestrator:
    """Orchestrates multiple agents to perform complex security tasks."""

    def __init__(
        self,
        llm: Any,
        tools: List[Any],
        runtime: Any,
        project_id: int,
        on_worker_event: Optional[WorkerCallback] = None,
        rag_engine: Any = None,
        mcp_manager: Optional[Any] = None,
        runtime_type: str = "local",
        target: str = "",
        prior_context: str = "",
    ):
        self.llm = llm
        self.base_tools = tools
        self.runtime = runtime
        self.project_id = project_id
        self.on_worker_event = on_worker_event
        self.rag_engine = rag_engine
        self.mcp_manager = mcp_manager
        self.runtime_type = runtime_type
        self.target = target
        self.prior_context = prior_context

        self.state = CrewState.IDLE
        self.pool: Optional[WorkerPool] = None
        self._messages: List[Dict[str, Any]] = []
        self.channel_layer = get_channel_layer()
        self.group_name = f"ai_crew_{self.project_id}"

    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast data to the project-specific WebSocket group."""
        if self.channel_layer:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "crew_update",
                    "data": data,
                },
            )

    def _get_system_prompt(self) -> str:
        """Build the system prompt with target info and context."""
        tool_lines = []
        for t in self.base_tools:
            desc = (
                t.description[:80] + "..." if len(t.description) > 80 else t.description
            )
            tool_lines.append(f"- **{t.name}**: {desc}")
        worker_tools_formatted = (
            "\n".join(tool_lines) if tool_lines else "No tools available"
        )

        # Get saved notes for this specific project
        notes_context = ""
        try:
            from recon_note.models import TodoNote
            notes = TodoNote.objects.filter(project_id=self.project_id)
            if notes.exists():
                sections = ["## Project Knowledge (from reconPoint database)"]
                for n in notes:
                    importance = " [IMPORTANT]" if n.is_important else ""
                    sections.append(f"- {n.title}{importance}: {n.description}")
                notes_context = "\n".join(sections)
        except Exception:
            pass

        # Get runtime environment with detected tools
        env = self.runtime.environment

        return pa_crew.render(
            target=self.target or "Not specified",
            prior_context=self.prior_context or "None - starting fresh",
            notes_context=notes_context,
            worker_tools=worker_tools_formatted,
            environment=env,
        )

    async def run(self, task: str) -> AsyncIterator[Dict[str, Any]]:
        """Run the crew on a task."""
        self.state = CrewState.RUNNING
        update = {"phase": "starting"}
        await self.broadcast(update)
        yield update

        from .crew_tools import create_crew_tools

        self.pool = WorkerPool(
            llm=self.llm,
            tools=self.base_tools,
            runtime=self.runtime,
            target=self.target,
            rag_engine=self.rag_engine,
            mcp_manager=self.mcp_manager,
            runtime_type=self.runtime_type,
            on_worker_event=self.on_worker_event,
        )

        crew_tools = create_crew_tools(self.pool, self.llm)

        self._messages = [
            {"role": "user", "content": f"Target: {self.target}\n\nTask: {task}"}
        ]

        iteration = 0
        final_report = ""

        try:
            while iteration < ORCHESTRATOR_MAX_ITERATIONS:
                iteration += 1

                response = await self.llm.generate(
                    system_prompt=self._get_system_prompt(),
                    messages=self._messages,
                    tools=crew_tools,
                )

                # Track tokens for orchestrator
                if response.usage:
                    total = response.usage.get("total_tokens", 0)
                    if total > 0:
                        update = {"phase": "tokens", "tokens": total}
                        await self.broadcast(update)
                        yield update

                # Check for tool calls first to determine if content is "thinking" or "final answer"
                if response.tool_calls:
                    # If there are tool calls, the content is "thinking" (reasoning before action)
                    if response.content:
                        update = {"phase": "thinking", "content": response.content}
                        await self.broadcast(update)
                        yield update
                        self._messages.append(
                            {"role": "assistant", "content": response.content}
                        )

                    def get_tc_name(tc):
                        if hasattr(tc, "function"):
                            return tc.function.name
                        return (
                            tc.get("function", {}).get("name", "")
                            if isinstance(tc, dict)
                            else ""
                        )

                    def get_tc_args(tc):
                        if hasattr(tc, "function"):
                            args = tc.function.arguments
                        else:
                            args = (
                                tc.get("function", {}).get("arguments", "{}")
                                if isinstance(tc, dict)
                                else "{}"
                            )
                        if isinstance(args, str):
                            try:
                                return json.loads(args)
                            except json.JSONDecodeError:
                                return {}
                        return args if isinstance(args, dict) else {}

                    def get_tc_id(tc):
                        if hasattr(tc, "id"):
                            return tc.id
                        return tc.get("id", "") if isinstance(tc, dict) else ""

                    self._messages.append(
                        {
                            "role": "assistant",
                            "content": response.content or "",
                            "tool_calls": [
                                {
                                    "id": get_tc_id(tc),
                                    "type": "function",
                                    "function": {
                                        "name": get_tc_name(tc),
                                        "arguments": json.dumps(get_tc_args(tc)),
                                    },
                                }
                                for tc in response.tool_calls
                            ],
                        }
                    )

                    async def execute_tool_call(tc):
                        tc_name = get_tc_name(tc)
                        tc_args = get_tc_args(tc)
                        tc_id = get_tc_id(tc)

                        update = {"phase": "tool_call", "tool": tc_name, "args": tc_args}
                        await self.broadcast(update)
                        # We don't yield here because multiple workers might yield at once
                        # the caller handles the main loop yield

                        tool = next((t for t in crew_tools if t.name == tc_name), None)
                        if not tool:
                            error_msg = f"Unknown tool: {tc_name}"
                            return {
                                "role": "tool",
                                "tool_call_id": tc_id,
                                "content": error_msg,
                                "tool_name": tc_name,
                                "error": True
                            }

                        try:
                            # If it's the finish tool, we might need special handling
                            # but usually we want to execute it last or if it's the only one.
                            # For now, let's just run it.
                            result = await tool.execute(tc_args, self.runtime)
                            
                            update = {
                                "phase": "tool_result",
                                "tool": tc_name,
                                "result": result,
                            }
                            await self.broadcast(update)
                            
                            return {
                                "role": "tool",
                                "tool_call_id": tc_id,
                                "content": str(result),
                                "tool_name": tc_name
                            }

                        except Exception as e:
                            error_msg = f"Error: {e}"
                            update = {
                                "phase": "tool_result",
                                "tool": tc_name,
                                "result": error_msg,
                            }
                            await self.broadcast(update)
                            return {
                                "role": "tool",
                                "tool_call_id": tc_id,
                                "content": error_msg,
                                "tool_name": tc_name,
                                "error": True
                            }

                    # Execute all tool calls in parallel
                    tool_results = await asyncio.gather(
                        *[execute_tool_call(tc) for tc in response.tool_calls]
                    )

                    # Append results to messages in order
                    for res in tool_results:
                        self._messages.append({
                            "role": res["role"],
                            "tool_call_id": res["tool_call_id"],
                            "content": res["content"]
                        })

                        # Special handling for finish signals in bundles
                        if res.get("tool_name") == "finish" and not res.get("error"):
                            final_report = res["content"]
                            # Check tokens for finish
                            if (
                                hasattr(self.pool, "finish_tokens")
                                and self.pool.finish_tokens > 0
                            ):
                                update = {
                                    "phase": "tokens",
                                    "tokens": self.pool.finish_tokens,
                                }
                                await self.broadcast(update)
                                self.pool.finish_tokens = 0

                    if final_report:
                        break
                else:
                    # No tool calls - check if agents were spawned
                    content = response.content or ""
                    if content:
                        self._messages.append({"role": "assistant", "content": content})

                    # If agents were spawned, call finish to synthesize results
                    # Otherwise, use the response directly as final report
                    if self.pool and self.pool.get_workers():
                        # Agents exist - call finish to synthesize
                        update = {"phase": "thinking", "content": content}
                        await self.broadcast(update)
                        yield update
                        finish_tool = next(
                            (t for t in crew_tools if t.name == "finish"), None
                        )
                        if finish_tool:
                            try:
                                final_report = await finish_tool.execute(
                                    {"context": content}, self.runtime
                                )
                                # Track tokens from auto-finish synthesis
                                if (
                                    hasattr(self.pool, "finish_tokens")
                                    and self.pool.finish_tokens > 0
                                ):
                                    update = {
                                        "phase": "tokens",
                                        "tokens": self.pool.finish_tokens,
                                    }
                                    await self.broadcast(update)
                                    yield update
                                    self.pool.finish_tokens = 0
                                break
                            except Exception as e:
                                update = {
                                    "phase": "error",
                                    "error": f"Auto-finish failed: {e}",
                                }
                                await self.broadcast(update)
                                yield update
                                break
                        else:
                            final_report = content
                            break
                    else:
                        # No agents - response is the final answer
                        final_report = content
                        break

            self.state = CrewState.COMPLETE
            update = {"phase": "complete", "report": final_report}
            await self.broadcast(update)
            yield update

        except Exception as e:
            self.state = CrewState.ERROR
            update = {"phase": "error", "error": str(e)}
            await self.broadcast(update)
            yield update

        finally:
            if self.pool:
                await self.pool.cancel_all()

    async def cancel(self) -> None:
        """Cancel the crew run."""
        if self.pool:
            await self.pool.cancel_all()
        self._cleanup_pending_calls()
        self.state = CrewState.IDLE

    def _cleanup_pending_calls(self) -> None:
        """Remove incomplete tool calls from message history."""
        while self._messages:
            last_msg = self._messages[-1]
            if last_msg.get("role") == "assistant" and last_msg.get("tool_calls"):
                self._messages.pop()
            elif last_msg.get("role") == "tool":
                self._messages.pop()
            elif last_msg.get("role") == "user":
                self._messages.pop()
                break
            else:
                break
