"""
Search Tools
=============

Reusable search utilities that wrap third-party retrieval services
(Tavily web search and Wikipedia loader) as LangChain tools.
"""

from __future__ import annotations

from langchain_community.document_loaders import WikipediaLoader
from langchain_tavily import TavilySearch

# ---------------------------------------------------------------------------
# Tavily Web Search
# ---------------------------------------------------------------------------

# Limit to 3 results to keep context length manageable and responses fast.
tavily_search: TavilySearch = TavilySearch(max_results=3)

# ---------------------------------------------------------------------------
# Wikipedia Loader (used as a tool inside the interview sub-graph)
# ---------------------------------------------------------------------------

# WikipediaLoader is instantiated lazily inside graph nodes because it
# requires a search query and performs the actual retrieval on invoke.
# We expose the class here so nodes can construct it with the desired
# query and top_k settings.
__all__ = [
    "tavily_search",
    "WikipediaLoader",
]
