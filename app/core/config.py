import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DB_DIR = BASE_DIR / "db"
DATABASE_PATH = DB_DIR / "fund.db"
SCHEMA_PATH = DB_DIR / "schema.sql"

# LangGraph 检查点数据库。它和业务库 fund.db 故意分成两个 SQLite 文件：
# 一个管持仓、报告这些业务数据，一个管图跑到哪一帧的状态，互不干扰。
CHECKPOINT_PATH = DB_DIR / "langgraph_checkpoints.db"

API_PREFIX = "/api"

# 默认使用本地虚构数据。
# 这样没网、第三方接口波动、写文章截图时，项目都能稳定跑起来。
# 想读取真实公开数据时，在启动前设置环境变量：USE_FIXTURES=false
USE_FIXTURES = os.getenv("USE_FIXTURES", "true").lower() in {"1", "true", "yes", "on"}

# 单只基金识别失败时的重试次数。真实网络请求偶尔会抖一下，简单重试一次就够。
HTTP_RETRIES = int(os.getenv("FUND_HTTP_RETRIES", "2"))

# 新闻搜索一次最多取多少条。
NEWS_PAGE_SIZE = int(os.getenv("NEWS_PAGE_SIZE", "10"))

# 报告最多允许人工打回重写几次，超过就强制收尾，避免图在循环里无限烧 token。
MAX_REVISIONS = int(os.getenv("MAX_REVISIONS", "3"))

LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "60"))