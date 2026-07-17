---
sprint: 02
task: 04-create-leads-api
---

# Prompt 02.04 — Criar API CRUD de Leads

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
- Service: `app/services/lead_merge.py` (find_existing_lead, merge_lead_data, log_merge_event)
- Middleware de tenant resolution

Agora voce precisa criar a **API REST CRUD de leads** com merge automatico.

Repo: `~/AGENCIA/SDR/`

---

## Tasks

### T1: Criar `app/api/v1/leads.py`

Use o template `/Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/templates/fastapi-route.py` como base.

```python
"""
Leads API — CRUD com merge automatico (Lead Brain).
"""
import json
from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session, select

from app.auth.dependencies import (
    get_current_organization,
    get_current_user,
)
from app.database import get_session
from app.models.lead import Lead, LeadTimelineEvent, _new_event_id, LEAD_SOURCES, LEAD_STATUSES
from app.models.organization import Organization
from app.models.user import User
from app.services.lead_merge import find_existing_lead, merge_lead_data, log_merge_event

router = APIRouter(prefix="/leads", tags=["leads"])


# --- Schemas ---

class LeadCreate(BaseModel):
    """Schema de entrada (POST)."""
    name: str = Field(min_length=1, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    document: Optional[str] = Field(default=None, max_length=50)
    source: str = Field(max_length=50)
    source_detail: Optional[dict] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: dict = Field(default_factory=dict)
    assigned_user_id: Optional[str] = None


class LeadUpdate(BaseModel):
    """Schema de atualizacao (PATCH) — todos campos opcionais."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    document: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=20)
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None
    assigned_user_id: Optional[str] = None


class LeadResponse(BaseModel):
    """Schema de saida (GET)."""
    id: str
    organization_id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    document: Optional[str]
    source: str
    source_detail: dict
    tags: List[str]
    custom_fields: dict
    status: str
    assigned_user_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_interaction_at: Optional[datetime]


def _lead_to_response(lead: Lead) -> LeadResponse:
    """Converte SQLModel Lead para LeadResponse."""
    return LeadResponse(
        id=lead.id,
        organization_id=lead.organization_id,
        name=lead.name,
        phone=lead.phone,
        email=lead.email,
        document=lead.document,
        source=lead.source,
        source_detail=json.loads(lead.source_detail or "{}"),
        tags=json.loads(lead.tags or "[]"),
        custom_fields=json.loads(lead.custom_fields or "{}"),
        status=lead.status,
        assigned_user_id=lead.assigned_user_id,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        last_interaction_at=lead.last_interaction_at,
    )


# --- Endpoints ---

@router.get("", response_model=List[LeadResponse])
async def list_leads(
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None, description="Busca em name/phone/email"),
    tag: Optional[str] = Query(None),
):
    """Lista leads do tenant atual."""
    statement = select(Lead).where(
        Lead.organization_id == organization.id,
        Lead.status != "deletado",  # NAO retorna deletados
    )

    if status_filter:
        statement = statement.where(Lead.status == status_filter)

    if search:
        like = f"%{search}%"
        statement = statement.where(
            (Lead.name.ilike(like)) |
            (Lead.phone.ilike(like)) |
            (Lead.email.ilike(like))
        )

    if tag:
        # tags e' JSON serializado; busca simples
        statement = statement.where(Lead.tags.contains(f'"{tag}"'))

    statement = statement.offset(skip).limit(limit).order_by(Lead.created_at.desc())

    leads = db.exec(statement).all()
    return [_lead_to_response(l) for l in leads]


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Cria lead. Se telefone/email ja existe no tenant, faz merge automatico."""
    # 1. Validar source
    if payload.source not in LEAD_SOURCES:
        raise HTTPException(status_code=400, detail=f"Invalid source. Allowed: {LEAD_SOURCES}")

    # 2. Normalizar
    phone = payload.phone.strip() if payload.phone else None
    email = payload.email.lower().strip() if payload.email else None

    # 3. Buscar lead existente (Lead Brain)
    existing = find_existing_lead(
        db,
        organization_id=organization.id,
        phone=phone,
        email=email,
    )

    if existing:
        # MERGE: preenche campos vazios no existente
        merged = merge_lead_data(existing, {
            "name": payload.name,
            "phone": phone,
            "email": email,
            "document": payload.document,
            "source": payload.source,
            "source_detail": json.dumps(payload.source_detail or {}),
            "tags": json.dumps(list(set(json.loads(existing.tags or "[]") + payload.tags))),
        })

        # Loga evento de merge
        log_merge_event(
            db,
            organization_id=organization.id,
            existing_lead_id=existing.id,
            new_lead_id="merge",  # placeholder, lead nao foi criado
            merged_fields=[k for k in payload.model_dump() if k != "source"],
            actor_user_id=current_user.id,
        )

        db.add(merged)
        db.commit()
        db.refresh(merged)
        return _lead_to_response(merged)

    # 4. Criar novo lead
    new_lead = Lead(
        organization_id=organization.id,
        name=payload.name,
        phone=phone,
        email=email,
        document=payload.document,
        source=payload.source,
        source_detail=json.dumps(payload.source_detail or {}),
        tags=json.dumps(payload.tags),
        custom_fields=json.dumps(payload.custom_fields),
        status="novo",
        assigned_user_id=payload.assigned_user_id,
        last_interaction_at=datetime.utcnow(),
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    # 5. Loga evento de criacao
    event = LeadTimelineEvent(
        id=_new_event_id(),
        organization_id=organization.id,
        lead_id=new_lead.id,
        event_type="created",
        payload=json.dumps({"source": new_lead.source}),
        actor_user_id=current_user.id,
    )
    db.add(event)
    db.commit()

    return _lead_to_response(new_lead)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Busca lead por ID (mesmo tenant only)."""
    lead = db.get(Lead, lead_id)
    if not lead or lead.organization_id != organization.id or lead.status == "deletado":
        raise HTTPException(status_code=404, detail="Lead not found")
    return _lead_to_response(lead)


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    payload: LeadUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Atualiza lead parcialmente."""
    lead = db.get(Lead, lead_id)
    if not lead or lead.organization_id != organization.id or lead.status == "deletado":
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = payload.model_dump(exclude_unset=True)

    # Track changes for timeline
    changes = {}
    for key, value in update_data.items():
        if key in ("tags", "custom_fields"):
            value = json.dumps(value)
        old_value = getattr(lead, key)
        if old_value != value:
            changes[key] = {"from": old_value, "to": value}
        setattr(lead, key, value)

    if changes:
        lead.updated_at = datetime.utcnow()
        lead.last_interaction_at = datetime.utcnow()

        # Loga evento
        event = LeadTimelineEvent(
            id=_new_event_id(),
            organization_id=organization.id,
            lead_id=lead.id,
            event_type="updated",
            payload=json.dumps({"changes": changes}),
            actor_user_id=current_user.id,
        )
        db.add(event)

    db.add(lead)
    db.commit()
    db.refresh(lead)
    return _lead_to_response(lead)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
):
    """Soft delete (LGPD): marca status='deletado', NAO remove do banco."""
    lead = db.get(Lead, lead_id)
    if not lead or lead.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead.status == "deletado":
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.status = "deletado"
    lead.updated_at = datetime.utcnow()

    # Loga evento
    event = LeadTimelineEvent(
        id=_new_event_id(),
        organization_id=organization.id,
        lead_id=lead.id,
        event_type="deleted",
        payload=json.dumps({"reason": "user_request"}),
        actor_user_id=current_user.id,
    )
    db.add(event)
    db.commit()
    return None


# --- Timeline endpoint ---

@router.get("/{lead_id}/timeline", response_model=List[dict])
async def get_lead_timeline(
    lead_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    organization: Annotated[Organization, Depends(get_current_organization)],
    db: Annotated[Session, Depends(get_session)],
    limit: int = Query(100, ge=1, le=500),
):
    """Retorna timeline do lead (eventos em ordem cronologica reversa)."""
    # Verifica que lead pertence ao tenant
    lead = db.get(Lead, lead_id)
    if not lead or lead.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Lead not found")

    statement = (
        select(LeadTimelineEvent)
        .where(LeadTimelineEvent.lead_id == lead_id)
        .order_by(LeadTimelineEvent.created_at.desc())
        .limit(limit)
    )
    events = db.exec(statement).all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "payload": json.loads(e.payload or "{}"),
            "actor_user_id": e.actor_user_id,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]
```

