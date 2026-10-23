# LangGraph 里最核心的 nodes 部分：一条完整的基金分析流水线。
#   fetch_fund  -> write_report -> review(人工审核，暂停) -> finalize
#          ^news^     ^            |打回重写（最多3次）
# fetch_fund 和 fetch_news 从 START 并行分叉，在 write_report 汇合。
from datetime import date

from langgraph.types import interrupt

from app.core.config import MAX_REVISIONS, USE_FIXTURES
from app.graph.llm import get_llm
from app.graph.state import FundState
from app.services.fund_data_service import get_fund_data_source
from app.services.news_service import get_news_data_source

def hello_node(state: FundState):
    print(f"[hello_node]: hello")
    return state

# 节点1：akshare 获取基金档案、净值和走势。
def fetch_fund_node(state: FundState) -> dict:
    fund_code = state["fund_code"]
    print(f"[fetch_fund_node] 开始获取基金数据: {fund_code}")

    fund_data = get_fund_data_source().fetch_fund(fund_code)

    print(f"[fetch_fund_node] 完成: {fund_data['fund_name']} 净值 {fund_data['nav']}")
    return {"fund": fund_data}


# 节点2：webSearch 拉取财经新闻、舆情。
def fetch_news_node(state: FundState) -> dict:
    fund_code = state["fund_code"]
    print(f"[fetch_news_node] 开始搜索新闻: {fund_code}")

    news_list = get_news_data_source().fetch_news(fund_code)

    print(f"[fetch_news_node] 完成: 命中 {len(news_list)} 条新闻")
    return {"news": news_list}


def _basic_lines(fund: dict) -> list[str]:
    # 基金档案在真实模式和 fixtures 模式下是同一套 key。
    basic = fund.get("basic") or {}
    ordered_keys = [
        "基金全称",
        "基金类型",
        "成立时间",
        "最新规模",
        "基金公司",
        "基金经理",
        "业绩比较基准",
    ]
    lines = [f"- 基金名称：{fund['fund_name']}（{fund['fund_code']}）"]
    for key in ordered_keys:
        value = basic.get(key)
        if value:
            lines.append(f"- {key}：{value}")
    return lines


def _news_section(news_list: list[dict]) -> str:
    if not news_list:
        return "近期未检索到带真实出处的公开新闻，本部分不做臆测。"

    lines = []
    for index, item in enumerate(news_list, start=1):
        lines.append(
            f"{index}. {item['title']}\n"
            f"   - 来源：{item['source']}　发布时间：{item['published_at']}\n"
            f"   - 链接：{item['url']}"
        )
    return "\n".join(lines)


# fixtures 模式下不烧 token，用模板拼一份结构完整的报告，保证离线也能演示整条流程。
def _build_fixture_report(state: FundState) -> str:
    fund = state["fund"]
    news_list = state.get("news", [])
    revision_count = state.get("revision_count", 0)
    review = state.get("review") or {}

    parts = [
        f"# {fund['fund_name']}（{fund['fund_code']}）分析报告（离线虚构数据）",
        "",
        f"> 报告日期：{date.today().isoformat()}　分析模式：fixtures（数据与新闻均为虚构，仅供开发演示）",
        "",
        "## 一、基金概况",
        "\n".join(_basic_lines(fund)),
        "",
        "## 二、净值走势",
        f"- 最新单位净值：{fund['nav']:.4f}",
        f"- 近期走势：{fund['trend']}",
        "- 分析：离线模式下仅基于虚构净值序列做技术面描述，不代表真实市场判断。",
        "",
        "## 三、新闻与舆情",
        _news_section(news_list),
        "",
        "## 四、持仓建议",
        "离线虚构数据，不提供任何真实投资建议。真实模式下本部分由大模型结合基金数据与新闻撰写。",
        "",
    ]

    if revision_count > 0:
        parts.extend(
            [
                "## 五、返工说明",
                f"- 这是第 {revision_count} 次返工后的版本。",
                f"- 已重点根据你的意见调整：{review.get('feedback', '')}",
                "",
            ]
        )

    return "\n".join(parts)


