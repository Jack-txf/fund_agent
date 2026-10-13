from app.core.config import DB_DIR, SCHEMA_PATH
from app.db.connection import create_connection


def init_database() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    if not SCHEMA_PATH.exists():
        raise RuntimeError(f"Database schema not found: {SCHEMA_PATH}")

    connection = create_connection()
    try:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        connection.commit()
    finally:
        connection.close()
