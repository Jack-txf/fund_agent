import sqlite3
from typing import Any

from app.core.exceptions import ConflictError, NotFoundError
from app.schemas.holding import HoldingCreate


def list_holdings(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT * FROM holdings ORDER BY id DESC"
    ).fetchall()
    return [dict(row) for row in rows]


def get_holding(connection: sqlite3.Connection, holding_id: int) -> dict[str, Any]:
    row = connection.execute(
        "SELECT * FROM holdings WHERE id = ?",
        (holding_id,),
    ).fetchone()
    if row is None:
        raise NotFoundError(f"Holding {holding_id} not found")
    return dict(row)


def create_holding(
    connection: sqlite3.Connection,
    holding: HoldingCreate,
) -> dict[str, Any]:
    try:
        cursor = connection.execute(
            """
            INSERT INTO holdings (fund_code, shares, cost_nav)
            VALUES (:fund_code, :shares, :cost_nav)
            """,
            holding.model_dump(),
        )
    except sqlite3.IntegrityError as exc:
        raise ConflictError(f"Fund {holding.fund_code} already exists") from exc

    return get_holding(connection, int(cursor.lastrowid))


def update_holding(
    connection: sqlite3.Connection,
    holding_id: int,
    holding: HoldingCreate,
) -> dict[str, Any]:
    get_holding(connection, holding_id)
    data = holding.model_dump()
    data["id"] = holding_id

    try:
        connection.execute(
            """
            UPDATE holdings
            SET fund_code = :fund_code,
                shares = :shares,
                cost_nav = :cost_nav,
                updated_at = datetime('now','localtime')
            WHERE id = :id
            """,
            data,
        )
    except sqlite3.IntegrityError as exc:
        raise ConflictError(f"Fund {holding.fund_code} already exists") from exc

    return get_holding(connection, holding_id)


def delete_holding(connection: sqlite3.Connection, holding_id: int) -> None:
    get_holding(connection, holding_id)
    connection.execute("DELETE FROM holdings WHERE id = ?", (holding_id,))
