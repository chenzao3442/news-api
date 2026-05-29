"""
HuggingFace Daily Papers HTTP 请求节点
API：huggingface.co/api/daily_papers
"""
import json
import logging
import requests
from langchain_core.runnables import RunnableConfig
from graphs.state import HFNodeInput, HFNodeOutput

logger = logging.getLogger(__name__)


def hf_node(
    state: HFNodeInput,
    config: RunnableConfig,
) -> HFNodeOutput:
    """
    title: HuggingFace Papers 抓取
    desc: 从 HuggingFace Daily Papers API 抓取每日热门论文
    integrations: 无
    """
    url = "https://huggingface.co/api/daily_papers?limit=10"
    result_text = ""

    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"
        })
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                result_text = resp.text
                logger.info("HuggingFace API 请求成功，获取到 %d 篇论文", len(data))
            else:
                result_text = json.dumps([])
                logger.warning("HuggingFace 返回空数据")
        else:
            result_text = json.dumps([])
            logger.warning("HuggingFace API 返回 %d", resp.status_code)
    except Exception as e:
        result_text = json.dumps([])
        logger.warning("HuggingFace API 请求失败: %s", str(e))

    if not result_text:
        result_text = json.dumps([])

    return HFNodeOutput(hf_result=result_text)