# Prompt — Criar Endpoint de API (generico)

> Spec reutilizavel para criar qualquer endpoint REST no Revenue SDR OS.
> Padroes completos: `.skills/fastapi-multi-tenant.md` (v2.0).

---

## Contexto

Repo: `~/AGENCIA/SDR/` (v0.2.0). Arquitetura de pacotes de dominio:

```
app/<feature>/
+-- models.py      # tabelas (TenantMixin)
+-- schemas.py     # pydantic entrada/saida (VALIDACAO)
+-- service.py     # regras + queries (filtradas por tenant)
+-- api.py         # rotas finas
```

## Passo a passo

### 1. Criar/atualizar o schema pydantic (VALIDACAO)

```python
# app/<feature>/schemas.py
from pydantic import BaseModel, Field


class <Feature>Create(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    # NUNCA organization_id — vem do contexto
```

### 2. Criar o service (regras + queries)

```python
# app/<feature>/service.py
from sqlmodel import Session, select

from app.<feature>.models import <Feature>


class <Feature>Service:
    def __init__(self, session: Session):
        self.session = session

    def get_in_organization(self, *, organization_id: str, <feature>_id: str):
        statement = select(<Feature>).where(
            <Feature>.id == <feature>_id,
            <Feature>.organization_id == organization_id,   # SEMPRE
        )
        return self.session.exec(statement).first()
```

### 3. Criar a rota (fina)

```python
# app/<feature>/api.py
from fastapi import APIRouter, status

from app.auth.dependencies import CurrentOrganization, CurrentUser
from app.core.errors import NotFoundError
from app.db.session import DbSession
from app.<feature>.schemas import <Feature>Create, <Feature>Response
from app.<feature>.service import <Feature>Service

router = APIRouter(prefix="/<features>", tags=["<features>"])


@router.get("/{<feature>_id}", response_model=<Feature>Response)
async def get_<feature>(
    <feature>_id: str,
    session: DbSession,
    organization: CurrentOrganization,
    user: CurrentUser,
) -> <Feature>Response:
    """Busca <feature> por ID (404 generico fora do tenant)."""
    item = <Feature>Service(session).get_in_organization(
        organization_id=organization.id, <feature>_id=<feature>_id
    )
    if item is None:
        raise NotFoundError("<Feature> not found")
    return item
```

### 4. Registrar o router

```python
# app/api/__init__.py
from app.<feature>.api import router as <feature>_router

api_v1_router.include_router(<feature>_router)
```

### 5. Testes obrigatorios

```python
# tests/test_<feature>_api.py
- happy path (create/get/list/update/delete)
- erro de validacao (422 com envelope)
- 404 generico cross-tenant
- token de outro tenant -> 401
- organization_id do payload ignorado (usa o do contexto)
```

## Validacao

```bash
pytest tests/test_<feature>_api.py -v
ruff check app/<feature>/
curl localhost:8000/openapi.json | python -c \
  "import json,sys; print('/api/v1/<features>' in json.load(sys.stdin)['paths'])"
```

## Checklist

```
[ ] Schema valida entrada (tamanhos, enums, EmailStr)
[ ] Rota fina: parse -> service -> response
[ ] Toda query filtra organization_id
[ ] Cross-tenant = 404 generico (NotFoundError)
[ ] organization_id do contexto, NUNCA do payload
[ ] Erros via AppError (envelope)
[ ] Listagens com Page/PageParams
[ ] Router registrado; /docs mostra o endpoint
[ ] Testes: CRUD + isolamento + envelope
[ ] ruff limpo
```
