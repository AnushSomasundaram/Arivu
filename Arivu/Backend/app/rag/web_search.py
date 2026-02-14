"""Web search integration using LangChain's Tavily tool.

To use web search, instantiate TavilySearchResults directly from LangChain:

Example:
    from langchain_community.tools.tavily_search import TavilySearchResults
    from app.core.config import settings

    tool = TavilySearchResults(
        max_results=5,
        api_key=settings.tavily_api_key,
        search_depth="advanced"
    )
    results = tool.invoke("your search query")

For more information, see:
https://python.langchain.com/docs/integrations/tools/tavily_search
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)
