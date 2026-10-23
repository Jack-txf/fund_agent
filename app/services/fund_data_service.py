import json
import math
from typing import Any, Protocol
from datetime import datetime, timedelta
from typing import Any

from app.graph.nodes.trends import summarize_trend


class FundDataSource(Protocol):
    # 所有数据源都实现同一个方法：输入 6 位基金代码，输出统一结构。
    # 图节点不关心数据来自本地 JSON 还是 akshare。
    def fetch_fund(self, fund_code: str) -> dict[str, Any]:
        ...


class FixtureFundDataSource:
    def __init__(self) -> None:
        # 延迟读取文件，避免应用一启动就因为测试文件不存在而失败。
        from app.core.config import BASE_DIR

        self.fixture_path = BASE_DIR / "app" / "fixtures" / "funds.json"

    def fetch_fund(self, fund_code: str) -> dict[str, Any]:
        raw_data = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        fund = raw_data["funds"].get(fund_code)

        if fund is None:
            # 不存在于 fixtures 时，错误信息要明确提示该先补假数据。
            raise ValueError(f"fixtures 中不存在基金 {fund_code}，请先在 funds.json 中补充")

        history = [float(item) for item in fund["history"]]

        return {
            "fund_code": fund_code,
            "fund_name": fund["name"],
            "nav": float(fund["nav"]),
            "history": history,
            "trend": summarize_trend(history),
            # basic 是基金档案：基金公司、经理、类型、规模这些，报告节点会用到。
            "basic": fund.get("basic", {}),
        }


def _clean_cell(value: Any) -> str | None:
    # akshare 返回的表格里，空值可能是 NaN/NaT，统一转成 None，别让 "nan" 混进报告。
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip()
    return text or None


class AkShareFundDataSource:
    # 真实数据源：基金档案走雪球接口，净值走势走东方财富接口，akshare 都已经封装好了。
    def fetch_fund(self, fund_code: str) -> dict[str, Any]:
        import akshare as ak
        import pandas as pd

        # 1. 基金档案（保持不变）
        basic_df = ak.fund_individual_basic_info_xq(symbol=fund_code)
        if basic_df is None or basic_df.empty:
            raise ValueError(f"未查询到基金 {fund_code}，请确认 6 位基金代码是否正确")

        basic = {
            str(item): _clean_cell(value)
            for item, value in zip(basic_df["item"], basic_df["value"])
        }
        fund_name = basic.get("基金名称") or "未知基金"

        # 2. 历史净值走势
        nav_df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        if nav_df is None or nav_df.empty:
            raise ValueError(f"未获取到基金 {fund_code} 的历史净值数据")

        # 按近一个月过滤，并保留日期 ----
        # 确保“净值日期”是 datetime 类型，便于比较
        nav_df["净值日期"] = pd.to_datetime(nav_df["净值日期"])

        # 计算一个月前的日期（用 30 天近似“近一月”）
        start_date = datetime.now() - timedelta(days=30)
        recent_df = nav_df[nav_df["净值日期"] >= start_date].copy()

        # 如果近一月无数据（极端情况，如新基金），回退到最后一条
        if recent_df.empty:
            recent_df = nav_df.tail(1).copy()

        # 构造带日期的 history：列表中的每个元素是 {"date": "...", "nav": ...}
        history = [
            {
                "date": row["净值日期"].strftime("%Y-%m-%d"),
                "nav": float(row["单位净值"]),
            }
            for _, row in recent_df.iterrows()
        ]

        # 最新净值取过滤后数据的最后一条（或全量数据的最后一条均可，这里取 recent_df）
        latest_nav = history[-1]["nav"]

        # 如果 summarize_trend 只接受纯净值列表，可传 [h["nav"] for h in history]
        # 若它也能处理带日期结构，直接传 history 即可。这里假定它仍需要纯数值列表。
        nav_values_only = [h["nav"] for h in history]

        return {
            "fund_code": fund_code,
            "fund_name": fund_name,
            "nav": latest_nav,
            "history": history,  # 带日期的近一月数据
            "trend": summarize_trend(nav_values_only),  # 根据原有函数签名调整
            "basic": basic,
        }


def get_fund_data_source() -> FundDataSource:
    # 工厂方法统一决定当前使用哪种数据源。
    # 业务代码只依赖 FundDataSource，不直接判断 USE_FIXTURES。
    from app.core.config import USE_FIXTURES

    if USE_FIXTURES:
        return FixtureFundDataSource()

    return AkShareFundDataSource()