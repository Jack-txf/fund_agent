import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from app.core.config import CHECKPOINT_PATH
from app.graph.nodes.nodes import (
    fetch_fund_node,
    fetch_news_node,
    finalize_node,
    review_node,
    route_after_review,
    write_report_node, hello_node,
)
from app.graph.state import FundState


def _build_checkpointer() -> SqliteSaver:
    # 检查点库与业务库 fund.db 分开：图状态冻结在哪一帧，全写进这个 SQLite。
    # 服务重启后，只要 thread_id 还在，就能从文件里把当时的状态捞回来。
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(CHECKPOINT_PATH), check_same_thread=False)
    saver = SqliteSaver(connection)
    # 首次运行时把检查点需要的表建好。
    saver.setup()
    return saver


def build_graph():
    graph = StateGraph(FundState)

    graph.add_node("hello_node", hello_node)
    graph.add_node("fetch_fund", fetch_fund_node)
    graph.add_node("fetch_news", fetch_news_node)
    graph.add_node("write_report", write_report_node)
    graph.add_node("review", review_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "hello_node")
    graph.add_edge("hello_node", "fetch_fund")
    graph.add_edge("hello_node", "fetch_news")
    graph.add_edge("fetch_fund", "write_report")
    graph.add_edge("fetch_news", "write_report")

    # 报告写完进入人工审核，review 节点内部会 interrupt 暂停。
    graph.add_edge("write_report", "review")

    # 审核后三选一：满意收尾；不满意且没超次数 -> 带着意见回到 write_report；
    # 已经返工三次 -> 强制收尾。
    graph.add_conditional_edges(
        "review",
        route_after_review,
        {
            "write_report": "write_report",
            "finalize": "finalize",
        },
    )
    graph.add_edge("finalize", END)

    return graph.compile(checkpointer=_build_checkpointer())


# 模块加载时就把图编译好，后面谁要用直接 import graph。
graph = build_graph()