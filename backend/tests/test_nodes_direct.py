import asyncio
import time
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.agents.nodes import section_drafting_node
from app.agents.state import BlueprintState

async def test():
    state: BlueprintState = {
        'refined_idea': 'Automated PR reviewer',
        'red_team_critique': 'Flaws in false positives',
        'section_6_tech_arch': 'FastAPI PostgreSQL',
        'section_2_market': 'DevOps CI/CD market',
        'logs': []
    }
    t0 = time.time()
    print("Starting section_drafting_node test...", flush=True)
    res = await section_drafting_node(state)
    print(f"Completed in {time.time()-t0:.2f}s; keys: {list(res.keys())}", flush=True)

if __name__ == "__main__":
    asyncio.run(test())
