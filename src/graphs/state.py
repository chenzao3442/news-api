"""
新闻聚合Bot — 全局状态与节点出入参定义
包含3个工作流：科技新闻、财经新闻、社会热点
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================
# 全局状态（LangGraph 自动合并节点输出）
# ============================================================
class GlobalState(BaseModel):
    """全局状态：所有工作流的共享状态"""
    # 工作流选择
    workflow: str = Field(default="", description="工作流类型: tech_news / finance_news / social_news")

    # 科技新闻 - HTTP 请求结果
    hn_result: str = Field(default="", description="Hacker News API 返回结果")
    github_result: str = Field(default="", description="GitHub Trending API 返回结果")
    hf_result: str = Field(default="", description="HuggingFace Papers API 返回结果")

    # 财经新闻 - HTTP 请求结果
    wallstreet_result: str = Field(default="", description="华尔街见闻 API 返回结果")
    kr36_result: str = Field(default="", description="36氪 API 返回结果")

    # 社会热点 - HTTP 请求结果
    weibo_result: str = Field(default="", description="微博热搜 API 返回结果")
    v2ex_result: str = Field(default="", description="V2EX API 返回结果")

    # 统一输出
    news_items: List[dict] = Field(default=[], description="合并后的新闻条目列表")


# ============================================================
# 图（工作流）的输入/输出
# ============================================================
class GraphInput(BaseModel):
    """工作流输入"""
    workflow: str = Field(..., description="工作流类型: tech_news / finance_news / social_news")


class GraphOutput(BaseModel):
    """工作流输出"""
    news_items: List[dict] = Field(..., description="新闻条目列表，每项包含 source/title/url/heat/time")


# ============================================================
# 调度节点（dispatch）的出入参
# ============================================================
class DispatchInput(BaseModel):
    """调度节点输入"""
    workflow: str = Field(..., description="工作流类型: tech_news / finance_news / social_news")


class DispatchOutput(BaseModel):
    """调度节点输出"""
    placeholder: str = Field(default="", description="占位字段，用于 LangGraph 状态更新")


# ============================================================
# 科技新闻 - 节点出入参
# ============================================================
class HNNodeInput(BaseModel):
    """Hacker News HTTP 请求节点输入"""
    pass


class HNNodeOutput(BaseModel):
    """Hacker News HTTP 请求节点输出"""
    hn_result: str = Field(..., description="Hacker News API 返回的 JSON 字符串")


class GitHubNodeInput(BaseModel):
    """GitHub Trending HTTP 请求节点输入"""
    pass


class GitHubNodeOutput(BaseModel):
    """GitHub Trending HTTP 请求节点输出"""
    github_result: str = Field(..., description="GitHub API 返回的 JSON 字符串")


class HFNodeInput(BaseModel):
    """HuggingFace Papers HTTP 请求节点输入"""
    pass


class HFNodeOutput(BaseModel):
    """HuggingFace Papers HTTP 请求节点输出"""
    hf_result: str = Field(..., description="HuggingFace API 返回的 JSON 字符串")


class MergeTechInput(BaseModel):
    """科技新闻合并节点输入"""
    hn_result: str = Field(..., description="Hacker News 返回结果")
    github_result: str = Field(..., description="GitHub 返回结果")
    hf_result: str = Field(..., description="HuggingFace 返回结果")


class MergeTechOutput(BaseModel):
    """科技新闻合并节点输出"""
    news_items: List[dict] = Field(..., description="合并后的科技新闻列表")


# ============================================================
# 财经新闻 - 节点出入参
# ============================================================
class WallstreetNodeInput(BaseModel):
    """华尔街见闻 HTTP 请求节点输入"""
    pass


class WallstreetNodeOutput(BaseModel):
    """华尔街见闻 HTTP 请求节点输出"""
    wallstreet_result: str = Field(..., description="华尔街见闻 API 返回结果")


class Kr36NodeInput(BaseModel):
    """36氪 HTTP 请求节点输入"""
    pass


class Kr36NodeOutput(BaseModel):
    """36氪 HTTP 请求节点输出"""
    kr36_result: str = Field(..., description="36氪 API 返回结果")


class MergeFinanceInput(BaseModel):
    """财经新闻合并节点输入"""
    wallstreet_result: str = Field(..., description="华尔街见闻返回结果")
    kr36_result: str = Field(..., description="36氪返回结果")


class MergeFinanceOutput(BaseModel):
    """财经新闻合并节点输出"""
    news_items: List[dict] = Field(..., description="合并后的财经新闻列表")


# ============================================================
# 社会热点 - 节点出入参
# ============================================================
class WeiboNodeInput(BaseModel):
    """微博热搜 HTTP 请求节点输入"""
    pass


class WeiboNodeOutput(BaseModel):
    """微博热搜 HTTP 请求节点输出"""
    weibo_result: str = Field(..., description="微博热搜 API 返回结果")


class V2exNodeInput(BaseModel):
    """V2EX HTTP 请求节点输入"""
    pass


class V2exNodeOutput(BaseModel):
    """V2EX HTTP 请求节点输出"""
    v2ex_result: str = Field(..., description="V2EX API 返回结果")


class MergeSocialInput(BaseModel):
    """社会热点合并节点输入"""
    weibo_result: str = Field(..., description="微博热搜返回结果")
    v2ex_result: str = Field(..., description="V2EX返回结果")


class MergeSocialOutput(BaseModel):
    """社会热点合并节点输出"""
    news_items: List[dict] = Field(..., description="合并后的社会热点列表")


# ============================================================
# 子图包装节点出入参（主图调度 → 子图）
# ============================================================
class SubgraphWrapperInput(BaseModel):
    """子图包装器输入（所有子工作流通用）"""
    workflow: str = Field(..., description="工作流类型")


class SubgraphWrapperOutput(BaseModel):
    """子图包装器输出（所有子工作流通用）"""
    news_items: List[dict] = Field(..., description="子工作流输出的新闻条目列表")


class TechNewsSubgraphOutput(BaseModel):
    """科技新闻子图输出"""
    news_items: List[dict] = Field(..., description="科技新闻条目列表")


class FinanceNewsSubgraphOutput(BaseModel):
    """财经新闻子图输出"""
    news_items: List[dict] = Field(..., description="财经新闻条目列表")


class SocialNewsSubgraphOutput(BaseModel):
    """社会热点子图输出"""
    news_items: List[dict] = Field(..., description="社会热点条目列表")