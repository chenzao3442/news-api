"""
财经新闻工作流子图
抓取华尔街见闻、36氪快讯并合并（并行）
"""
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from graphs.state import (
    GlobalState, GraphInput, GraphOutput,
)
from graphs.nodes.wallstreet_node import wallstreet_node
from graphs.nodes.kr36_node import kr36_node
from graphs.nodes.merge_finance_node import merge_finance_node


# 并行启动器节点
def finance_starter(
    state: GraphInput,
    config: RunnableConfig,
) -> dict:
    """并行启动器：触发两个 HTTP 请求并行执行"""
    return {}


def create_finance_news_graph() -> StateGraph:
    """创建财经新闻工作流（并行架构）"""
    builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

    builder.add_node("finance_starter", finance_starter)
    builder.add_node("wallstreet_node", wallstreet_node)
    builder.add_node("kr36_node", kr36_node)
    builder.add_node("merge_finance_node", merge_finance_node)

    # 入口 → starter（并行扇出）
    builder.set_entry_point("finance_starter")
    builder.add_edge("finance_starter", "wallstreet_node")
    builder.add_edge("finance_starter", "kr36_node")

    # 并行分支汇聚到合并节点
    builder.add_edge(["wallstreet_node", "kr36_node"], "merge_finance_node")

    # 合并节点 → 结束
    builder.add_edge("merge_finance_node", END)

    return builder


# 快捷实例化
finance_news_graph = create_finance_news_graph().compile()