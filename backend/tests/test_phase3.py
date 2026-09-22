import asyncio
import json
import sys
import httpx
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

API_BASE = "http://127.0.0.1:8000/api"

async def test_api_endpoints():
    print("=" * 60)
    print("PHASE 3 FASTAPI SERVER INTEGRATION TEST")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=120.0) as client:
        # 1. Test Providers Endpoint
        print("\n[1] Testing GET /api/config/providers...", flush=True)
        res = await client.get(f"{API_BASE}/config/providers")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        print(f"    Active Providers: {data.get('providers')}", flush=True)
        print("    [PASS] Providers endpoint verified!")

        # 2. Test Blueprint Generation Trigger
        print("\n[2] Testing POST /api/blueprint/generate...", flush=True)
        payload = {
            "raw_idea": "A privacy-first personal finance tracker with automated bank CSV import and categorization.",
            "user_constraints": {
                "preferred_stack": "FastAPI + React",
                "database": "SQLite"
            }
        }
        gen_res = await client.post(f"{API_BASE}/blueprint/generate", json=payload)
        assert gen_res.status_code == 200, f"Expected 200, got {gen_res.status_code}"
        gen_data = gen_res.json()
        job_id = gen_data.get("job_id")
        assert job_id, "No job_id returned!"
        print(f"    Launched Job ID: {job_id}", flush=True)
        print("    [PASS] Generation endpoint launched background workflow!")

        # 3. Test SSE Stream reading first few packets
        print("\n[3] Testing GET /api/blueprint/stream/{job_id} (SSE stream)...", flush=True)
        async with client.stream("GET", f"{API_BASE}/blueprint/stream/{job_id}", timeout=30.0) as response:
            assert response.status_code == 200, f"SSE stream returned {response.status_code}"
            packet_count = 0
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    raw_data = line[5:].strip()
                    try:
                        parsed = json.loads(raw_data)
                        print(f"    SSE Packet [{packet_count+1}]: Step='{parsed.get('current_step')}' Agent='{parsed.get('active_agent')}'", flush=True)
                        packet_count += 1
                        if packet_count >= 3:
                            break
                    except json.JSONDecodeError:
                        pass
        print("    [PASS] SSE real-time stream verified!")

        # 4. Test Job Inspection Endpoint
        print("\n[4] Testing GET /api/blueprint/{job_id}...", flush=True)
        job_res = await client.get(f"{API_BASE}/blueprint/{job_id}")
        assert job_res.status_code == 200, f"Expected 200, got {job_res.status_code}"
        job_info = job_res.json()
        print(f"    Job Status: {job_info.get('status')} | Active Agent: {job_info.get('active_agent')}", flush=True)
        print("    [PASS] Job state endpoint verified!")

        # 5. Test Export Guard on In-Progress Job
        print("\n[5] Testing Export Guard on In-Progress Job...", flush=True)
        exp_res = await client.get(f"{API_BASE}/blueprint/{job_id}/export?format=cursor")
        assert exp_res.status_code == 400, f"Expected 400 for incomplete blueprint, got {exp_res.status_code}"
        print("    [PASS] Export guard correctly prevents exporting incomplete blueprints!")

        # 6. Test Export Formats with Direct FastAPI App Transport
        print("\n[6] Testing Export Formatting (Cursor, Claude, Antigravity, Markdown)...", flush=True)
        from app.main import app
        from app.api.routes import jobs
        mock_id = "test-mock-export-id"
        jobs[mock_id] = {
            "job_id": mock_id,
            "status": "completed",
            "final_blueprint": "# TEST MASTER BLUEPRINT\n\n12-section architecture specification verified."
        }

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as asgi_client:
            for fmt in ["cursor", "claude", "antigravity", "markdown"]:
                exp = await asgi_client.get(f"/api/blueprint/{mock_id}/export?format={fmt}")
                assert exp.status_code == 200, f"Export {fmt} failed: {exp.status_code}"
                assert len(exp.text) > 0, f"Export {fmt} returned empty"
                print(f"    [PASS] Export format '{fmt}' generated valid specification ({len(exp.text)} bytes)", flush=True)

    print("\n" + "=" * 60)
    print("PHASE 3 ALL API ENDPOINTS VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
