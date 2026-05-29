"""
新闻聚合Bot — 主工作流入口
内置3个工作流，通过 workflow 参数路由：
- tech_news: Hacker News + GitHub Trending + HuggingFace Papers
- finance_news: 华尔街见闻 + 36氪快讯
- social_news: 微博热搜 + V2EX热门
"""
import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from graphs.state import (
    GlobalState, GraphInput, GraphOutput,
    DispatchInput, DispatchOutput,
)
from graphs.nodes.hn_node import hn_node
from graphs.nodes.github_node import github_node
from graphs.nodes.hf_node import hf_node
from graphs.nodes.merge_tech_node import merge_tech_node
from graphs.nodes.wallstreet_node import wallstreet_node
from graphs.nodes.kr36_node import kr36_node
from graphs.nodes.merge_finance_node import merge_finance_node
from graphs.nodes.weibo_node import weibo_node
from graphs.nodes.v2ex_node import v2ex_node
from graphs.nodes.merge_social_node import merge_social_node

logger = logging.getLogger(__name__)


# ============================================================
# 调度节点
# ============================================================
def dispatch_node(
    state: DispatchInput,
    config: RunnableConfig,
) -> DispatchOutput:
    """
    title: 工作流调度
    desc: 根据 workflow 字段值（tech_news/finance_news/social_news）路由到对应的新闻抓取分支
    integrations: 无
    """
    logger.info("调度到工作流: %s", state.workflow)
    return DispatchOutput(placeholder="dispatched")


def dispatch_router(state: GlobalState) -> Literal["tech_news", "finance_news", "social_news"]:
    """条件路由：根据 workflow 字段值选择子工作流"""
    return state.workflow


# ============================================================
# 主图编排（包含所有工作流节点，通过条件路由切换）
# ============================================================
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 调度节点
builder.add_node("dispatch_node", dispatch_node)

# 科技新闻节点
builder.add_node("hn_node", hn_node)
builder.add_node("github_node", github_node)
builder.add_node("hf_node", hf_node)
builder.add_node("merge_tech_node", merge_tech_node)

# 财经新闻节点
builder.add_node("wallstreet_node", wallstreet_node)
builder.add_node("kr36_node", kr36_node)
builder.add_node("merge_finance_node", merge_finance_node)

# 社会热点节点
builder.add_node("weibo_node", weibo_node)
builder.add_node("v2ex_node", v2ex_node)
builder.add_node("merge_social_node", merge_social_node)

# 设置入口点
builder.set_entry_point("dispatch_node")

# 条件路由 → 各工作流的起始节点
builder.add_conditional_edges(
    "dispatch_node",
    dispatch_router,
    {
        "tech_news": "hn_node",
        "finance_news": "wallstreet_node",
        "social_news": "weibo_node",
    },
)

# ---------- 科技新闻分支（三路并行） ----------
builder.add_edge("hn_node", "github_node")
builder.add_edge("hn_node", "hf_node")
builder.add_edge(["github_node", "hf_node"], "merge_tech_node")
builder.add_edge("merge_tech_node", END)

# ---------- 财经新闻分支（两路并行） ----------
builder.add_edge("wallstreet_node", "kr36_node")
builder.add_edge("kr36_node", "merge_finance_node")
builder.add_edge("merge_finance_node", END)

# ---------- 社会热点分支（两路并行） ----------
builder.add_edge("weibo_node", "v2ex_node")
builder.add_edge("v2ex_node", "merge_social_node")
builder.add_edge("merge_social_node", END)

# 编译主图
main_graph = builder.compile()