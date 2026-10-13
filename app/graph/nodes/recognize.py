from typing import Any

from app.graph.state import FundState
from app.services.fund_data_service import get_fund_data_source


def recognize_node(state: FundState) -> dict[str, dict[str, Any]]:
    print(f"[recognize_node] 开始执行")

    # 节点只做一件事：从 State 里拿到基金代码。
    fund_code = state["fund_code"]

    # 具体数据从哪里来，节点不关心，交给数据源（本地假数据或真实公开接口）。
    data_source = get_fund_data_source()
    fund_data = data_source.fetch_fund(fund_code)

    # history（一长串历史净值）留在数据源内部算走势用，不继续往 State 里塞。
    # 后续节点只需要名称、净值和那句人话。
    return {
        "fund": {
            "fund_code": fund_data["fund_code"],
            "fund_name": fund_data["fund_name"],
            "nav": fund_data["nav"],
            "trend": fund_data["trend"],
        }
    }
