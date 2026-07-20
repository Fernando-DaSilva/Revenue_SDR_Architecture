---
name: fastapi-multi-tenant
description: |
  Padroes de API FastAPI para o Revenue SDR OS. Carregue esta skill sempre
  que for criar/modificar endpoints, dependencies, services ou routers.
version: 2.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# FastAPI Multi-Tenant — Padroes do Revenue SDR OS (v2.0)

## Principio basico

```
Todo endpoint que toca dados de dominio:
  1. Recebe a Organization do contexto (middleware resolveu)
  2. Filtra TODA query por organization_id (no service)
  3. Retorna 404 generico cross-tenant (NAO 403 — nao vaza existencia)
  4. Erros via AppError -> envelope {"error": {code, message, details}}
```

---

## Estrutura de um dominio (pacote)

```
app/<feature>/
+-- models.py      # tabelas SQLModel (TenantMixin!)
+-- schemas.py     # pydantic de entrada/saida (VALIDACAO vive aqui)
+-- service.py     # regras de negocio + queries (SEMPRE por tenant)
+-- api.py         # rotas finas: parse -> service -> response
```

Rotas HTML ficam em `app/web/pages/<feature>.py`; templates em
`app/web/templates/<feature>/`.

## Rota (fina) — app/<feature>/api.py

```python
"""API JSON de <features> (/api/v1/<features>)."""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import CurrentOrganization, CurrentUser
from app.core.errors import NotFoundError
from app.core.pagination import Page, PageParams
from app.db.session import DbSession
from app.<feature>.schemas import FeatureCreate, FeatureResponse
from app.<feature>.service import FeatureService

router = APIRouter(prefix="/<features>", tags=["<features>"])


@router.get("", response_model=Page[FeatureResponse])
async def list_features(
    session: DbSession,                          # sessao por request
    organization: CurrentOrganization,           # tenant do middleware
    user: CurrentUser,                           # cookie OU Bearer
    params: Annotated[PageParams, Depends()],    # ?offset=&limit=
) -> Page[FeatureResponse]:
    """Lista <features> do tenant (paginado)."""
    service = FeatureService(session)
    items, total = service.list_in_organization(
        organization_id=organization.id, offset=params.offset, limit=params.limit
    )
    return Page.create(items, total=total, params=params)


@router.get("/{feature_id}", response_model=FeatureResponse)
async def get_feature(
    feature_id: str,
    session: DbSession,
    organization: CurrentOrganization,
    user: CurrentUser,
) -> FeatureResponse:
    """Busca por ID dentro do tenant. 404 generico fora do tenant."""
    feature = FeatureService(session).get_in_organization(
        organization_id=organization.id, feature_id=feature_id
    )
    if feature is None:
        raise NotFoundError("<Feature> not found")
    return feature


@router.post("", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_feature(
    payload: FeatureCreate,
    session: DbSession,
    organization: CurrentOrganization,
    user: CurrentUser,
) -> FeatureResponse:
    """Cria <feature> no tenant do contexto (NUNCA do payload)."""
    return FeatureService(session).create(
        organization_id=organization.id, data=payload, actor_user_id=user.id
    )
```

## Service — app/<feature>/service.py

```python
"""Regras de <feature>. Toda query filtra por organization_id."""
from sqlmodel import Session, func, select

from app.<feature>.models import Feature


class FeatureService:
    def __init__(self, session: Session):
        self.session = session

    def get_in_organization(self, *, organization_id: str, feature_id: str):
        """Retorna None para IDs de outros tenants — nunca vaza existencia."""
        statement = select(Feature).where(
            Feature.id == feature_id,
            Feature.organization_id == organization_id,
        )
        return self.session.exec(statement).first()

    def list_in_organization(self, *, organization_id: str, offset: int, limit: int):
        base = select(Feature).where(Feature.organization_id == organization_id)
        total = self.session.exec(select(func.count()).select_from(base.subquery())).one()
        items = self.session.exec(
            base.order_by(Feature.created_at).offset(offset).limit(limit)  # type: ignore[attr-defined]
        ).all()
        return list(items), total
```

## Schemas — app/<feature>/schemas.py (VALIDACAO vive aqui)

