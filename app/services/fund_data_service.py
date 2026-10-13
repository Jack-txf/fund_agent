import json
import re
import time
import urllib.error
import urllib.request
from typing import Any, Protocol

from app.core.config import HTTP_RETRIES
from app.graph.nodes.trends import summarize_trend


class FundDataSource(Protocol):
    # 所有数据源都实现同一个方法：输入 6 位基金代码，输出统一结构。
    # recognize 节点不关心数据来自本地 JSON 还是真实网络请求。
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
        }


class WebFundDataSource:
    PINGZHONG_URL = "https://fund.eastmoney.com/pingzhongdata/{code}.js"

    def _request_text(self, fund_code: str) -> str:
        url = self.PINGZHONG_URL.format(code=fund_code)
        request = urllib.request.Request(
            url,
            headers={
                # 给一个正常的浏览器标识，只做低频公开数据读取，不做绕过反爬的事情。
                "User-Agent": "Mozilla/5.0 FundAgent/0.1 personal-low-frequency-script"
            },
        )

        last_error: Exception | None = None

        for attempt in range(HTTP_RETRIES):
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    # 天天基金这个接口通常是 utf-8 编码。
                    return response.read().decode("utf-8")
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
                # 简单退避，避免网络刚抖一下立刻连续打请求。
                time.sleep(0.5 * (attempt + 1))

        raise RuntimeError(f"读取基金 {fund_code} 公开数据失败") from last_error

    @staticmethod
    def _parse_pingzhong(script_text: str) -> tuple[str, list[float]]:
        # 基金名称在 pingzhongdata 里形如：var fS_name = "xxx";
        name_match = re.search(r'var\s+fS_name\s*=\s*"(.*?)";', script_text)
        fund_name = name_match.group(1) if name_match else "未知基金"

        # 历史净值在 Data_netWorthTrend 中，每一项形如 {"x":..., "y":1.234}
        trend_match = re.search(
            r"var\s+Data_netWorthTrend\s*=\s*(\[.*?]);",
            script_text,
            flags=re.S,
        )

        if trend_match is None:
            raise ValueError("没有解析到历史净值数据")

        trend_data = json.loads(trend_match.group(1))
        history = [float(item["y"]) for item in trend_data if item.get("y") is not None]

        if not history:
            raise ValueError("历史净值数据为空")

        return fund_name, history

    def fetch_fund(self, fund_code: str) -> dict[str, Any]:
        script_text = self._request_text(fund_code)
        fund_name, history = self._parse_pingzhong(script_text)

        return {
            "fund_code": fund_code,
            "fund_name": fund_name,
            "nav": history[-1],
            "history": history,
            "trend": summarize_trend(history),
        }


def get_fund_data_source() -> FundDataSource:
    # 工厂方法统一决定当前使用哪种数据源。
    # 业务代码只依赖 FundDataSource，不直接判断 USE_FIXTURES。
    from app.core.config import USE_FIXTURES

    if USE_FIXTURES:
        return FixtureFundDataSource()

    return WebFundDataSource()
