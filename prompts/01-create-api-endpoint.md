---
task_id: 01
task_name: create-api-endpoint
version: 1.0.0
sprint: 2 (Lead Brain)
---

# Prompt 01 — Criar Endpoint REST

> **Copy-paste este prompt inteiro pra um agente de IA (Claude Code, Codex, etc).**
> **Ele sabe exatamente o que fazer.**

---

## Tarefa

Criar um endpoint REST novo no projeto Revenue SDR OS seguindo os padroes do projeto.

---

## Skills a carregar ANTES de comecar

```
1. .skills/revenue-sdr-os-architect.md     ← SEMPRE primeiro
2. .skills/fastapi-multi-tenant.md          ← obrigatorio
3. [outras conforme a tarefa]
```

---

## Contexto do projeto

```
Stack: FastAPI + SQLModel + SQLite (WAL) + HTMX + Alpine.js
Repo: ~/AGENCIA/SDR/ (clone antes de comecar)
Documentacao completa: /Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/
Multi-tenant: TODO endpoint filtra por organization_id
White-label: cores vem do banco via CSS variables
API-first: toda UI consome endpoint documentado
```

---

## Inputs que o usuario te da

Substitua os placeholders abaixo com os valores reais:

```
NOME_DO_MODEL: <ex: Lead, Conversation, Message, ...>
NOME_DO_ENDPOINT: <ex: leads, conversations, messages>
VERBO_PRINCIPAL: <GET (list), POST (create), GET /{id}, PATCH, DELETE>
DESCRICAO_FUNCIONAL: <1-2 frases do que o endpoint faz>
CAMPOS_DO_MODEL: <lista dos campos + tipos + constraints>
ROLES_PERMITIDAS: <admin, manager, closer, sdr, member - quem pode acessar?>
```

Exemplo preenchido:
```
NOME_DO_MODEL: Lead
NOME_DO_ENDPOINT: leads
VERBO_PRINCIPAL: GET (lista)
DESCRICAO_FUNCIONAL: Lista leads do tenant atual com paginacao e filtros
CAMPOS_DO_MODEL: name (str), phone (str), email (str optional), source (enum), tags (list[str])
ROLES_PERMITIDAS: admin, manager, sdr (closer e member NAO podem listar todos)
```

---

## Estrutura esperada

### 1. Arquivo a criar

```
app/api/v1/<endpoint_name>.py
```

### 2. Conteudo (use como base)

```python
"""
<Endpoint description>.
"""
from typing import Annotated, List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, EmailStr
from sqlmodel import Session, select

from app.auth.dependencies import get_current_organization, get_current_user, require_role
from app.database import get_session
from app.models.<model_name> import <ModelName>
from app.models.organization import Organization
from app.models.user import User

router = APIRouter(prefix="/<endpoint_name>", tags=["<endpoint_name>"])


# --- Schemas ---

class <ModelName>Create(BaseModel):
    """Schema de entrada (POST)."""
    name: str = Field(min_length=1, max_length=200)
    # ... outros campos


class <ModelName>Update(BaseModel):
    """Schema de atualizacao (PATCH) — todos campos opcionais."""
    name: str | None = Field(default=None, min_length=1, max_length=200)
    # ... outros campos


class <ModelName>Response(BaseModel):
    """Schema de saida (GET)."""
    id: str
    organization_id: str
    name: str
    created_at: datetime
    # ... outros campos


# --- Endpoints ---

@router.get("", response_model=List[<ModelName>Response])
async def list_<endpoint_name>(
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Lista <endpoint> do tenant atual com paginacao."""
    statement = (
        select(<ModelName>)
        .where(<ModelName>.organization_id == organization.id)
        .offset(skip)
        .limit(limit)
    )
    items = db.exec(statement).all()
    return items


@router.post("", response_model=<ModelName>Response, status_code=201)
async def create_<endpoint_singular>(
    payload: <ModelName>Create,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Cria novo <endpoint_singular> no tenant atual."""
    item = <ModelName>(
        organization_id=organization.id,  # SEMPRE do contexto
        **payload.model_dump(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=<ModelName>Response)
async def get_<endpoint_singular>(
    item_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Busca <endpoint_singular> por ID (mesmo tenant only)."""
    item = db.get(<ModelName>, item_id)
    if not item or item.organization_id != organization.id:
        # 404 generico, NAO vaza existencia
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=<ModelName>Response)
async def update_<endpoint_singular>(
    item_id: str,
    payload: <ModelName>Update,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Atualiza <endpoint_singular> parcialmente."""
    item = db.get(<ModelName>, item_id)
    if not item or item.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_<endpoint_singular>(
    item_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Deleta <endpoint_singular>."""
    item = db.get(<ModelName>, item_id)
    if not item or item.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return None
```

