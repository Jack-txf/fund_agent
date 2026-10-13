from sqlite3 import Connection
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_db
from app.schemas.report import ReportCreate, ReportOut, ReportUpdate
from app.services import report_service

router = APIRouter()
DbSession = Annotated[Connection, Depends(get_db)]


@router.get("", response_model=list[ReportOut])
def list_reports(db: DbSession, thread_id: str | None = None) -> list[dict]:
    return report_service.list_reports(db, thread_id)


@router.post("", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def create_report(db: DbSession, report: ReportCreate) -> dict:
    return report_service.create_report(db, report)


@router.get("/{report_id}", response_model=ReportOut)
def get_report(db: DbSession, report_id: int) -> dict:
    return report_service.get_report(db, report_id)


@router.patch("/{report_id}", response_model=ReportOut)
def update_report(db: DbSession, report_id: int, report: ReportUpdate) -> dict:
    return report_service.update_report(db, report_id, report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(db: DbSession, report_id: int) -> Response:
    report_service.delete_report(db, report_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
