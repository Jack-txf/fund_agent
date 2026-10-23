from fastapi import APIRouter, HTTPException

from app.schemas.fund import AnalyseResponse, RecognizedFundOut, RecognizeRequest, ReviewRequest
from app.services.analysis_service import fund_analyse, recognize_fund, review_fund

router = APIRouter()


# 认一只基金：名称、净值、一句走势。不走完整大图。
@router.post("/recognize", response_model=RecognizedFundOut)
def recognize(payload: RecognizeRequest) -> dict:
    try:
        return recognize_fund(payload.fund_code)
    except ValueError as exc:
        # 比如离线 fixtures 里根本没有这只基金，属于请求本身的问题，返回 400。
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# 真正分析一只基金：图跑到人工审核节点暂停，返回报告和 thread_id。
@router.post("/real_fund_analyse", response_model=AnalyseResponse)
def real_fund_analyse(req: RecognizeRequest) -> dict:
    try:
        return fund_analyse(req)
    except ValueError as exc:
        # 代码不存在、档案为空等：请求本身的问题。
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        # 第三方数据/搜索接口失败：上游问题。
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# 人工审核：满意就通过，不满意带意见打回；第三次返工后还不满意，图会强制结束。
@router.post("/review", response_model=AnalyseResponse)
def review(req: ReviewRequest) -> dict:
    # NotFoundError / BadRequestError 由 main.py 里注册的全局异常处理器统一转成状态码。
    return review_fund(req.thread_id, req.approved, req.feedback)