### 3. Adicionar ao router principal

```python
# app/api/v1/__init__.py
from app.api.v1 import <endpoint_name>  # adicionar
api_router.include_router(<endpoint_name>.router)
```

### 4. (Se for Sprint 2+) Criar migration Alembic

```bash
# Gera migration automaticamente baseado nos models
cd ~/AGENCIA/SDR
source .venv/bin/activate
alembic revision --autogenerate -m "add <model_name> table"
alembic upgrade head
```

### 5. Criar testes de tenant isolation

```python
# tests/test_<endpoint_name>_isolation.py

def test_list_<endpoint_name>_only_returns_own_org(client, seed_two_orgs, auth_headers_org_a):
    org_a, org_b, user_a, user_b = seed_two_orgs
    response = client.get("/api/v1/<endpoint_name>", headers=auth_headers_org_a)
    assert response.status_code == 200
    items = response.json()
    item_ids = [i["id"] for i in items]
    # So itens do Org A, NAO do Org B
    assert user_a.id not in item_ids  # exemplo


def test_get_<endpoint_singular>_cross_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a):
    """Cross-tenant access retorna 404 generico."""
    org_a, org_b, user_a, user_b = seed_two_orgs
    # Cria item em Org B
    # Tenta acessar via Org A → 404
```

---

## Validacao obrigatoria

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate

# 1. Codigo compila
python -c "from app.main import app; print('OK')"

# 2. Server sobe
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
sleep 3
curl http://127.0.0.1:8000/api/v1/health/

# 3. Endpoint funciona (autenticado)
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"email":"admin@clinica-bela.com","password":"senha123"}'

# (pega o access_token da resposta)
TOKEN="..."

curl http://127.0.0.1:8000/api/v1/<endpoint_name> \
  -H "Authorization: Bearer ***" \
  -H "X-Tenant-Slug: clinica-bela"

# 4. Cross-tenant bloqueado
curl http://127.0.0.1:8000/api/v1/<endpoint_name> \
  -H "Authorization: Bearer ***" \
  -H "X-Tenant-Slug: imob-center"
# Resultado esperado: retorna dados da Org A (porque header manda), nao da B

# 5. OpenAPI mostra novo endpoint
curl http://127.0.0.1:8000/openapi.json | python -m json.tool | grep "<endpoint_name>"

# 6. Testes passam
pytest tests/test_<endpoint_name>_isolation.py -v
pytest -v

# 7. Migration funciona
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

---

## Checklist final

```
[ ] Codigo compila sem warnings
[ ] Endpoint declarado em app/api/v1/<endpoint_name>.py
[ ] Router adicionado em app/api/v1/__init__.py
[ ] Toda query tem .where(Model.organization_id == organization.id)
[ ] Cross-tenant access retorna 404 (NAO 403)
[ ] Schemas Pydantic separados do SQLModel
[ ] Docstrings em todas funcoes
[ ] Type hints em todas funcoes
[ ] OpenAPI tag definida
[ ] Migration criada e testada (upgrade + downgrade)
[ ] Testes de tenant isolation criados
[ ] pytest -v passa
[ ] curl health + endpoint funciona
[ ] Commit message: feat: add <endpoint_name> CRUD with tenant isolation
[ ] Push feito
```

---

## Entrega esperada

Ao terminar, reporte ao usuario:

1. **O que foi feito** (1 paragrafo)
2. **Arquivos criados/modificados** (lista)
3. **Como testar** (curl commands)
4. **Limitacoes conhecidas** (se houver)
5. **Sugestoes para proxima iteracao** (opcional)

---

*"Nunca mais perca um lead por falta de acompanhamento."*