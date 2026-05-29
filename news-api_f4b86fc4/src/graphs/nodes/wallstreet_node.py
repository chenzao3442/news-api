"""
华尔街见闻 HTTP 请求节点
API：wallstreetcn.com/api/finfo/v2/live-list
被拦截则返回空
"""
import json
import logging
import requests
from langchain_core.runnables import RunnableConfig
from graphs.state import WallstreetNodeInput, WallstreetNodeOutput

logger = logging.getLogger(__name__)


def wallstreet_node(
    state: WallstreetNodeInput,
    config: RunnableConfig,
) -> WallstreetNodeOutput:
    """
    title: 华尔街见闻抓取
    desc: 从华尔街见闻 API 抓取财经快讯，若被拦截则返回空数据
    integrations: 无
    """
    url = "https://wallstreetcn.com/api/finfo/v2/live-list?channel=global-channel&limit=15"
    result_text = ""

    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://wallstreetcn.com/",
            "Accept": "application/json, text/plain, */*",
        })
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, dict):
                result_text = resp.text
                logger.info("华尔街见闻 API 请求成功")
            else:
                result_text = json.dumps({"data": {"items": []}})
                logger.warning("华尔街见闻返回空数据")
        else:
            result_text = json.dumps({"data": {"items": []}})
            logger.warning("华尔街见闻返回 %d，可能被拦截", resp.status_code)
    except Exception as e:
        result_text = json.dumps({"data": {"items": []}})
        logger.warning("华尔街见闻请求失败: %s", str(e))

    if not result_text:
        result_text = json.dumps({"data": {"items": []}})

    return WallstreetNodeOutput(wallstreet_result=result_text)