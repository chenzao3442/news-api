"""
36氪 HTTP 请求节点
主API：36kr.com/api/newsflash
备选RSS：36kr.com/feed
"""
import json
import logging
import re
import requests
from langchain_core.runnables import RunnableConfig
from graphs.state import Kr36NodeInput, Kr36NodeOutput

logger = logging.getLogger(__name__)


def _parse_36kr_rss(xml_text: str) -> list:
    """从 36氪 RSS 中解析条目"""
    items = []
    item_pattern = re.compile(r'<item>([\s\S]*?)</item>')
    for match in item_pattern.finditer(xml_text):
        block = match.group(1)
        title_match = re.search(r'<title>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</title>', block)
        title = (title_match.group(1) or title_match.group(2) or "") if title_match else ""
        link_match = re.search(r'<link>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</link>', block)
        url = (link_match.group(1) or link_match.group(2) or "") if link_match else ""
        # 尝试提取发布时间
        pubdate_match = re.search(r'<pubDate>(.*?)</pubDate>', block)
        pubdate = pubdate_match.group(1) if pubdate_match else ""
        items.append({"title": title, "url": url, "published_at": pubdate})
    return items


def kr36_node(
    state: Kr36NodeInput,
    config: RunnableConfig,
) -> Kr36NodeOutput:
    """
    title: 36氪快讯抓取
    desc: 从 36氪 API 抓取快讯，API 失败时降级到 RSS
    integrations: 无
    """
    primary_url = "https://36kr.com/api/newsflash"
    fallback_url = "https://36kr.com/feed"
    result_text = ""
    used_fallback = False

    try:
        resp = requests.get(primary_url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://36kr.com/",
        })
        if resp.status_code == 200:
            data = resp.json()
            items = (data.get("data", {}).get("items") or
                     data.get("data", {}).get("newsflashes") or [])
            if len(items) > 0:
                result_text = resp.text
                logger.info("36氪 API 请求成功，获取到 %d 条", len(items))
            else:
                used_fallback = True
        else:
            used_fallback = True
            logger.warning("36氪 API 返回 %d", resp.status_code)
    except Exception as e:
        logger.warning("36氪 API 请求失败: %s，降级到 RSS", str(e))
        used_fallback = True

    # --- 备选 RSS ---
    if used_fallback:
        try:
            rss_resp = requests.get(fallback_url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"
            })
            if rss_resp.status_code == 200:
                rss_items = _parse_36kr_rss(rss_resp.text)
                wrapped = {"data": {"items": []}}
                for item in rss_items[:15]:
                    wrapped["data"]["items"].append({
                        "title": item["title"],
                        "url": item["url"],
                        "published_at": item["published_at"]
                    })
                result_text = json.dumps(wrapped, ensure_ascii=False)
                logger.info("36氪 RSS 降级成功，获取到 %d 条", len(rss_items))
            else:
                result_text = json.dumps({"data": {"items": []}})
                logger.warning("36氪 RSS 也失败了: %d", rss_resp.status_code)
        except Exception as e:
            result_text = json.dumps({"data": {"items": []}})
            logger.warning("36氪 RSS 请求异常: %s", str(e))

    if not result_text:
        result_text = json.dumps({"data": {"items": []}})

    return Kr36NodeOutput(kr36_result=result_text)