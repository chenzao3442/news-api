"""
新闻聚合Bot — FastAPI API 服务
为 Coze Bot 提供 3 个 REST API 接口，分别对应 3 个新闻工作流
"""
import logging
import os
import sys
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 确保项目根目录在 Python 路径中（Railway 部署必需）
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from graphs.tech_news_graph import tech_news_graph
from graphs.finance_news_graph import finance_news_graph
from graphs.social_news_graph import social_news_graph

# ============================================================
# 日志配置
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("news_api")

# ============================================================
# API 数据模型
# ============================================================
class NewsItem(BaseModel):
    """单条新闻条目"""
    source: str = Field(..., description="新闻来源")
    title: str = Field(..., description="新闻标题")
    url: str = Field(default="", description="原文链接")
    heat: str = Field(default="", description="热度指标")
    time: str = Field(default="", description="发布时间")


class NewsResponse(BaseModel):
    """API 统一响应格式"""
    success: bool = Field(..., description="是否成功")
    news_items: List[NewsItem] = Field(default=[], description="新闻条目列表")
    total: int = Field(default=0, description="新闻条数")
    message: str = Field(default="", description="提示信息")


# ============================================================
# FastAPI 应用
# ============================================================
app = FastAPI(
    title="新闻聚合 API",
    description="聚合科技新闻、财经新闻、社会热点，统一 JSON 格式输出",
    version="1.0.0",
)

# 允许跨域（coze.cn Bot 调用时需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 健康检查
# ============================================================
@app.get("/api/health", tags=["系统"])
async def health_check():
    """服务健康检查"""
    return {
        "status": "ok",
        "service": "新闻聚合 API",
        "version": "1.0.0",
        "endpoints": {
            "tech_news": "/api/news/tech",
            "finance_news": "/api/news/finance",
            "social_news": "/api/news/social",
        },
    }


# ============================================================
# 新闻接口（3个工作流）
# ============================================================
@app.post("/api/news/tech", response_model=NewsResponse, tags=["新闻"])
async def fetch_tech_news():
    """
    科技新闻聚合
    - 来源: Hacker News, GitHub Trending, HuggingFace Papers
    - 返回统一格式的 news_items 列表
    """
    logger.info("=== 调用科技新闻接口 ===")
    try:
        result = tech_news_graph.invoke({"workflow": "tech_news"})
        items = result.get("news_items", [])
        logger.info("科技新闻获取成功，共 %d 条", len(items))
        return NewsResponse(success=True, news_items=items, total=len(items))
    except Exception as e:
        logger.error("科技新闻接口异常: %s", str(e))
        raise HTTPException(status_code=500, detail=f"科技新闻抓取失败: {str(e)}")


@app.post("/api/news/finance", response_model=NewsResponse, tags=["新闻"])
async def fetch_finance_news():
    """
    财经新闻聚合
    - 来源: 华尔街见闻, 36氪快讯
    - 返回统一格式的 news_items 列表
    """
    logger.info("=== 调用财经新闻接口 ===")
    try:
        result = finance_news_graph.invoke({"workflow": "finance_news"})
        items = result.get("news_items", [])
        logger.info("财经新闻获取成功，共 %d 条", len(items))
        return NewsResponse(success=True, news_items=items, total=len(items))
    except Exception as e:
        logger.error("财经新闻接口异常: %s", str(e))
        raise HTTPException(status_code=500, detail=f"财经新闻抓取失败: {str(e)}")


@app.post("/api/news/social", response_model=NewsResponse, tags=["新闻"])
async def fetch_social_news():
    """
    社会热点聚合
    - 来源: 微博热搜, V2EX热门
    - 返回统一格式的 news_items 列表
    """
    logger.info("=== 调用社会热点接口 ===")
    try:
        result = social_news_graph.invoke({"workflow": "social_news"})
        items = result.get("news_items", [])
        logger.info("社会热点获取成功，共 %d 条", len(items))
        return NewsResponse(success=True, news_items=items, total=len(items))
    except Exception as e:
        logger.error("社会热点接口异常: %s", str(e))
        raise HTTPException(status_code=500, detail=f"社会热点抓取失败: {str(e)}")


# ============================================================
# 启动入口
# ============================================================
if __name__ == "__main__":
    import uvicorn
    # Railway 自动设置 PORT 环境变量，本地开发默认 8000
    port = int(os.getenv("PORT", "8000"))
    logger.info("启动新闻聚合 API 服务，端口: %d", port)
    uvicorn.run(app, host="0.0.0.0", port=port)