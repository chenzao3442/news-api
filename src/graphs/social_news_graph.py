"""
社会热点工作流子图
抓取微博热搜、V2EX热门并合并（并行）
"""
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from graphs.state import (
    GlobalState, GraphInput, GraphOutput,
)
from graphs.nodes.weibo_node import weibo_node
from graphs.nodes.v2ex_node import v2ex_node
from graphs.nodes.merge_social_node import merge_social_node


# 并行启动器节点
def social_starter(
    state: GraphInput,
    config: RunnableConfig,
) -> dict:
    """并行启动器：触发两个 HTTP 请求并行执行"""
    return {}


def create_social_news_graph() -> StateGraph:
    """创建社会热点工作流（并行架构）"""
    builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

    builder.add_node("social_starter", social_starter)
    builder.add_node("weibo_node", weibo_node)
    builder.add_node("v2ex_node", v2ex_node)
    builder.add_node("merge_social_node", merge_social_node)

    # 入口 → starter（并行扇出）
    builder.set_entry_point("social_starter")
    builder.add_edge("social_starter", "weibo_node")
    builder.add_edge("social_starter", "v2ex_node")

    # 并行分支汇聚到合并节点
    builder.add_edge(["weibo_node", "v2ex_node"], "merge_social_node")

    # 合并节点 → 结束
    builder.add_edge("merge_social_node", END)

    return builder


# 快捷实例化
social_news_graph = create_social_news_graph().compile()