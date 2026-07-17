---
sprint: 02
task: 05-create-memories-api
---

# Prompt 02.05 — Criar API de Memories

> **Copy-paste este prompt inteiro pra um agente de IA.**

---

## Skills a carregar

```
1. .skills/revenue-sdr-os-architect.md
2. .skills/fastapi-multi-tenant.md
3. .skills/pytest-tenant-isolation.md
```

---

## Contexto

Ja existem:
- Models: Lead, LeadMemory, LeadTimelineEvent
- Leads API (com merge automatico)
- Service: lead_merge

Agora voce precisa criar a **API de Memories** (CRUD dentro de um lead) — Memory Brain.

Repo: `~/AGENCIA/SDR/`

---

## Tasks

### T1: Criar `app/api/v1/memories.py`

```python
"""
Lead Memories API — Memory Brain.

CRUD de notas estruturadas sobre um lead (preferencias, objecoes,
contexto financeiro, datas importantes, etc).
"""
import json
from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.auth.dependencies import (
    get_current_organization,
    get_current_user,
)
from app.database import get_session
from app.models.lead import Lead, LeadMemory, LeadTimelineEvent, MEMORY_CATEGORIES, _new_event_id
from app.models.organization import Organization
from app.models.user import User

router = APIRouter(prefix="/leads", tags=["memories"])


# --- Schemas ---

class MemoryCreate(BaseModel):
    """Schema de entrada (POST)."""
    category: str = Field(max_length=50)
    key: str = Field(max_length=100)
    value: str = Field(max_length=10000)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = Field(default="manual", max_length=50)


class MemoryUpdate(BaseModel):
    """Schema de atualizacao (PATCH)."""
    value: Optional[str] = Field(default=None, max_length=10000)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class MemoryResponse(BaseModel):
    """Schema de saida (GET)."""
    id: str
    lead_id: str
    organization_id: str
    category: str
    key: str
    value: str
    confidence: float
    source: str
    created_at: datetime
    updated_at: Optional[datetime]


def _memory_to_response(mem: LeadMemory) -> MemoryResponse:
    return MemoryResponse(
        id=mem.id,
        lead_id=mem.lead_id,
        organization_id=mem.organization_id,
        category=mem.category,
        key=mem.key,
        value=mem.value,
        confidence=mem.confidence,
        source=mem.source,
        created_at=mem.created_at,
        updated_at=mem.updated_at,
    )


# --- Helpers ---

def _check_lead_access(db: Session, lead_id: str, organization_id: str) -> Lead:
    """Verifica que lead existe e pertence ao tenant."""
    lead = db.get(Lead, lead_id)
    if not lead or lead.organization_id != organization_id or lead.status == "deletado":
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


def _log_event(
    db: Session,
    organization_id: str,
    lead_id: str,
    event_type: str,
    payload: dict,
    actor_user_id: str,
):
    """Adiciona evento ao timeline."""
    event = LeadTimelineEvent(
        id=_new_event_id(),
        organization_id=organization_id,
        lead_id=lead_id,
        event_type=event_type,
        payload=json.dumps(payload),
        actor_user_id=actor_user_id,
    )
    db.add(event)


# --- Endpoints ---

@router.get("/{lead_id}/memories", response_model=List[MemoryResponse])
async def list_memories(
    lead_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
    category: Optional[str] = Query(None),
):
    """Lista memories de um lead."""
    _check_lead_access(db, lead_id, organization.id)

    statement = select(LeadMemory).where(
        LeadMemory.lead_id == lead_id,
        LeadMemory.organization_id == organization.id,
    )
    if category:
        statement = statement.where(LeadMemory.category == category)

    statement = statement.order_by(LeadMemory.created_at.desc())
    memories = db.exec(statement).all()
    return [_memory_to_response(m) for m in memories]


@router.post(
    "/{lead_id}/memories",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_memory(
    lead_id: str,
    payload: MemoryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Adiciona memory a um lead (manual ou detectado por IA)."""
    # 1. Verifica lead
    lead = _check_lead_access(db, lead_id, organization.id)

    # 2. Validar category
    if payload.category not in MEMORY_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Allowed: {MEMORY_CATEGORIES}",
        )

    # 3. Criar memory
    memory = LeadMemory(
        organization_id=organization.id,
        lead_id=lead_id,
        category=payload.category,
        key=payload.key.strip(),
        value=payload.value.strip(),
        confidence=payload.confidence,
        source=payload.source,
    )
    db.add(memory)

    # 4. Loga evento
    _log_event(
        db,
        organization.id,
        lead_id,
        "memory_added",
        {"category": payload.category, "key": payload.key},
        current_user.id,
    )

    # 5. Atualiza last_interaction_at do lead
    lead.last_interaction_at = datetime.utcnow()
    db.add(lead)

    db.commit()
    db.refresh(memory)
    return _memory_to_response(memory)


@router.patch(
    "/{lead_id}/memories/{memory_id}",
    response_model=MemoryResponse,
)
async def update_memory(
    lead_id: str,
    memory_id: str,
    payload: MemoryUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Atualiza value ou confidence de uma memory."""
    _check_lead_access(db, lead_id, organization.id)

    memory = db.get(LeadMemory, memory_id)
    if not memory or memory.lead_id != lead_id or memory.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Memory not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "value":
            value = value.strip()
        setattr(memory, key, value)
    memory.updated_at = datetime.utcnow()

    _log_event(
        db,
        organization.id,
        lead_id,
        "memory_updated",
        {"memory_id": memory_id, "fields": list(update_data.keys())},
        current_user.id,
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)
    return _memory_to_response(memory)


@router.delete(
    "/{lead_id}/memories/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_memory(
    lead_id: str,
    memory_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Deleta uma memory (irreversivel)."""
    _check_lead_access(db, lead_id, organization.id)

    memory = db.get(LeadMemory, memory_id)
    if not memory or memory.lead_id != lead_id or memory.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Memory not found")

    _log_event(
        db,
        organization.id,
        lead_id,
        "memory_deleted",
        {"memory_id": memory_id, "category": memory.category, "key": memory.key},
        current_user.id,
    )

    db.delete(memory)
    db.commit()
    return None


# --- Bulk endpoint (usado pela deteccao automatica em mensagens) ---

@router.post("/{lead_id}/memories/bulk", response_model=List[MemoryResponse])
async def bulk_create_memories(
    lead_id: str,
    memories: List[MemoryCreate],
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Cria varias memories de uma vez (usado pelo extractor automatico)."""
    _check_lead_access(db, lead_id, organization.id)

    created = []
    for payload in memories:
        if payload.category not in MEMORY_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category: {payload.category}",
            )

        memory = LeadMemory(
            organization_id=organization.id,
            lead_id=lead_id,
            category=payload.category,
            key=payload.key.strip(),
            value=payload.value.strip(),
            confidence=payload.confidence,
            source=payload.source,
        )
        db.add(memory)
        created.append(memory)

    _log_event(
        db,
        organization.id,
        lead_id,
        "memory_bulk_added",
        {"count": len(created)},
        current_user.id,
    )

    db.commit()
    for m in created:
        db.refresh(m)
    return [_memory_to_response(m) for m in created]
```