### T2: Registrar router em `app/api/v1/__init__.py`

```python
from app.api.v1 import leads

api_router.include_router(leads.router)
```

---

## Validacao

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate

# 1. Server sobe
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
sleep 3

# 2. Login
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"email":"admin@clinica-bela.com","password":"senha123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. Criar lead
curl -X POST http://127.0.0.1:8000/api/v1/leads \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{
    "name": "João Silva",
    "phone": "+5511999998888",
    "email": "joao@example.com",
    "source": "whatsapp"
  }'

# 4. Criar de novo com mesmo telefone (deve fazer MERGE)
curl -X POST http://127.0.0.1:8000/api/v1/leads \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{
    "name": "João Silva Santos",
    "phone": "+5511999998888",
    "email": "joao.santos@example.com",
    "source": "site"
  }'

# Esperado: retorna o lead ORIGINAL (mesmo ID), com campos preenchidos se vazios

# 5. Listar leads
curl http://127.0.0.1:8000/api/v1/leads \
  -H "Authorization: Bearer ***" \
  -H "X-Tenant-Slug: clinica-bela"

# 6. Buscar por ID
curl http://127.0.0.1:8000/api/v1/leads/<id> \
  -H "Authorization: Bearer ***" \
  -H "X-Tenant-Slug: clinica-bela"

# 7. Atualizar
curl -X PATCH http://127.0.0.1:8000/api/v1/leads/<id> \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"status": "qualificado", "tags": ["VIP"]}'

# 8. Timeline
curl http://127.0.0.1:8000/api/v1/leads/<id>/timeline \
  -H "Authorization: Bearer ***" \
  -H "X-Tenant-Slug: clinica-bela"

# 9. Soft delete
curl -X DELETE http://127.0.0.1:8000/api/v1/leads/<id> \
  -H "Authorization: Bearer ***" \
  -H "X-Tenant-Slug: clinica-bela"

# 10. Tentar acessar lead deletado → 404
curl http://127.0.0.1:8000/api/v1/leads/<id> \
  -H "Authorization: Bearer ***" \
  -H "X-Tenant-Slug: clinica-bela"
```

---

## Checklist

```
[ ] app/api/v1/leads.py criado com 6 endpoints
[ ] POST faz merge automatico se telefone/email duplicado
[ ] POST retorna 400 se source invalido
[ ] GET lista filtra status='deletado'
[ ] GET permite busca por name/phone/email
[ ] GET permite filtro por status e tag
[ ] GET /{id} retorna 404 se cross-tenant
[ ] GET /{id} retorna 404 se soft-deletado
[ ] PATCH loga evento de updated com changes
[ ] DELETE faz soft delete (NAO remove do banco)
[ ] Timeline retorna eventos em ordem cronologica reversa
[ ] Router registrado em app/api/v1/__init__.py
[ ] pytest tests/test_leads.py -v passa
[ ] pytest tests/test_lead_isolation.py -v passa
[ ] curl manual funciona para todos endpoints
```

---

*"Lead e' pessoa. Trate com memoria."*