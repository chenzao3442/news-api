"""
微博热搜 HTTP 请求节点
API：weibo.com/ajax/side/hotSearch
被拦截则返回空（国内API需要cookie）
"""
import json
import logging
import requests
from langchain_core.runnables import RunnableConfig
from graphs.state import WeiboNodeInput, WeiboNodeOutput

logger = logging.getLogger(__name__)


def weibo_node(
    state: WeiboNodeInput,
    config: RunnableConfig,
) -> WeiboNodeOutput:
    """
    title: 微博热搜抓取
    desc: 从微博 API 抓取实时热搜，若无 cookie 可能被拦截，则返回空数据
    integrations: 无
    """
    url = "https://weibo.com/ajax/side/hotSearch"
    result_text = ""

    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://weibo.com/",
        }, allow_redirects=True)
        if resp.status_code == 200 and "realtime" in resp.text:
            result_text = resp.text
            logger.info("微博热搜 API 请求成功")
        else:
            result_text = json.dumps({"data": {"realtime": []}})
            logger.warning("微博热搜返回 %d，可能被拦截", resp.status_code)
    except Exception as e:
        result_text = json.dumps({"data": {"realtime": []}})
        logger.warning("微博热搜请求失败: %s", str(e))

    if not result_text:
        result_text = json.dumps({"data": {"realtime": []}})

    return WeiboNodeOutput(weibo_result=result_text)