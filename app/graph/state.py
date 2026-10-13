from typing import Any, TypedDict


# 这一篇只分析“一只基金”，所以 State 不搞列表。
# 等一只基金的整条路跑顺了，后面再考虑一次分析多只，别一上来就把自己绕进去。
class FundState(TypedDict, total=False):
    # 输入：一个 6 位基金代码，整个图从它开始。
    fund_code: str
    # recognize 节点的产出：这只基金的名称、最新净值、一句走势人话。
    fund: dict[str, Any]
