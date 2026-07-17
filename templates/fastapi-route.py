"""
Template: FastAPI Route com tenant isolation.

Use este template como base para criar qualquer endpoint novo.
Substitua os placeholders (formato {{ModelName}}) e remova os TODOs.

Placeholders:
  - ModelName: nome do SQLModel (ex: Lead, Conversation, Message)
  - model_name: snake_case (ex: lead, conversation, message)
  - endpoint_name: plural snake_case (ex: leads, conversations)
  - endpoint_singular: singular snake_case (ex: lead, conversation)
  - Description: descricao do que o endpoint faz
"""

from datetime import datetime
from typing import Annotated, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session, select

from app.auth.dependencies import (
    get_current_organization,
    get_current_user,
)
from app.database import get_session
from app.models.organization import Organization
from app.models.user import User

# TODO: ajustar import do seu model
# from app.models.MODEL_NAME import MODEL_NAME


router = APIRouter(prefix="/ENDPOINT_NAME", tags=["ENDPOINT_NAME"])


# --- Helper: ID factory ---

def _new_model_name_id() -> str:
    """TODO: ajustar prefixo (lead_, conv_, msg_, etc)."""
    return f"model_name_{uuid4().hex[:12]}"


# --- Schemas (Pydantic, separado do SQLModel) ---

class MODEL_NAMECreate(BaseModel):
    """Schema de entrada (POST)."""
    # TODO: adicionar campos com validators
    name: str = Field(min_length=1, max_length=200)
    # description: str | None = None


class MODEL_NAMEUpdate(BaseModel):
    """Schema de atualizacao (PATCH) — todos campos opcionais."""
    # TODO: adicionar campos como Optional
    name: str | None = Field(default=None, min_length=1, max_length=200)


class MODEL_NAMEResponse(BaseModel):
    """Schema de saida (GET)."""
    id: str
    organization_id: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# --- Endpoints ---

@router.get("", response_model=List[MODEL_NAMEResponse])
async def list_endpoint_name(
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0, description="Offset para paginacao"),
    limit: int = Query(50, ge=1, le=200, description="Limite por pagina"),
):
    """Lista ENDPOINT_NAME do tenant atual com paginacao."""
    # TODO: ajustar query se precisar de filtros/joins
    statement = (
        select(MODEL_NAME)
        .where(MODEL_NAME.organization_id == organization.id)
        .offset(skip)
        .limit(limit)
    )
    items = db.exec(statement).all()
    return items


@router.post("", response_model=MODEL_NAMEResponse, status_code=status.HTTP_201_CREATED)
async def create_endpoint_singular(
    payload: MODEL_NAMECreate,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Cria novo ENDPOINT_SINGULAR no tenant atual."""
    item = MODEL_NAME(
        organization_id=organization.id,  # SEMPRE do contexto, NUNCA do payload
        **payload.model_dump(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=MODEL_NAMEResponse)
async def get_endpoint_singular(
    item_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Busca ENDPOINT_SINGULAR por ID (mesmo tenant only)."""
    item = db.get(MODEL_NAME, item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MODEL_NAME not found",
        )

    # CRITICO: defense in depth — cross-tenant retorna 404 GENERICO
    if item.organization_id != organization.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MODEL_NAME not found",
        )

    return item


@router.patch("/{item_id}", response_model=MODEL_NAMEResponse)
async def update_endpoint_singular(
    item_id: str,
    payload: MODEL_NAMEUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Atualiza ENDPOINT_SINGULAR parcialmente."""
    item = db.get(MODEL_NAME, item_id)

    if not item or item.organization_id != organization.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MODEL_NAME not found",
        )

    # Aplica apenas campos enviados (exclude_unset)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_endpoint_singular(
    item_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Deleta ENDPOINT_SINGULAR."""
    item = db.get(MODEL_NAME, item_id)

    if not item or item.organization_id != organization.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MODEL_NAME not found",
        )

    db.delete(item)
    db.commit()
    return None


# --- Como adicionar ao router principal ---

# Em app/api/v1/__init__.py:
#
# from app.api.v1 import ENDPOINT_NAME  # noqa
# api_router.include_router(ENDPOINT_NAME.router)