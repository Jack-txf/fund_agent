from collections.abc import Generator
from sqlite3 import Connection

from app.db.connection import create_connection


def get_db() -> Generator[Connection, None, None]:
    connection = create_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
