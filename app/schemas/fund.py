from pydantic import BaseModel, Field


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
