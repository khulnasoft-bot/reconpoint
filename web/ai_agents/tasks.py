import asyncio
import logging
from celery import shared_task
from django.utils import timezone
from dashboard.models import Project, AIReasoningLog, SecurityAuditLog, InAppNotification
from startScan.models import ScanHistory, Subdomain
from .agents.orchestrator import CrewOrchestrator
from .agents.models import AgentStatus

logger = logging.getLogger(__name__)

@shared_task(name="run_crew_ai_analysis")
def run_crew_ai_analysis(project_id, user_username, auto_execute=False):
    """
    Celery task to run the multi-agent AI analysis.
    """
    project = Project.objects.get(id=project_id)
    
    # helper to run async code in sync celery task
    def _run_async(coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    async def _perform_analysis():
        from .llm.llm import LLM
        from .runtime.runtime import LocalRuntime
        from .tools.loader import ToolLoader
        from .knowledge.rag import RAGEngine
        from pathlib import Path
        
        # 1. Initialize RAG Engine with Distributed Vector Store
        from .knowledge.distributed_rag import RedisVectorStore
        vector_store = RedisVectorStore(prefix=f"ai_knowledge:{project_id}")
        
        # We assume knowledge is in a 'knowledge' directory within the ai_agents package
        knowledge_dir = Path(__file__).parent / "knowledge" / "data"
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        rag_engine = RAGEngine(knowledge_path=knowledge_dir, vector_store=vector_store)
        
        # 2. Initialize LLM with RAG support
        llm = LLM(rag_engine=rag_engine)
        
        # 3. Initialize Runtime (Configurable via ENV or setting)
        from django.conf import settings
        runtime_type = getattr(settings, "RECONPOINT_AGENT_RUNTIME", "local")
        
        if runtime_type == "docker":
            from .runtime.docker_runtime import DockerRuntime
            runtime = DockerRuntime(project_id=project_id)
        else:
            runtime = LocalRuntime(project_id=project_id)
        
        # 4. Load Tools
        loader = ToolLoader()
        tools = loader.get_all_tools()
        
        # 5. Initialize MCP Manager
        from .mcp.manager import MCPManager
        mcp_manager = MCPManager()
        # Connect to all configured servers (including Metasploit if configured)
        await mcp_manager.connect_all()
        
        orchestrator = CrewOrchestrator(
            llm=llm,
            tools=tools,
            runtime=runtime,
            project_id=project_id,
            rag_engine=rag_engine,
            mcp_manager=mcp_manager,
            target=project.name,
            runtime_type=runtime_type
        )
        
        # Initial status update
        SecurityAuditLog.objects.create(
            project=project,
            action="AI_CREW_ANALYSIS_STARTED",
            performed_by=user_username,
            details={"mode": "multi-agent"}
        )

        try:
            results = []
            async for update in orchestrator.run(f"Perform a full security assessment of the project {project.name}. Analyze active subdomains and suggest next steps."):
                results.append(update)
            
            # Final state synthesis
            # Note: The 'finish' tool result is the final report
            final_report = ""
            for res in reversed(results):
                if res.get("phase") == "complete":
                    final_report = res.get("report", "")
                    break
            
            # Save to AIReasoningLog
            AIReasoningLog.objects.create(
                project=project,
                recon_analysis="See worker findings for detailed analysis.",
                attack_hypotheses="Autonomous plan execution.",
                risk_assessment="Findings synthesized in final report.",
                final_report=final_report
            )

            # Check for critical keywords in report
            if "CRITICAL" in final_report.upper() or "HIGH" in final_report.upper():
                InAppNotification.objects.create(
                    project=project,
                    notification_type="project",
                    status="error",
                    title="AI Crew: Critical Findings Identified",
                    description=f"The AI crew identified potential high-risk vulnerabilities on {project.name}.",
                    icon="mdi-robot-industrial",
                )

            SecurityAuditLog.objects.create(
                project=project,
                action="AI_CREW_ANALYSIS_COMPLETED",
                performed_by="ai_agent",
                details={"status": "success"}
            )

            return True
        except Exception as e:
            logger.error(f"AI Crew Analysis failed: {e}", exc_info=True)
            SecurityAuditLog.objects.create(
                project=project,
                action="AI_CREW_ANALYSIS_FAILED",
                performed_by="ai_agent",
                details={"error": str(e)},
                risk_level="high",
            )
            return False

    return _run_async(_perform_analysis())
