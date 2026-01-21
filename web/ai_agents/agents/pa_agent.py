from .base_agent import AgentMessage, BaseAgent
from .state import AgentStateManager
from ..config.constants import AGENT_MAX_ITERATIONS
from ..llm.memory import ConversationMemory
from ..tools.registry import get_all_tools, get_tool


class ReconAgentAgent(BaseAgent):
    """Main pentesting agent for ReconAgent."""

    def __init__(
        self,
        llm: "LLM",
        tools: List["Tool"],
        runtime: "Runtime",
        target: Optional[str] = None,
        scope: Optional[List[str]] = None,
        rag_engine: Optional["RAGEngine"] = None,
        **kwargs,
    ):
        """
        Initialize the ReconAgent agent.

        Args:
            llm: The LLM instance for generating responses
            tools: List of tools available to the agent
            runtime: The runtime environment for tool execution
            target: Primary target for penetration testing
            scope: List of in-scope targets/networks
            rag_engine: RAG engine for knowledge retrieval
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(llm, tools, runtime, **kwargs)
        self.target = target
        self.scope = scope or []
        self.rag_engine = rag_engine

    def get_system_prompt(self, mode: str = "agent") -> str:
        """Generate system prompt with context.

        Args:
            mode: 'agent' for autonomous mode, 'assist' for single-shot assist mode
        """
        # Get RAG context if available
        rag_context = ""
        if self.rag_engine and self.conversation_history:
            last_msg = self.conversation_history[-1].content
            # Ensure content is a string (could be list for multimodal)
            if isinstance(last_msg, list):
                last_msg = " ".join(
                    str(part.get("text", ""))
                    for part in last_msg
                    if isinstance(part, dict)
                )
            if last_msg:
                relevant = self.rag_engine.search(last_msg)
                if relevant:
                    rag_context = "\n\n".join(relevant)

        # Get saved notes for this project
        notes_context = ""
        try:
            from recon_note.models import TodoNote
            # Assuming project_id is available or passed in. 
            # For now, let's assume it's part of the agent state or passed in.
            project_id = getattr(self, "project_id", None)
            if project_id:
                notes = TodoNote.objects.filter(project_id=project_id)
                if notes.exists():
                    sections = ["## Project Knowledge (from reconPoint database)"]
                    for n in notes:
                        importance = " [IMPORTANT]" if n.is_important else ""
                        sections.append(f"- {n.title}{importance}: {n.description}")
                    notes_context = "\n".join(sections)
        except Exception:
            pass

        # Get environment info from runtime
        env = self.runtime.environment

        # Select template based on mode
        template = pa_assist if mode == "assist" else pa_agent

        return template.render(
            target=self.target,
            scope=self.scope,
            environment=env,
            rag_context=rag_context,
            notes_context=notes_context,
            tools=self.tools,
            plan=getattr(self.runtime, "plan", None),
        )

    async def agent_loop(self, initial_message: str) -> AsyncIterator[AgentMessage]:
        """Main agent execution loop with iterative reasoning."""
        # This overrides BaseAgent.run logic for more advanced loop if needed
        # For now, let's use the BaseAgent's loop but ensure it reports tokens properly
        async for msg in self.run(initial_message):
            yield msg
