import uuid

from app.graph.builder import graph


def recognize_fund(fund_code: str) -> dict:
    # 这一篇先不碰数据库：给一个基金代码，就分析这一只。
    # “从持仓表里读代码再分析”是后面的事，这里先把图本身跑通。
    thread_id = str(uuid.uuid4())

    # 图的初始状态只有一个基金代码。
    initial_state = {"fund_code": fund_code}

    # invoke 会把图从头跑到 END，返回最终的 State。
    # thread_id 本篇还用不上检查点，但先按一次分析一个 id 的规矩生成好。
    result = graph.invoke(
        initial_state,
        config={"configurable": {"thread_id": thread_id}},
    )

    return result["fund"]
