import asyncio
import json
import time
import httpx

API_BASE = "http://127.0.0.1:8000/api"

async def benchmark_generation():
    print("=" * 70)
    print("PROMPT BUILDER: MULTI-AGENT SWARM REAL-TIME BENCHMARK")
    print("=" * 70)

    start_time = time.time()
    payload = {
        "raw_idea": "An AI-powered automated pull request reviewer that comments on security vulnerabilities and logic flaws.",
        "user_constraints": {
            "preferred_stack": "FastAPI + React",
            "database": "PostgreSQL"
        }
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        # Trigger generation
        post_start = time.time()
        res = await client.post(f"{API_BASE}/blueprint/generate", json=payload)
        assert res.status_code == 200, f"Trigger failed: {res.status_code} {res.text}"
        job_data = res.json()
        job_id = job_data["job_id"]
        print(f"[0.0s] Triggered Job: {job_id}")

        last_agent = None
        last_step_time = time.time()
        final_blueprint = None

        # Listen to SSE stream until completion
        async with client.stream("GET", f"{API_BASE}/blueprint/stream/{job_id}", timeout=300.0) as response:
            assert response.status_code == 200, f"Stream failed: {response.status_code}"
            
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                raw_data = line[5:].strip()
                try:
                    event = json.loads(raw_data)
                except Exception:
                    continue

                event_type = event.get("event")
                step = event.get("current_step", "")
                agent = event.get("active_agent", "")
                elapsed = time.time() - start_time
                step_duration = time.time() - last_step_time

                if agent != last_agent and agent:
                    print(f"[{elapsed:6.2f}s] (+{step_duration:4.1f}s) AGENT: {agent:<25} | Step: {step}", flush=True)
                    last_agent = agent
                    last_step_time = time.time()

                if event_type == "completed":
                    print(f"\n[SUCCESS] Completed in {elapsed:.2f} seconds!", flush=True)
                    break
                elif event_type == "error":
                    print(f"\n[ERROR] Pipeline failed after {elapsed:.2f}s: {event.get('error')}", flush=True)
                    break

        # Fetch final blueprint stats
        inspect_res = await client.get(f"{API_BASE}/blueprint/{job_id}")
        data = inspect_res.json()
        status = data.get("status")
        total_time = time.time() - start_time
        blueprint_text = data.get("final_blueprint", "")
        word_count = len(blueprint_text.split()) if blueprint_text else 0

        print("=" * 70)
        print(f"STATUS:      {status}")
        print(f"TOTAL TIME:  {total_time:.2f} seconds ({total_time / 60:.2f} minutes)")
        print(f"WORD COUNT:  {word_count:,} words")
        print(f"SECTIONS:    {len(data.get('sections', {}))} completed")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(benchmark_generation())
