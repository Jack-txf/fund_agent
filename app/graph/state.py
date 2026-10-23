from typing import Any, TypedDict

from app.schemas.fund import RecognizeRequest


# 这一篇只分析“一只基金”，所以 State 不搞列表。
# 字段跟着流程走：基金数据、新闻、报告、审核意见，在同一条 thread 上不断往下传。
class FundState(TypedDict, total=False):
    # 输入：一个 6 位基金代码，整个图从它开始。
    fund_code: str
    # fetch_fund 节点的产出：名称、净值、走势、基金档案。
    fund: dict[str, Any]
    # fetch_news 节点的产出：新闻列表，每条含标题、来源、时间、链接。
    news: list[dict[str, Any]]

    # write_report 节点的产出：Markdown 报告正文。
    report: str

    # review 节点恢复后拿到的人工结论：approved + feedback。
    review: dict[str, Any]

    # 报告已经被打回重写了几版，用来控制“最多三次”。
    revision_count: int
    # 收尾结论：approved（审核通过）或 max_revisions_reached（返工三次仍不满意）。
    final_status: str


def init_state(req: RecognizeRequest) -> FundState:
    return {
        "fund_code": req.fund_code,
        "revision_count": 0,
    }