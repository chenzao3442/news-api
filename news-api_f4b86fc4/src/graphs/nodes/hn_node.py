"""
Hacker News HTTP 请求节点
主API：hn.algolia.com
备选RSS：hnrss.org/frontpage
"""
import json
import logging
import requests
from typing import Optional
from langchain_core.runnables import RunnableConfig
from graphs.state import HNNodeInput, HNNodeOutput

logger = logging.getLogger(__name__)

# RSS 简易解析
def _parse_rss_items(xml_text: str) -> list:
    """从 RSS XML 中提取 item 列表"""
    items = []
    # 提取 <item>...</item> 块
    import re
    item_pattern = re.compile(r'<item>([\s\S]*?)</item>')
    for match in item_pattern.finditer(xml_text):
        block = match.group(1)
        title_match = re.search(r'<title>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</title>', block)
        title = (title_match.group(1) or title_match.group(2) or "") if title_match else ""
        link_match = re.search(r'<link>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</link>', block)
        url = (link_match.group(1) or link_match.group(2) or "") if link_match else ""
        items.append({"title": title, "url": url})
    return items


def hn_node(
    state: HNNodeInput,
    config: RunnableConfig,
) -> HNNodeOutput:
    """
    title: Hacker News 抓取
    desc: 从 Hacker News API 抓取热门文章，API 失败时自动降级到 RSS 源
    integrations: 无
    """
    # --- 主 API 请求 ---
    primary_url = "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=15"
    fallback_url = "https://hnrss.org/frontpage"
    result_text = ""
    used_fallback = False

    try:
        resp = requests.get(primary_url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"
        })
        if resp.status_code == 200:
            data = resp.json()
            if data.get("hits") and len(data["hits"]) > 0:
                result_text = resp.text
                logger.info("Hacker News API 请求成功，获取到 %d 条", len(data["hits"]))
            else:
                used_fallback = True
        else:
            used_fallback = True
    except Exception as e:
        logger.warning("Hacker News API 请求失败: %s，降级到 RSS", str(e))
        used_fallback = True

    # --- 备选 RSS ---
    if used_fallback:
        try:
            rss_resp = requests.get(fallback_url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"
            })
            if rss_resp.status_code == 200:
                rss_items = _parse_rss_items(rss_resp.text)
                # 将 RSS 结果包装成与 API 一致的 JSON 结构
                wrapped = {"hits": []}
                for item in rss_items[:15]:
                    wrapped["hits"].append({
                        "title": item["title"],
                        "url": item["url"],
                        "objectID": "",
                        "points": 0
                    })
                result_text = json.dumps(wrapped)
                logger.info("Hacker News RSS 降级成功，获取到 %d 条", len(rss_items))
            else:
                result_text = json.dumps({"hits": []})
                logger.warning("Hacker News RSS 也失败了: %d", rss_resp.status_code)
        except Exception as e:
            result_text = json.dumps({"hits": []})
            logger.warning("Hacker News RSS 请求异常: %s", str(e))

    if not result_text:
        result_text = json.dumps({"hits": []})

    return HNNodeOutput(hn_result=result_text)