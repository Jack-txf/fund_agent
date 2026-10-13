from fastapi import APIRouter, HTTPException

from app.schemas.fund import RecognizedFundOut, RecognizeRequest
from app.services.analysis_service import recognize_fund

router = APIRouter()


# 分析一只基金：前端把基金代码 POST 过来，后端把图跑一遍。
@router.post("/recognize", response_model=RecognizedFundOut)
def recognize(payload: RecognizeRequest) -> dict:
    try:
        return recognize_fund(payload.fund_code)
    except ValueError as exc:
        # 比如离线 fixtures 里根本没有这只基金，属于请求本身的问题，返回 400。
        raise HTTPException(status_code=400, detail=str(exc)) from exc
