import os
import django
import sys
from pathlib import Path

# Add the web directory to sys.path
sys.path.append(str(Path(__file__).parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reconPoint.settings")
django.setup()

def verify_imports():
    print("Checking AI Agents imports...")
    try:
        from ai_agents.tasks import run_crew_ai_analysis
        print("✅ ai_agents.tasks.run_crew_ai_analysis imported successfully")
        
        from ai_agents.agents.orchestrator import CrewOrchestrator
        print("✅ ai_agents.agents.orchestrator.CrewOrchestrator imported successfully")
        
        from ai_agents.llm.llm import LLM
        print("✅ ai_agents.llm.llm.LLM imported successfully")
        
        from ai_agents.runtime.runtime import LocalRuntime
        print("✅ ai_agents.runtime.runtime.LocalRuntime imported successfully")
        
        from ai_agents.tools.loader import ToolLoader
        loader = ToolLoader()
        tools = loader.get_all_tools()
        print(f"✅ ToolLoader initialized. Loaded {len(tools)} tools.")
        for tool in tools:
            print(f"   - {tool.name}")
            
        from ai_agents.knowledge.rag import RAGEngine
        print("✅ ai_agents.knowledge.rag.RAGEngine imported successfully")
        
        print("\nAll core AI components verified successfully!")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_imports()
