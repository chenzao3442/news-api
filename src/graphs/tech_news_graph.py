"""
科技新闻工作流子图
抓取 Hacker News、GitHub Trending、HuggingFace Papers 并合并（三路并行）
"""
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from graphs.state import (
    GlobalState, GraphInput, GraphOutput,
)
from graphs.nodes.hn_node import hn_node
from graphs.nodes.github_node import github_node
from graphs.nodes.hf_node import hf_node
from graphs.nodes.merge_tech_node import merge_tech_node


# 并行启动器节点
def tech_starter(
    state: GraphInput,
    config: RunnableConfig,
) -> dict:
    """并行启动器：触发三个 HTTP 请求并行执行"""
    return {}


def create_tech_news_graph() -> StateGraph:
    """创建科技新闻工作流（三路并行架构）"""
    builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

    # 添加节点
    builder.add_node("tech_starter", tech_starter)
    builder.add_node("hn_node", hn_node)
    builder.add_node("github_node", github_node)
    builder.add_node("hf_node", hf_node)
    builder.add_node("merge_tech_node", merge_tech_node)

    # 入口点 → starter（并行扇出到三个HTTP节点）
    builder.set_entry_point("tech_starter")
    builder.add_edge("tech_starter", "hn_node")
    builder.add_edge("tech_starter", "github_node")
    builder.add_edge("tech_starter", "hf_node")

    # 三个并行分支汇聚到合并节点
    builder.add_edge(["hn_node", "github_node", "hf_node"], "merge_tech_node")

    # 合并节点 → 结束
    builder.add_edge("merge_tech_node", END)

    return builder


# 提供快捷实例化
tech_news_graph = create_tech_news_graph().compile()