_REPORT_SYSTEM_PROMPT = """你是一名严谨的基金研究助理，负责根据给定材料撰写基金分析报告。
硬性要求：
1. 只允许使用提供的基金数据和新闻材料，严禁编造任何新闻、数据或链接。
2. 每条新闻必须保留给定的来源、发布时间和原始链接，格式不可省略。
3. 如果没有新闻材料，必须如实写“近期未检索到带真实出处的公开新闻”，不得凭空补充。
4. 报告末尾必须注明：本报告由 AI 基于公开信息生成，仅供参考，不构成投资建议。
5. 输出 Markdown，依次包含四个二级标题：## 一、基金概况、## 二、净值走势、## 三、新闻与舆情、## 四、持仓建议。"""


def _build_llm_report(state: FundState) -> str:
    fund = state["fund"]
    news_list = state.get("news", [])
    revision_count = state.get("revision_count", 0)
    review = state.get("review") or {}

    material = [
        f"报告日期：{date.today().isoformat()}",
        "",
        "【基金数据】",
        "\n".join(_basic_lines(fund)),
        f"- 最新单位净值：{fund['nav']:.4f}",
        f"- 近期走势描述：{fund['trend']}",
        "",
        "【新闻材料】（只有这些可以引用）",
        _news_section(news_list),
    ]

    if revision_count > 0:
        material.extend(
            [
                "",
                f"这是被人工打回后的第 {revision_count} 次返工版本。",
                f"上一版报告的审核意见是：{review.get('feedback', '')}",
                "请针对审核意见修改，没被质疑的部分保持稳定，不要与审核意见无关地大改。",
            ]
        )

    response = get_llm().invoke(
        [
            ("system", _REPORT_SYSTEM_PROMPT),
            ("human", "\n".join(material)),
        ]
    )
    return str(response.content).strip()


# 节点3：汇合基金数据和新闻，生成 Markdown 报告。
# 被打回后也会回到这个节点：带着人工意见再写一版，不重新取数。
def write_report_node(state: FundState) -> dict:
    # 每次带意见回到这里，返工计数 +1。第一次写报告时 review 还不存在，不加。
    revision_count = state.get("revision_count", 0)
    if state.get("review"):
        revision_count += 1

    print(f"[write_report_node] 开始撰写报告，当前返工次数: {revision_count}")

    if USE_FIXTURES:
        working_state = {**state, "revision_count": revision_count}
        report = _build_fixture_report(working_state)
    else:
        working_state = {**state, "revision_count": revision_count}
        report = _build_llm_report(working_state)

    print(f"[write_report_node] 报告完成，正文长度: {len(report)}")
    return {"report": report, "revision_count": revision_count}


# 节点4：人工审核。图在这里真正暂停，等待人拿着 thread_id 回来给结论。
def review_node(state: FundState) -> dict:
    print("[review_node] 报告已提交，暂停等待人工审核")

    # interrupt 做两件事：
    # 1. 第一次走到这里，把载荷抛给调用方，图当场冻住；
    # 2. 人审核后用 Command(resume=...) 续跑，interrupt 的返回值就是人给的结论。
    decision = interrupt(
        {
            "prompt": "报告已生成，请审核：满意请通过，不满意请写明修改意见后打回。",
            "revision_count": state.get("revision_count", 0),
            "report": state["report"],
        }
    )

    approved = bool(decision.get("approved"))
    feedback = str(decision.get("feedback") or "").strip()
    print(f"[review_node] 收到人工结论: approved={approved}, feedback={feedback!r}")

    return {"review": {"approved": approved, "feedback": feedback}}


# review 之后的岔路口：通过或返工次数用尽 -> finalize；否则打回重写报告。
def route_after_review(state: FundState) -> str:
    review = state.get("review") or {}
    if review.get("approved"):
        return "finalize"
    if state.get("revision_count", 0) >= MAX_REVISIONS:
        print(f"[route_after_review] 已经返工 {MAX_REVISIONS} 次仍不满意，强制收尾")
        return "finalize"
    return "write_report"


# 节点5：最终收尾，给这次分析一个明确的终态。
def finalize_node(state: FundState) -> dict:
    review = state.get("review") or {}
    if review.get("approved"):
        final_status = "approved"
        print("[finalize_node] 审核通过，流程正常结束")
    else:
        final_status = "max_revisions_reached"
        print("[finalize_node] 返工三次仍未通过，流程强制结束")

    return {"final_status": final_status}

