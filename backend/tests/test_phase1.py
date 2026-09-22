import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.llm_provider import llm_provider
from app.services.search_service import search_service

async def main():
    print("=" * 60)
    print("PHASE 1 REAL-TIME INTEGRATION TEST")
    print("=" * 60)

    # 1. Test Provider Status
    status = llm_provider.get_status()
    print(f"\n[1] LLM Provider Initialized Status: {status}", flush=True)

    # 2. Test Live DuckDuckGo Search
    print("\n[2] Testing Live DuckDuckGo Web Search...", flush=True)
    search_query = "AI prompt builder IDE developer tools"
    results = await search_service.search(search_query, max_results=2)
    print(f"    Found {len(results)} search results for: '{search_query}'", flush=True)
    for r in results:
        print(f"    - Title: {r['title'][:60]}...", flush=True)
        print(f"      URL: {r['url']}", flush=True)
        print(f"      Snippet: {r['snippet'][:100]}...\n", flush=True)
    assert len(results) > 0, "DuckDuckGo search returned 0 results!"
    print("    [PASS] DuckDuckGo search is working 100% on live web!", flush=True)

    # 3. Test LLM Generation with live fallback
    print("\n[3] Testing LLM Generation...", flush=True)
    test_prompt = "Reply with exactly 5 words confirming you are ready to architect software."
    response = await llm_provider.generate(
        prompt=test_prompt,
        system_prompt="You are a senior enterprise systems architect. Follow constraints precisely."
    )
    print(f"    Model Response: '{response.strip()}'", flush=True)
    assert len(response.strip()) > 0, "LLM returned empty response!"
    print("    [PASS] LLM Provider generation succeeded in real-time!", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("PHASE 1 ALL TESTS PASSED SUCCESSFULLY!", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
