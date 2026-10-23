import uuid

from langgraph.types import Command

from app.core.exceptions import BadRequestError, NotFoundError
from app.graph.builder import graph
from app.graph.state import init_state
from app.schemas.fund import RecognizeRequest
from app.services.fund_data_service import get_fund_data_source


def recognize_fund(fund_code: str) -> dict:
    # /recognize 只做“认基金”，直接调数据源，不复用那张会暂停、会烧 token 的大图。
    fund_data = get_fund_data_source().fetch_fund(fund_code)
    return {
        "fund_code": fund_data["fund_code"],
        "fund_name": fund_data["fund_name"],
        "nav": fund_data["nav"],
        "trend": fund_data["trend"],
    }


# 【真正地开始分析一只基金，走一条完整的 Graph 流程】
def fund_analyse(req: RecognizeRequest) -> dict:
    # 1. 用请求体构造图的初始 State，里面有基金代码和初始返工计数。
    state = init_state(req)

    # 2. 每次分析一个独立 thread_id，它是暂停/恢复时找回这次会话状态的钥匙。
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # 3. 启动图：并行取基金数据和新闻 -> 写报告 -> 在 review 节点暂停。
    graph.invoke(state, config=config)

    # 4. 暂停后把“当前这一帧”连同 thread_id 返回给调用方。
    return _snapshot(thread_id)


# 【人工审核后恢复图：approved=true 通过，false 带着 feedback 打回】
def review_fund(thread_id: str, approved: bool, feedback: str | None) -> dict:
    config = {"configurable": {"thread_id": thread_id}}

    current = graph.get_state(config)

    # 完全取不到值：thread_id 不对或检查点库里没有这条会话。
    if not current.values and not current.next:
        raise NotFoundError(f"分析会话 {thread_id} 不存在")

    # next 为空说明图已经走到 END，不能对一份终稿反复审核。
    if not current.next:
        raise BadRequestError("该分析会话已经结束，不能再次审核")

    # Command(resume=...) 的值会成为 review 节点里 interrupt(...) 的返回值。
    graph.invoke(
        Command(resume={"approved": approved, "feedback": (feedback or "").strip()}),
        config=config,
    )

    return _snapshot(thread_id)


def _snapshot(thread_id: str) -> dict:
    # 统一封装“这次分析现在长什么样”，避免把 Interrupt 之类框架对象直接丢给前端。
    config = {"configurable": {"thread_id": thread_id}}
    current = graph.get_state(config)
    values = current.values

    return {
        "thread_id": thread_id,
        # next 里有节点名 = 图暂停在某个节点之前（这里就是 review）；为空 = 已结束。
        "status": "waiting_review" if current.next else "finished",
        "fund": values.get("fund"),
        "news": values.get("news", []),
        "report": values.get("report"),
        "revision_count": values.get("revision_count", 0),
        "final_status": values.get("final_status"),
    }