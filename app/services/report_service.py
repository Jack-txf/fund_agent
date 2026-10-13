import json
import sqlite3
from typing import Any

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.schemas.report import ReportCreate, ReportUpdate


def _report_from_row(row: sqlite3.Row) -> dict[str, Any]:
    report = dict(row)
    report["content"] = json.loads(report["content"])
    return report


def list_reports(
    connection: sqlite3.Connection,
    thread_id: str | None,
) -> list[dict[str, Any]]:
    if thread_id is None:
        rows = connection.execute(
            "SELECT * FROM reports ORDER BY thread_id, version"
        ).fetchall()
    else:
        rows = connection.execute(
            "SELECT * FROM reports WHERE thread_id = ? ORDER BY version",
            (thread_id,),
        ).fetchall()

    return [_report_from_row(row) for row in rows]


def get_report(connection: sqlite3.Connection, report_id: int) -> dict[str, Any]:
    row = connection.execute(
        "SELECT * FROM reports WHERE id = ?",
        (report_id,),
    ).fetchone()
    if row is None:
        raise NotFoundError(f"Report {report_id} not found")
    return _report_from_row(row)


def create_report(
    connection: sqlite3.Connection,
    report: ReportCreate,
) -> dict[str, Any]:
    data = report.model_dump()
    data["content"] = json.dumps(data["content"], ensure_ascii=False)

    try:
        cursor = connection.execute(
            """
            INSERT INTO reports (thread_id, version, status, content, feedback)
            VALUES (:thread_id, :version, :status, :content, :feedback)
            """,
            data,
        )
    except sqlite3.IntegrityError as exc:
        raise ConflictError(
            f"Report version {report.version} of thread {report.thread_id} already exists"
        ) from exc

    return get_report(connection, int(cursor.lastrowid))


def update_report(
    connection: sqlite3.Connection,
    report_id: int,
    report: ReportUpdate,
) -> dict[str, Any]:
    get_report(connection, report_id)

    changes = report.model_dump(exclude_unset=True)
    if not changes:
        raise BadRequestError("At least one field must be provided")

    assignments: list[str] = []
    params: dict[str, Any] = {"id": report_id}

    if "status" in changes:
        assignments.append("status = :status")
        params["status"] = changes["status"]

    if "feedback" in changes:
        assignments.append("feedback = :feedback")
        params["feedback"] = changes["feedback"]

    if "content" in changes:
        assignments.append("content = :content")
        params["content"] = json.dumps(changes["content"], ensure_ascii=False)

    try:
        connection.execute(
            f"UPDATE reports SET {', '.join(assignments)} WHERE id = :id",
            params,
        )
    except sqlite3.IntegrityError as exc:
        raise ConflictError("Failed to update report") from exc

    return get_report(connection, report_id)


def delete_report(connection: sqlite3.Connection, report_id: int) -> None:
    get_report(connection, report_id)
    connection.execute("DELETE FROM reports WHERE id = ?", (report_id,))
