from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Advice = Literal["buy", "sell", "hold"]
ReportStatus = Literal["pending", "approved", "rejected"]


class FundView(BaseModel):
    fund_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    fund_name: str = Field(..., min_length=1, max_length=100)
    trend: str = Field(..., min_length=1, max_length=500)
    advice: Advice
    reason: str = Field(..., min_length=1, max_length=2000)


class ReportContent(BaseModel):
    views: list[FundView] = Field(..., min_length=1)
    overall: str = Field(..., min_length=1, max_length=5000)


class ReportCreate(BaseModel):
    thread_id: str = Field(..., min_length=1, max_length=64)
    version: int = Field(..., ge=1)
    status: ReportStatus = "pending"
    content: ReportContent
    feedback: str | None = Field(default=None, max_length=1000)


class ReportUpdate(BaseModel):
    status: ReportStatus | None = None
    content: ReportContent | None = None
    feedback: str | None = Field(default=None, max_length=1000)


class ReportOut(BaseModel):
    id: int
    thread_id: str
    version: int
    status: ReportStatus
    content: ReportContent
    feedback: str | None
    created_at: str

    model_config = ConfigDict(from_attributes=True)
