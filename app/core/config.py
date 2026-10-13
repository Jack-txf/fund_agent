import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_DIR = BASE_DIR / "db"
DATABASE_PATH = DB_DIR / "fund.db"
SCHEMA_PATH = DB_DIR / "schema.sql"
API_PREFIX = "/api"

# 默认使用本地虚构数据。
# 这样没网、第三方接口波动、写文章截图时，项目都能稳定跑起来。
# 想读取真实公开数据时，在启动前设置环境变量：USE_FIXTURES=false
USE_FIXTURES = os.getenv("USE_FIXTURES", "true").lower() in {"1", "true", "yes", "on"}

# 单只基金识别失败时的重试次数。真实网络请求偶尔会抖一下，简单重试一次就够。
HTTP_RETRIES = int(os.getenv("FUND_HTTP_RETRIES", "2"))
