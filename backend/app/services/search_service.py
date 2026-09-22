import asyncio
import logging
import re
from typing import List, Dict, Any
from ddgs import DDGS

logger = logging.getLogger(__name__)

class WebSearchService:
    """Fast web search service powered by DDGS (DuckDuckGo, 0 API key required)."""

    def __init__(self, max_results_per_query: int = 3):
        self.max_results_per_query = max_results_per_query

    def _extract_keywords(self, text: str, max_words: int = 4) -> str:
        """Extract clean core keywords from text."""
        words = re.findall(r'\b[A-Za-z0-9_-]+\b', text)
        stop_words = {"a", "an", "the", "and", "or", "for", "with", "that", "this", "into", "in", "on", "to", "is", "are"}
        meaningful = [w for w in words if w.lower() not in stop_words]
        return " ".join(meaningful[:max_words])

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
        Runs the full 5-category research protocol using clean, natural keyword queries.
        """
        keywords = self._extract_keywords(product_idea, max_words=3)
        if not keywords:
            keywords = "software tool SaaS"

        queries = {
            "market_sizing": f"{keywords} industry market size",
            "competitors": f"{keywords} software competitors",
            "audience_frustrations": f"{keywords} user reviews problems",
            "technical_stack": f"{keywords} open source github",
            "regulatory": f"{keywords} compliance regulations",
        }

        def _sync_run_all():
            results = {k: [] for k in queries.keys()}
            try:
                with DDGS(timeout=4) as ddgs:
                    # Single fast multi-result search
                    raw = list(ddgs.text(f"{keywords} software SaaS", max_results=6))
                    categories = list(queries.keys())
                    for idx, item in enumerate(raw):
                        cat = categories[idx % len(categories)]
                        results[cat].append({
                            "title": item.get("title", ""),
                            "url": item.get("href", ""),
                            "snippet": item.get("body", "")
                        })
            except Exception as e:
                logger.warning(f"Fast DDGS search note: {e}")
            return results

        return await asyncio.to_thread(_sync_run_all)

search_service = WebSearchService()
