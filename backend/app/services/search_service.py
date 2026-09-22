import asyncio
import logging
from typing import List, Dict, Any
from ddgs import DDGS

logger = logging.getLogger(__name__)

class WebSearchService:
    """Free web search service powered by DDGS (DuckDuckGo, 0 API key required)."""

    def __init__(self, max_results_per_query: int = 5):
        self.max_results_per_query = max_results_per_query

    async def search(self, query: str, max_results: int = None) -> List[Dict[str, str]]:
        """Run an async web search for a query and return formatted snippets."""
        limit = max_results or self.max_results_per_query
        
        def _sync_search():
            results = []
            try:
                with DDGS() as ddgs:
                    raw = list(ddgs.text(query, max_results=limit))
                    for item in raw:
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("href", ""),
                            "snippet": item.get("body", "")
                        })
            except Exception as e:
                logger.warning(f"DDGS search error for '{query}': {e}")
            return results

        return await asyncio.to_thread(_sync_search)

    async def run_structured_protocol(self, product_idea: str) -> Dict[str, Any]:
        """
        Runs the full 5-category research protocol:
        1. Market sizing & growth
        2. Competitor products & weaknesses
        3. Audience & Reddit discussions
        4. Technical APIs & libraries
        5. Regulatory & compliance
        """
        queries = {
            "market_sizing": [
                f"{product_idea} market size TAM growth rate trends",
                f"{product_idea} industry statistics report"
            ],
            "competitors": [
                f"{product_idea} top competitors pricing alternatives",
                f"{product_idea} product hunt competitor complaints"
            ],
            "audience_frustrations": [
                f"{product_idea} site:reddit.com frustrations pain points",
                f"{product_idea} user complaints what sucks about current tools"
            ],
            "technical_stack": [
                f"{product_idea} github open source architecture API",
                f"{product_idea} best tech stack database"
            ],
            "regulatory": [
                f"{product_idea} compliance legal requirements data privacy",
                f"{product_idea} regulations GDPR security standards"
            ]
        }

        research_results = {}
        for category, query_list in queries.items():
            category_results = []
            for q in query_list:
                snippets = await self.search(q, max_results=3)
                category_results.extend(snippets)
            research_results[category] = category_results

        return research_results

search_service = WebSearchService()
