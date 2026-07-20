"""
Template: pacote de dominio completo (v0.2.0) — model + service + api.

Use como base para qualquer feature nova no Revenue SDR OS.
Substitua os placeholders e remova os TODOs:

  - FeatureName:      nome da classe (ex: Lead, Conversation)
  - feature_name:     snake_case singular (ex: lead, conversation)
  - feature_names:    snake_case plural (ex: leads, conversations)
  - feat:             prefixo do ID (ex: lead, conv, msg)

Onde cada trecho vive:
  models.py  -> app/<feature_names>/models.py
  schemas.py -> app/<feature_names>/schemas.py
  service.py -> app/<feature_names>/service.py
  api.py     -> app/<feature_names>/api.py
  Registro   -> app/api/__init__.py
"""

# ============================================================
# models.py — app/<feature_names>/models.py
# ============================================================

from sqlmodel import Field

from app.db.base import TenantMixin, prefixed_id


class FeatureName(TenantMixin, table=True):
    """
    __tablename__ = "feature_names"
    TenantMixin entrega: organization_id (FK NOT NULL), created_at,
    updated_at (UTC-aware, onupdate automatico).
    """

    id: str = Field(
        default_factory=lambda: prefixed_id("feat"),  # TODO: prefixo
        primary_key=True,
    )
    name: str = Field(max_length=200)
    # TODO: campos de dominio (max_length sempre; JSON nativo se precisar)
    # is_active: bool = Field(default=True, nullable=False)


# ============================================================
# schemas.py — app/<feature_names>/schemas.py  (VALIDACAO aqui!)
# ============================================================

from pydantic import BaseModel, Field as PydanticField


class FeatureNameCreate(BaseModel):
    """Entrada (POST). NUNCA organization_id — vem do contexto."""

    name: str = PydanticField(min_length=1, max_length=200)
    # TODO: campos com validacao (enums, EmailStr, ge/le...)


class FeatureNameUpdate(BaseModel):
    """Entrada (PATCH) — tudo opcional."""

    name: str | None = PydanticField(default=None, min_length=1, max_length=200)


class FeatureNameResponse(BaseModel):
    """Saida (GET)."""

    id: str
    organization_id: str
    name: str
    # created_at: datetime
    # updated_at: datetime


# ============================================================
# service.py — app/<feature_names>/service.py
# ============================================================

from sqlmodel import Session, func, select


class FeatureNameService:
    """Regras de FeatureName. TODA query filtra por organization_id."""

    def __init__(self, session: Session):
        self.session = session

    def get_in_organization(
        self, *, organization_id: str, feature_name_id: str
    ) -> FeatureName | None:
        """None para IDs de outros tenants — nunca vaza existencia."""
        statement = select(FeatureName).where(
            FeatureName.id == feature_name_id,
            FeatureName.organization_id == organization_id,
        )
        return self.session.exec(statement).first()

    def list_in_organization(
        self, *, organization_id: str, offset: int = 0, limit: int = 50
    ) -> tuple[list[FeatureName], int]:
        base = select(FeatureName).where(
            FeatureName.organization_id == organization_id
        )
        total = self.session.exec(
            select(func.count()).select_from(base.subquery())
        ).one()
        items = self.session.exec(
            base.order_by(FeatureName.created_at)  # type: ignore[attr-defined]
            .offset(offset)
            .limit(limit)
        ).all()
        return list(items), total

    def create(self, *, organization_id: str, data: FeatureNameCreate) -> FeatureName:
        item = FeatureName(
            organization_id=organization_id,  # SEMPRE do contexto
            **data.model_dump(),
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item


# ============================================================
# api.py — app/<feature_names>/api.py
# ============================================================

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import CurrentOrganization, CurrentUser
from app.core.errors import NotFoundError
from app.core.pagination import Page, PageParams
from app.db.session import DbSession

router = APIRouter(prefix="/feature_names", tags=["feature_names"])  # TODO


@router.get("", response_model=Page[FeatureNameResponse])
async def list_feature_names(
    session: DbSession,
    organization: CurrentOrganization,
    user: CurrentUser,
    params: Annotated[PageParams, Depends()],
) -> Page[FeatureNameResponse]:
    """Lista feature_names do tenant (paginado)."""
    items, total = FeatureNameService(session).list_in_organization(
        organization_id=organization.id,
        offset=params.offset,
        limit=params.limit,
    )
    return Page.create(items, total=total, params=params)  # type: ignore[arg-type]


@router.get("/{feature_name_id}", response_model=FeatureNameResponse)
async def get_feature_name(
    feature_name_id: str,
    session: DbSession,
    organization: CurrentOrganization,
    user: CurrentUser,
) -> FeatureNameResponse:
    """Busca por ID. 404 generico fora do tenant (nao vaza existencia)."""
    item = FeatureNameService(session).get_in_organization(
        organization_id=organization.id, feature_name_id=feature_name_id
    )
    if item is None:
        raise NotFoundError("FeatureName not found")
    return item  # type: ignore[return-value]


@router.post("", response_model=FeatureNameResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_name(
    payload: FeatureNameCreate,
    session: DbSession,
    organization: CurrentOrganization,
    user: CurrentUser,
) -> FeatureNameResponse:
    """Cria no tenant do contexto."""
    return FeatureNameService(session).create(  # type: ignore[return-value]
        organization_id=organization.id, data=payload
    )


# ============================================================
# Registro — app/api/__init__.py
# ============================================================
#
# from app.feature_names.api import router as feature_names_router
#
# api_v1_router.include_router(feature_names_router)
