"""
GitHub Trending HTTP 请求节点
主API：api.github.com/search/repositories
备选RSS：mshibanami.github.io/GitHubTrendingRSS
"""
import json
import logging
import re
from datetime import datetime, timedelta
import requests
from langchain_core.runnables import RunnableConfig
from graphs.state import GitHubNodeInput, GitHubNodeOutput

logger = logging.getLogger(__name__)


def _parse_github_rss(xml_text: str) -> list:
    """从 GitHub Trending RSS 中提取项目列表"""
    items = []
    item_pattern = re.compile(r'<item>([\s\S]*?)</item>')
    for match in item_pattern.finditer(xml_text):
        block = match.group(1)
        title_match = re.search(r'<title>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</title>', block)
        title = (title_match.group(1) or title_match.group(2) or "") if title_match else ""
        link_match = re.search(r'<link>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</link>', block)
        url = (link_match.group(1) or link_match.group(2) or "") if link_match else ""
        desc_match = re.search(r'<description>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</description>', block)
        desc = (desc_match.group(1) or desc_match.group(2) or "") if desc_match else ""
        items.append({"full_name": title, "html_url": url, "description": desc, "stargazers_count": 0, "language": ""})
    return items


def github_node(
    state: GitHubNodeInput,
    config: RunnableConfig,
) -> GitHubNodeOutput:
    """
    title: GitHub Trending 抓取
    desc: 从 GitHub Search API 抓取热门开源项目，API 失败时降级到 RSS
    integrations: 无
    """
    # 动态计算日期（7天前）
    date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    primary_url = (
        f"https://api.github.com/search/repositories"
        f"?q=stars:>500+pushed:>={date_from}"
        f"&sort=stars&order=desc&per_page=15"
    )
    fallback_url = "https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml"
    result_text = ""
    used_fallback = False

    try:
        resp = requests.get(primary_url, timeout=10, headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "NewsBot/1.0"
        })
        if resp.status_code == 200:
            data = resp.json()
            if data.get("items") and len(data["items"]) > 0:
                result_text = resp.text
                logger.info("GitHub API 请求成功，获取到 %d 条", len(data["items"]))
            else:
                used_fallback = True
        else:
            used_fallback = True
            logger.warning("GitHub API 返回 %d: %s", resp.status_code, resp.text[:200])
    except Exception as e:
        logger.warning("GitHub API 请求失败: %s，降级到 RSS", str(e))
        used_fallback = True

    # --- 备选 RSS ---
    if used_fallback:
        try:
            rss_resp = requests.get(fallback_url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"
            })
            if rss_resp.status_code == 200:
                rss_items = _parse_github_rss(rss_resp.text)
                wrapped = {"items": []}
                for item in rss_items[:15]:
                    wrapped["items"].append({
                        "full_name": item["full_name"],
                        "html_url": item["html_url"],
                        "description": item["description"],
                        "stargazers_count": 0,
                        "language": ""
                    })
                result_text = json.dumps(wrapped)
                logger.info("GitHub RSS 降级成功，获取到 %d 条", len(rss_items))
            else:
                result_text = json.dumps({"items": []})
                logger.warning("GitHub RSS 也失败了: %d", rss_resp.status_code)
        except Exception as e:
            result_text = json.dumps({"items": []})
            logger.warning("GitHub RSS 请求异常: %s", str(e))

    if not result_text:
        result_text = json.dumps({"items": []})

    return GitHubNodeOutput(github_result=result_text)