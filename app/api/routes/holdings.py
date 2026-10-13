from sqlite3 import Connection
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_db
from app.schemas.holding import HoldingCreate, HoldingOut
from app.services import holding_service

router = APIRouter()
DbSession = Annotated[Connection, Depends(get_db)]


@router.get("", response_model=list[HoldingOut])
def list_holdings(db: DbSession) -> list[dict]:
    return holding_service.list_holdings(db)


@router.post("", response_model=HoldingOut, status_code=status.HTTP_201_CREATED)
def create_holding(db: DbSession, holding: HoldingCreate) -> dict:
    return holding_service.create_holding(db, holding)


@router.get("/{holding_id}", response_model=HoldingOut)
def get_holding(db: DbSession, holding_id: int) -> dict:
    return holding_service.get_holding(db, holding_id)


@router.put("/{holding_id}", response_model=HoldingOut)
def update_holding(db: DbSession, holding_id: int, holding: HoldingCreate) -> dict:
    return holding_service.update_holding(db, holding_id, holding)


@router.delete("/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(db: DbSession, holding_id: int) -> Response:
    holding_service.delete_holding(db, holding_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