### T2: Registrar router em `app/api/v1/__init__.py`

```python
from app.api.v1 import memories  # adicionar

api_router.include_router(memories.router)
```

---

## Validacao

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate

# 1. Login + pegar token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"email":"admin@clinica-bela.com","password":"senha123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Criar lead (se nao existir)
LEAD_ID=$(curl -s -X POST http://127.0.0.1:8000/api/v1/leads \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"name":"Maria","phone":"+5511988887777","source":"whatsapp"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['id'])")

# 3. Adicionar memories
curl -X POST http://127.0.0.1:8000/api/v1/leads/$LEAD_ID/memories \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"category":"personal","key":"conjuge","value":"João","confidence":1.0,"source":"manual"}'

curl -X POST http://127.0.0.1:8000/api/v1/leads/$LEAD_ID/memories \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"category":"objection","key":"preco","value":"Acha caro mas tem interesse","confidence":0.7,"source":"conversation_detected"}'

# 4. Listar memories
curl http://127.0.0.1:8000/api/v1/leads/$LEAD_ID/memories \
  -H "Authorization: Bearer ***" \
  -H "X-Tenant-Slug: clinica-bela"

# 5. Listar filtrado por categoria
curl "http://127.0.0.1:8000/api/v1/leads/$LEAD_ID/memories?category=objection" \
  -H "Authorization: Bearer ***" \
  -H "X-Tenant-Slug: clinica-bela"

# 6. Bulk
curl -X POST http://127.0.0.1:8000/api/v1/leads/$LEAD_ID/memories/bulk \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '[
    {"category":"financial","key":"orcamento_max","value":"R$ 5000"},
    {"category":"temporal","key":"viagem","value":"Agosto 2026"}
  ]'

# 7. Atualizar memory
MEMORY_ID=$(curl -s http://127.0.0.1:8000/api/v1/leads/$LEAD_ID/memories \
  -H "Authorization: Bearer ***" \
  -H "X-Tenant-Slug: clinica-bela" \
  | python -c "import sys, json; print(json.load(sys.stdin)[0]['id'])")

curl -X PATCH http://127.0.0.1:8000/api/v1/leads/$LEAD_ID/memories/$MEMORY_ID \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"confidence":0.95}'

# 8. Timeline (deve incluir memory_added, memory_updated, memory_bulk_added)
curl http://127.0.0.1:8000/api/v1/leads/$LEAD_ID/timeline \
  -H "Authorization: Bearer ***" \
  -H "X-Tenant-Slug: clinica-bela"
```

---

## Checklist

```
[ ] app/api/v1/memories.py criado com 5 endpoints
[ ] POST valida category contra MEMORY_CATEGORIES
[ ] POST atualiza last_interaction_at do lead
[ ] POST loga evento memory_added
[ ] PATCH loga evento memory_updated
[ ] DELETE loga evento memory_deleted (audit)
[ ] BULK cria varias + loga memory_bulk_added
[ ] Cross-tenant: memory de outro lead NAO e' encontrada
[ ] Cross-tenant: memory de outro tenant NAO e' encontrada
[ ] Router registrado em app/api/v1/__init__.py
[ ] pytest tests/test_memories.py -v passa
[ ] curl manual funciona
```

---

*"Memory e' o que diferencia um SDR de um chatbot."*