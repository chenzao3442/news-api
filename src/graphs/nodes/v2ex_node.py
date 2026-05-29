"""
V2EX 热门 HTTP 请求节点
主API：v2ex.com/api/topics/hot.json
备选RSS：v2ex.com/index.xml
"""
import json
import logging
import re
import requests
from langchain_core.runnables import RunnableConfig
from graphs.state import V2exNodeInput, V2exNodeOutput

logger = logging.getLogger(__name__)


def _parse_v2ex_rss(xml_text: str) -> list:
    """从 V2EX RSS 中提取主题列表"""
    items = []
    item_pattern = re.compile(r'<item>([\s\S]*?)</item>')
    for match in item_pattern.finditer(xml_text):
        block = match.group(1)
        title_match = re.search(r'<title>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</title>', block)
        title = (title_match.group(1) or title_match.group(2) or "") if title_match else ""
        link_match = re.search(r'<link>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</link>', block)
        url = (link_match.group(1) or link_match.group(2) or "") if link_match else ""
        # V2EX RSS 格式: <v2ex:replies> 或 <comments>
        replies_match = re.search(r'<v2ex:replies>(.*?)</v2ex:replies>', block)
        replies = int(replies_match.group(1)) if replies_match else 0
        items.append({"title": title, "url": url, "replies": replies})
    return items


def v2ex_node(
    state: V2exNodeInput,
    config: RunnableConfig,
) -> V2exNodeOutput:
    """
    title: V2EX 热门抓取
    desc: 从 V2EX API 抓取热门主题，API 失败时降级到 RSS
    integrations: 无
    """
    primary_url = "https://www.v2ex.com/api/topics/hot.json"
    fallback_url = "https://www.v2ex.com/index.xml"
    result_text = ""
    used_fallback = False

    try:
        resp = requests.get(primary_url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"
        })
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                result_text = resp.text
                logger.info("V2EX API 请求成功，获取到 %d 条", len(data))
            else:
                used_fallback = True
        else:
            used_fallback = True
            logger.warning("V2EX API 返回 %d", resp.status_code)
    except Exception as e:
        logger.warning("V2EX API 请求失败: %s，降级到 RSS", str(e))
        used_fallback = True

    # --- 备选 RSS ---
    if used_fallback:
        try:
            rss_resp = requests.get(fallback_url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"
            })
            if rss_resp.status_code == 200:
                rss_items = _parse_v2ex_rss(rss_resp.text)
                wrapped = []
                for item in rss_items[:15]:
                    wrapped.append({
                        "title": item["title"],
                        "url": item["url"],
                        "replies": item["replies"],
                        "created": ""
                    })
                result_text = json.dumps(wrapped)
                logger.info("V2EX RSS 降级成功，获取到 %d 条", len(rss_items))
            else:
                result_text = json.dumps([])
                logger.warning("V2EX RSS 也失败了: %d", rss_resp.status_code)
        except Exception as e:
            result_text = json.dumps([])
            logger.warning("V2EX RSS 请求异常: %s", str(e))

    if not result_text:
        result_text = json.dumps([])

    return V2exNodeOutput(v2ex_result=result_text)