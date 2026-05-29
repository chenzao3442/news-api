"""
社会热点合并节点
将微博热搜、V2EX热门合并为统一格式
"""
import json
import logging
from typing import List, Any
from urllib.parse import quote
from langchain_core.runnables import RunnableConfig
from graphs.state import MergeSocialInput, MergeSocialOutput

logger = logging.getLogger(__name__)


def _safe_json_parse(text: str) -> Any:
    """安全解析 JSON 字符串"""
    if not text or not text.strip():
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def merge_social_node(
    state: MergeSocialInput,
    config: RunnableConfig,
) -> MergeSocialOutput:
    """
    title: 社会热点合并
    desc: 将微博热搜、V2EX热门两个来源的数据合并为统一格式的 news_items 数组
    integrations: 无
    """
    items: List[dict] = []

    # ===== 微博热搜 =====
    wb_data = _safe_json_parse(state.weibo_result)
    if wb_data and isinstance(wb_data, dict):
        wb_items = wb_data.get("data", {}).get("realtime") or []
        if isinstance(wb_items, list):
            for i in wb_items[:15]:
                word = i.get("word") or ""
                items.append({
                    "source": "微博热搜",
                    "title": word,
                    "url": (
                        f"https://s.weibo.com/weibo?q={quote(word)}"
                        if word else ""
                    ),
                    "heat": f"{i.get('num', 0)}热度",
                    "time": "Hot"
                })

    # ===== V2EX =====
    v2_data = _safe_json_parse(state.v2ex_result)
    if v2_data and isinstance(v2_data, list):
        for t in v2_data[:15]:
            created_ts = t.get("created")
            time_str = ""
            if created_ts:
                from datetime import datetime
                time_str = datetime.fromtimestamp(int(created_ts)).strftime("%Y-%m-%d")
            items.append({
                "source": "V2EX",
                "title": t.get("title") or "",
                "url": t.get("url") or "",
                "heat": f"{t.get('replies', 0)} replies",
                "time": time_str
            })

    logger.info("社会热点合并完成，共 %d 条", len(items))
    return MergeSocialOutput(news_items=items)