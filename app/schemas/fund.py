from typing import Literal

from pydantic import BaseModel, Field, model_validator


class RecognizeRequest(BaseModel):
    # 分析一只基金的请求体：只需要一个 6 位数字代码。
    fund_code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6 位基金代码",
    )


class RecognizedFundOut(BaseModel):
    # recognize 节点跑完后返回给前端的结构。
    fund_code: str
    fund_name: str
    nav: float
    trend: str


class ReviewRequest(BaseModel):
    # 人工审核请求：拿着第一次分析返回的 thread_id 回来给结论。
    thread_id: str = Field(..., min_length=1, description="分析会话 ID")
    approved: bool = Field(..., description="true=审核通过；false=打回重写")
    feedback: str | None = Field(
        default=None,
        max_length=500,
        description="打回时的具体修改意见；approved=false 时必填",
    )

    @model_validator(mode="after")
    def require_feedback_when_rejected(self) -> "ReviewRequest":
        if not self.approved and not (self.feedback and self.feedback.strip()):
            raise ValueError("打回重写时必须填写具体的修改意见 feedback")
        return self


class AnalyseResponse(BaseModel):
    # waiting_review=图已暂停在审核节点；finished=流程彻底结束。
    thread_id: str
    status: Literal["waiting_review", "finished"]
    fund: dict | None = None
    news: list[dict] = []
    report: str | None = None
    revision_count: int = 0
    final_status: Literal["approved", "max_revisions_reached"] | None = None