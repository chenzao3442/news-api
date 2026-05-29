"""
科技新闻合并节点
将 Hacker News、GitHub Trending、HuggingFace Papers 合并为统一格式
"""
import json
import logging
from typing import List, Any
from langchain_core.runnables import RunnableConfig
from graphs.state import MergeTechInput, MergeTechOutput

logger = logging.getLogger(__name__)


def _safe_json_parse(text: str) -> Any:
    """安全解析 JSON 字符串"""
    if not text or not text.strip():
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def merge_tech_node(
    state: MergeTechInput,
    config: RunnableConfig,
) -> MergeTechOutput:
    """
    title: 科技新闻合并
    desc: 将 Hacker News、GitHub Trending、HuggingFace Papers 三个来源的数据合并为统一格式的 news_items 数组
    integrations: 无
    """
    items: List[dict] = []

    # ===== Hacker News =====
    hn_data = _safe_json_parse(state.hn_result)
    if hn_data and isinstance(hn_data, dict):
        hits = hn_data.get("hits")
        if isinstance(hits, list):
            for h in hits[:15]:
                items.append({
                    "source": "Hacker News",
                    "title": h.get("title") or "",
                    "url": h.get("url") or (
                        f"https://news.ycombinator.com/item?id={h.get('objectID', '')}"
                    ),
                    "hn_url": f"https://news.ycombinator.com/item?id={h.get('objectID', '')}",
                    "heat": f"{h.get('points', 0)} points",
                    "time": "Today"
                })

    # ===== GitHub Trending =====
    gh_data = _safe_json_parse(state.github_result)
    if gh_data and isinstance(gh_data, dict):
        gh_items = gh_data.get("items")
        if isinstance(gh_items, list):
            for r in gh_items[:15]:
                items.append({
                    "source": "GitHub Trending",
                    "title": f"{r.get('full_name', '')} - {r.get('description', '')}",
                    "url": r.get("html_url") or "",
                    "heat": f"{r.get('stargazers_count', 0)} stars",
                    "time": "Today",
                    "lang": r.get("language") or ""
                })

    # ===== HuggingFace Papers =====
    hf_data = _safe_json_parse(state.hf_result)
    if hf_data and isinstance(hf_data, list):
        for p in hf_data[:10]:
            paper = p.get("paper") or {}
            items.append({
                "source": "HuggingFace Papers",
                "title": paper.get("title") or "",
                "url": paper.get("url") or "",
                "heat": f"+{paper.get('upvotes', 0)} upvotes",
                "time": "Today"
            })

    logger.info("科技新闻合并完成，共 %d 条", len(items))
    return MergeTechOutput(news_items=items)