```python
"""Contratos de API de <feature>. Table models NAO validam entrada."""
from pydantic import BaseModel, Field


class FeatureCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class FeatureUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None


class FeatureResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: str | None
```

## Model — app/<feature>/models.py

```python
"""Tabelas de <feature>. Herda TenantMixin: organization_id obrigatorio."""
from sqlmodel import Field

from app.db.base import TenantMixin, prefixed_id


class Feature(TenantMixin, table=True):
    __tablename__ = "features"

    id: str = Field(default_factory=lambda: prefixed_id("feat"), primary_key=True)
    name: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)
```

---

## Dependencies padrao (ja existem — NAO recriar)

```python
from app.auth.dependencies import (
    CurrentOrganization,   # Organization do tenant resolvido (404 se nao houver)
    CurrentUser,           # User autenticado via cookie|Bearer (401 padronizado)
    OptionalUser,          # User | None (paginas publicas)
    require_role,          # require_role(Role.ADMIN, Role.MANAGER)
)
from app.db.session import DbSession              # sessao por request
from app.core.pagination import Page, PageParams  # paginacao padrao
```

## Erros (envelope) — app/core/errors.py

```python
from app.core.errors import (
    AppError,               # base: status_code + code + message + details
    AuthenticationError,    # 401 authentication_failed
    PermissionDeniedError,  # 403 permission_denied (role insuficiente)
    NotFoundError,          # 404 not_found (e cross-tenant generico)
    TenantNotFoundError,    # 404 tenant_not_found
    ConflictError,          # 409 conflict
)

# Resposta ao client (automatica via handler):
# {"error": {"code": "not_found", "message": "<Feature> not found", "details": {}}}
```

**Mapeamento**:
- 401 nao autenticado -> `AuthenticationError`
- 403 role insuficiente -> `PermissionDeniedError`
- 404 nao achou / cross-tenant -> `NotFoundError`
- 409 conflito (ex: duplicata) -> `ConflictError`
- 422 validacao -> automatico do pydantic (handler normaliza)

## Tenant resolution (middleware — ja implementado)

Precedencia: `custom_domain` (Host) ou subdominio -> header
`X-Tenant-Slug` -> query param `?tenant=` (so dev) -> `DEFAULT_TENANT_SLUG`.
Seta `request.state.organization` + ContextVar `current_organization`.
Rotas publicas: `/`, `/docs`, `/openapi.json`, `/static/*`, health checks.

## Versionamento de API

```
/api/v1/...   <- vigente
/api/v2/...   <- quando quebrar compatibilidade (v1 mantida 6+ meses)
```

---

## Anti-patterns (NUNCA faca)

```python
# ERRADO: organization_id do payload
feature = Feature(organization_id=payload.organization_id, ...)   # NUNCA!
# CERTO: do contexto
feature = Feature(organization_id=organization.id, ...)

# ERRADO: query sem filtro de tenant
session.exec(select(Feature).where(Feature.id == feature_id))
# CERTO
session.exec(select(Feature).where(
    Feature.id == feature_id,
    Feature.organization_id == organization_id,
))

# ERRADO: 403 em cross-tenant (vaza existencia)
raise PermissionDeniedError("Not allowed")
# CERTO: 404 generico
raise NotFoundError("Feature not found")

# ERRADO: HTTPException solta
raise HTTPException(status_code=404, detail="...")
# CERTO: AppError com envelope consistente
raise NotFoundError("...")

# ERRADO: query na rota
@router.get("")
async def list_(session: DbSession):
    return session.exec(select(Feature)...)  # NUNCA!
# CERTO: rota fina -> service
```

---

## Checklist de review

```
[ ] Rota fina: so parse -> service -> response (sem query na rota)
[ ] Toda query filtra organization_id (no service)
[ ] Cross-tenant = 404 generico (NotFoundError), NAO 403
[ ] organization_id SEMPRE do contexto, NUNCA do payload
[ ] Validacao de entrada no schema pydantic (nao no table model)
[ ] Model herda TenantMixin; ID via prefixed_id("<prefix>")
[ ] Erros via AppError (envelope), codigos estaveis
[ ] Paginacao com Page/PageParams em listagens
[ ] Endpoint coberto por teste de isolamento cross-tenant
[ ] Docstring PT-BR sem acentos; tag OpenAPI definida
```
