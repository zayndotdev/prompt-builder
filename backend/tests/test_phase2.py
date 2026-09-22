import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.agents.workflow import blueprint_graph
from app.agents.state import BlueprintState

async def test_full_pipeline():
    print("=" * 60, flush=True)
    print("PHASE 2 REAL-TIME MULTI-AGENT SWARM TEST", flush=True)
    print("=" * 60, flush=True)

    raw_idea = "An AI voice agent for plumbing and HVAC contractors that answers emergency calls 24/7, qualifies leaks/furnace issues, and books dispatches into ServiceTitan or Jobber."
    
    initial_state: BlueprintState = {
        "job_id": "test-job-001",
        "raw_idea": raw_idea,
        "user_constraints": {
            "platform": "Web & Mobile",
            "preferred_stack": "FastAPI + React + PostgreSQL",
            "budget": "Free / Low-cost tier focus"
        },
        "logs": [],
        "expansion_attempts": {},
    }

    print(f"\n[1] Submitting Raw Idea:\n    \"{raw_idea}\"", flush=True)
    print("\n[2] Executing Multi-Agent LangGraph Swarm...", flush=True)

    # Stream graph updates node by node
    async for output in blueprint_graph.astream(initial_state):
        for node_name, state_update in output.items():
            print(f"\n---> Finished Node: [{node_name}]", flush=True)
            if "logs" in state_update and state_update["logs"]:
                print(f"     Latest Log: {state_update['logs'][-1]}", flush=True)
            if "total_words" in state_update:
                print(f"     Current Total Words: {state_update['total_words']:,}", flush=True)
            if "under_target_sections" in state_update:
                print(f"     Under Target Sections: {state_update['under_target_sections']}", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("PHASE 2 SWARM TEST COMPLETED SUCCESSFULLY!", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
