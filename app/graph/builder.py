from langgraph.graph import END, START, StateGraph

from app.graph.nodes.recognize import recognize_node
from app.graph.state import FundState


# 图的组装统一放这里。
# 本篇只有一个真正干活的节点，路径是：START -> recognize -> END
def build_graph():
    # StateGraph 是图的构造器，FundState 规定了图里能流动哪些字段。
    builder = StateGraph(FundState)

    # 注册 recognize 节点（认基金、看走势）。
    builder.add_node("recognize", recognize_node)

    # 用边把节点串起来：图从 START 进 recognize，干完直接到 END。
    builder.add_edge(START, "recognize")
    builder.add_edge("recognize", END)

    # 本篇图一口气跑完、中途不暂停，所以先不挂 checkpointer。
    return builder.compile()


# 模块加载时就把图编译好，后面谁要用直接 import graph。
graph = build_graph()
