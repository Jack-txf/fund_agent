from pydantic import BaseModel, ConfigDict, Field


class HoldingCreate(BaseModel):
    fund_code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6 位基金代码",
    )
    shares: float | None = Field(default=None, gt=0)
    cost_nav: float | None = Field(default=None, gt=0)


class HoldingOut(BaseModel):
    id: int
    fund_code: str
    shares: float | None
    cost_nav: float | None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
