"""
财经新闻合并节点
将华尔街见闻、36氪快讯合并为统一格式
"""
import json
import logging
from typing import List, Any
from langchain_core.runnables import RunnableConfig
from graphs.state import MergeFinanceInput, MergeFinanceOutput

logger = logging.getLogger(__name__)


def _safe_json_parse(text: str) -> Any:
    """安全解析 JSON 字符串"""
    if not text or not text.strip():
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def merge_finance_node(
    state: MergeFinanceInput,
    config: RunnableConfig,
) -> MergeFinanceOutput:
    """
    title: 财经新闻合并
    desc: 将华尔街见闻、36氪快讯两个来源的数据合并为统一格式的 news_items 数组
    integrations: 无
    """
    items: List[dict] = []

    # ===== 华尔街见闻 =====
    ws_data = _safe_json_parse(state.wallstreet_result)
    if ws_data and isinstance(ws_data, dict):
        ws_items = (ws_data.get("data", {}).get("items") or
                    ws_data.get("data", {}).get("newsflashes") or [])
        if isinstance(ws_items, list):
            for i in ws_items[:15]:
                items.append({
                    "source": "华尔街见闻",
                    "title": i.get("title_text") or i.get("title") or "",
                    "url": (
                        f"https://wallstreetcn.com/news/{i.get('uri', '')}"
                        if i.get("uri") else ""
                    ),
                    "time": i.get("display_time") or "",
                    "heat": ""
                })

    # ===== 36氪 =====
    kr_data = _safe_json_parse(state.kr36_result)
    if kr_data and isinstance(kr_data, dict):
        kr_items = (kr_data.get("data", {}).get("items") or
                    kr_data.get("data", {}).get("newsflashes") or [])
        if isinstance(kr_items, list):
            for i in kr_items[:15]:
                entity = i.get("entity") or {}
                items.append({
                    "source": "36氪",
                    "title": i.get("title") or entity.get("title") or "",
                    "url": i.get("url") or entity.get("url") or "",
                    "time": i.get("published_at") or entity.get("published_at") or "",
                    "heat": ""
                })

    logger.info("财经新闻合并完成，共 %d 条", len(items))
    return MergeFinanceOutput(news_items=items)