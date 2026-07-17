---
name: fastapi-multi-tenant
description: |
  Padroes de API FastAPI para o Revenue SDR OS. Carregue esta skill sempre
  que for criar/modificar endpoints, dependencies, ou routers.
version: 1.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# FastAPI Multi-Tenant — Padroes do Revenue SDR OS

## Principio basico

```
Todo endpoint que toca dados de dominio:
  1. Precisa de organization_id no contexto (vem do middleware)
  2. Filtra TODA query por organization_id
  3. Retorna 404 generico se tenant nao existe (NAO 403 — nao vaza existencia)
```

---

## Estrutura de router

```python
# app/api/v1/<feature>.py
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user, get_current_organization
from app.database import get_session
from app.models.organization import Organization
from app.models.user import User

router = APIRouter(prefix="/<feature>", tags=["<feature>"])


class FeatureResponse(BaseModel):
    id: str
    name: str
    # ... campos publicos


@router.get("", response_model=List[FeatureResponse])
async def list_features(
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Lista features do tenant atual."""
    # CRITICO: sempre filtrar por organization_id
    statement = select(Feature).where(
        Feature.organization_id == organization.id
    )
    features = db.exec(statement).all()
    return features


@router.get("/{feature_id}", response_model=FeatureResponse)
async def get_feature(
    feature_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Busca feature por ID (mesmo tenant only)."""
    feature = db.get(Feature, feature_id)

    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    # CRITICO: defense in depth
    if feature.organization_id != organization.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found",  # 404 generico, nao vaza existencia
        )

    return feature


@router.post("", response_model=FeatureResponse, status_code=201)
async def create_feature(
    payload: FeatureCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Cria feature no tenant atual."""
    feature = Feature(
        organization_id=organization.id,  # SEMPRE pegar do contexto
        **payload.model_dump(),
    )
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature
```

---

## Dependencies padrao

```python
# app/auth/dependencies.py

def get_current_organization(request: Request) -> Organization:
    """Pega organization do request.state (setada pelo middleware)."""
    organization = getattr(request.state, "organization", None)
    if not organization:
        raise HTTPException(status_code=400, detail="Organization not resolved")
    return organization


def get_current_user(
    user: Annotated[Optional[User], Depends(get_current_optional_user)],
) -> User:
    """User logado ou 401."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


def require_role(*allowed_roles: str):
    """Factory: exige role especifica."""
    def role_checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Requires one of roles: {list(allowed_roles)}",
            )
        return user
    return role_checker
```

---

## Schema patterns

### ID prefixed

```python
# SEMPRE prefixar IDs pra debug facil
def _new_user_id() -> str:
    return f"user_{uuid.uuid4().hex[:12]}"

class User(SQLModel, table=True):
    id: str = Field(default_factory=_new_user_id, primary_key=True)
```

### Tenant FK obrigatoria

```python
class TenantModel(TimestampMixin, SQLModel):
    """Base: todo model de dominio PRECISA de organization_id."""
    organization_id: str = Field(
        foreign_key="organizations.id",
        index=True,
        nullable=False,
    )


class Feature(TenantModel, table=True):
    __tablename__ = "features"
    # ... outros campos
```

### Pydantic schemas separados de SQLModel

```python
# Schema de entrada (POST/PUT)
class FeatureCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


# Schema de saida (GET)
class FeatureResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: str | None
    created_at: datetime


# Schema de update (PATCH)
class FeatureUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
```

---

## Tenant resolution (3 fallbacks)

```python
# app/middleware/tenant.py

class TenantResolutionMiddleware(BaseHTTPMiddleware):
    """Resolve organization via:
      1. Subdomain (ex: clinica-bela.localhost)
      2. Header X-Tenant-Slug
      3. Query param ?tenant= (apenas dev)
      4. Default (config.DEFAULT_TENANT_SLUG)
    """

    async def dispatch(self, request, call_next):
        slug = (
            self._extract_slug_from_subdomain(request)
            or request.headers.get("X-Tenant-Slug")
            or request.url.query_params.get("tenant")
            or settings.default_tenant_slug
        )

        organization = self._load_organization(slug)
        if not organization:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Tenant '{slug}' not found"},
            )

        request.state.organization = organization
        request.state.tenant_slug = slug
        return await call_next(request)
```

---

## CORS e Security

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # de .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**JWT settings**:
- `httponly=True` (cookie nao acessivel por JS)
- `secure=True` em prod (HTTPS only)
- `samesite="lax"` (protege CSRF)
- `max_age=7 * 24 * 3600` (7 dias)

---

## Versionamento de API

```
/api/v1/auth/login    ← v1
/api/v2/auth/login    ← v2 (quando quebrar compatibilidade)
```

**Regra**: v1 mantida por minimo 6 meses apos lancamento de v2.

---

## OpenAPI / Scalar UI

FastAPI gera OpenAPI 3.1 auto em `/openapi.json`. Scalar UI em `/docs` ja vem built-in.

```python
app = FastAPI(
    title="Revenue SDR OS",
    version=__version__,
    description="White-label multi-tenant sales platform with AI SDR",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json",
)
```

---

## Erros padrao

```python
# 404 generico (NAO vaza existencia)
raise HTTPException(status_code=404, detail="Feature not found")

# 403 quando role insuficiente
raise HTTPException(status_code=403, detail="Requires admin role")

# 400 quando contexto invalido
raise HTTPException(status_code=400, detail="Organization not resolved")

# 401 quando nao autenticado
raise HTTPException(
    status_code=401,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)

# 422 automatico do Pydantic (validacao)
# FastAPI retorna automaticamente quando payload nao passa no schema
```

---

## Anti-patterns (NUNCA faca isso)

```python
# ERRADO: confiar em organization_id do payload
async def create_feature(payload: FeatureCreate):
    feature = Feature(organization_id=payload.organization_id, ...)  # NUNCA!

# CERTO: sempre pegar do contexto
async def create_feature(
    payload: FeatureCreate,
    organization: Annotated[Organization, Depends(get_current_organization)],
):
    feature = Feature(organization_id=organization.id, ...)


# ERRADO: query sem filtro de tenant
db.exec(select(Feature).where(Feature.id == id))  # NUNCA!

# CERTO: sempre filtrar
db.exec(select(Feature).where(
    Feature.id == id,
    Feature.organization_id == organization.id
))


# ERRADO: 403 em cross-tenant access
raise HTTPException(403, "Not allowed")  # vaza existencia

# CERTO: 404 generico
raise HTTPException(404, "Feature not found")
```

---

## Checklist de review

```
[ ] Endpoint declara Depends(get_current_organization) ou usa middleware
[ ] Toda query tem .where(Feature.organization_id == organization.id)
[ ] Cross-tenant access retorna 404, NAO 403
[ ] Schema Pydantic separado do SQLModel
[ ] IDs sao prefixed (org_, user_, lead_, etc)
[ ] Tenant FK e' NOT NULL + indexed
[ ] Response nao vaza dados de outros tenants
[ ] Docstring no endpoint descreve comportamento
[ ] OpenAPI tag definida
[ ] Teste de tenant isolation cobre o endpoint
```