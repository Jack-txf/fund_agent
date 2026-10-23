import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Protocol

from app.core.config import HTTP_RETRIES, NEWS_PAGE_SIZE


class NewsDataSource(Protocol):
    # 输入基金代码，输出新闻列表。
    # 每条新闻必须凑齐四件套：标题、来源、发布时间、能点回去的真实链接。
    def fetch_news(self, fund_code: str) -> list[dict[str, Any]]:
        ...


class FixtureNewsDataSource:
    def __init__(self) -> None:
        from app.core.config import BASE_DIR

        self.fixture_path = BASE_DIR / "app" / "fixtures" / "news.json"

    def fetch_news(self, fund_code: str) -> list[dict[str, Any]]:
        raw_data = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        # 离线模式下没有新闻也算正常：报告里会如实写“近期无公开新闻”。
        return list(raw_data.get("news", {}).get(fund_code, []))


def _strip_html(text: str, limit: int = 120) -> str:
    # 搜索接口返回的摘要里可能带 HTML 标签，简单清一下并截断。
    plain = re.sub(r"<[^>]+>", "", text or "")
    plain = re.sub(r"\s+", " ", plain).strip()
    return plain[:limit]


class EastmoneyNewsDataSource:
    # 东方财富全文搜索接口，akshare 的 stock_news_em 底层调的就是它，
    # 区别只是人家传股票代码，咱这里传基金代码。
    SEARCH_URL = "https://search-api-web.eastmoney.com/search/jsonp"

    def __init__(self, page_size: int = NEWS_PAGE_SIZE) -> None:
        self.page_size = page_size

    def _request_text(self, fund_code: str) -> str:
        inner_param = {
            "uid": "",
            "keyword": fund_code,
            "type": ["cmsArticleWebOld"],
            "client": "web",
            "clientType": "web",
            "clientVersion": "curr",
            "param": {
                "cmsArticleWebOld": {
                    "searchScope": "default",
                    "sort": "default",
                    "pageIndex": 1,
                    "pageSize": self.page_size,
                    # 高亮标签置空，省得回来还得剥 <em>。
                    "preTag": "",
                    "postTag": "",
                }
            },
        }
        params = urllib.parse.urlencode(
            {"cb": "fund_agent_cb", "param": json.dumps(inner_param, ensure_ascii=False)}
        )
        request = urllib.request.Request(
            f"{self.SEARCH_URL}?{params}",
            headers={
                "User-Agent": "Mozilla/5.0 FundAgent/0.1 personal-low-frequency-script",
                "Referer": "https://so.eastmoney.com/",
            },
        )

        last_error: Exception | None = None
        for attempt in range(HTTP_RETRIES):
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    return response.read().decode("utf-8")
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
                time.sleep(0.5 * (attempt + 1))

        raise RuntimeError(f"搜索基金 {fund_code} 的新闻失败") from last_error

    @staticmethod
    def _parse_jsonp(script_text: str) -> list[dict[str, Any]]:
        # 返回体是 JSONP：fund_agent_cb({...})，用正则把括号里的 JSON 抠出来。
        match = re.search(r"^[^(]+\((.*)\)\s*$", script_text, flags=re.S)
        if match is None:
            raise ValueError("新闻接口返回格式异常")

        payload = json.loads(match.group(1))
        return payload.get("result", {}).get("cmsArticleWebOld", []) or []

    def fetch_news(self, fund_code: str) -> list[dict[str, Any]]:
        script_text = self._request_text(fund_code)
        raw_items = self._parse_jsonp(script_text)

        news_list: list[dict[str, Any]] = []
        for item in raw_items:
            title = _strip_html(item.get("title", ""))
            url = (item.get("url") or "").strip()
            # 标题或链接缺一个就丢掉，绝不允许“没有出处的消息”混进报告。
            if not title or not url:
                continue
            news_list.append(
                {
                    "title": title,
                    "source": (item.get("mediaName") or "未知来源").strip(),
                    "published_at": (item.get("date") or "").strip(),
                    "url": url,
                    "summary": _strip_html(item.get("content", "")),
                }
            )

        return news_list


def get_news_data_source() -> NewsDataSource:
    from app.core.config import USE_FIXTURES

    if USE_FIXTURES:
        return FixtureNewsDataSource()

    return EastmoneyNewsDataSource()