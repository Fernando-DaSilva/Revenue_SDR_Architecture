---
sprint: 02
task: 01-create-models
---

# Prompt 02.01 — Criar Models (Lead, Memory, Timeline Event)

> **Copy-paste este prompt inteiro pra um agente de IA.**
> Ele sabe exatamente o que fazer.

---

## Skills a carregar ANTES

```
1. /Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/.skills/revenue-sdr-os-architect.md
2. /Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/.skills/sqlmodel-migration.md
3. /Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/.skills/fastapi-multi-tenant.md
```

---

## Contexto

Voce esta implementando a Sprint 02 do Revenue SDR OS — Lead Brain + Memory Brain.
O repo de codigo e' `~/AGENCIA/SDR/`. Ja existe:
- Organization, User (Sprint 01)
- Middleware de tenant resolution
- Auth (JWT + bcrypt)

Voce precisa criar **3 models novos** com FK para `organizations.id`:

---

## Tasks

### T1: Criar `app/models/lead.py` com 3 SQLModels

```python
"""
Lead + Memory + Timeline Event models.

Implementa o Lead Brain (unificacao cross-channel) e Memory Brain
(notas estruturadas + deteccao automatica).
"""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


# --- ID factories ---

def _new_lead_id() -> str:
    return f"lead_{uuid4().hex[:12]}"

def _new_memory_id() -> str:
    return f"mem_{uuid4().hex[:12]}"

def _new_event_id() -> str:
    return f"evt_{uuid4().hex[:12]}"


# --- Enums (use string constants para simplicidade) ---

LEAD_SOURCES = [
    "instagram", "facebook", "whatsapp", "site", "landing_page",
    "linkedin", "google", "indicacao", "telefone", "email", "import_csv", "outros"
]

LEAD_STATUSES = [
    "novo", "qualificado", "reuniao_agendada", "reuniao_feita",
    "proposta_enviada", "em_negociacao", "venda", "perdido",
    "inativo", "deletado"  # soft delete (LGPD)
]

MEMORY_CATEGORIES = [
    "personal",      # nome conjuge, idade, cidade
    "preference",    # estilo preferido, time futebol, hobbies
    "objection",     # objecoes recurrentes ("muito caro", "vou pensar")
    "financial",     # orcamento, renda, dia pagamento
    "context",       # contexto da compra, urgencia
    "family",        # info sobre familia
    "temporal",      # datas importantes (aniversario, viagem)
    "other"
]


# --- Lead ---

class Lead(SQLModel, table=True):
    __tablename__ = "leads"

    id: str = Field(default_factory=_new_lead_id, primary_key=True, index=True)

    # Tenant (CRITICO)
    organization_id: str = Field(foreign_key="organizations.id", index=True, nullable=False)

    # Identidade
    name: str = Field(min_length=1, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50, index=True)
    email: Optional[str] = Field(default=None, max_length=200, index=True)
    document: Optional[str] = Field(default=None, max_length=50)  # CPF/CNPJ

    # Origem
    source: str = Field(max_length=50)  # ver LEAD_SOURCES
    source_detail: str = Field(default="{}", max_length=10000)  # JSON

    # Segmentacao
    tags: str = Field(default="[]", max_length=10000)  # JSON array
    custom_fields: str = Field(default="{}", max_length=10000)  # JSON object

    # Status
    status: str = Field(default="novo", max_length=20, index=True)
    assigned_user_id: Optional[str] = Field(
        default=None, foreign_key="users.id", index=True
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    last_interaction_at: Optional[datetime] = Field(default=None)

    # Relationships
    memories: List["LeadMemory"] = Relationship(
        back_populates="lead",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    timeline: List["LeadTimelineEvent"] = Relationship(
        back_populates="lead",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# --- Lead Memory ---

class LeadMemory(SQLModel, table=True):
    __tablename__ = "lead_memories"

    id: str = Field(default_factory=_new_memory_id, primary_key=True, index=True)

    # Tenant
    organization_id: str = Field(foreign_key="organizations.id", index=True, nullable=False)
    lead_id: str = Field(foreign_key="leads.id", index=True, nullable=False)

    # Conteudo
    category: str = Field(max_length=50, index=True)  # ver MEMORY_CATEGORIES
    key: str = Field(max_length=100)
    value: str = Field(max_length=10000)

    # Metadata
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = Field(default="manual", max_length=50)  # manual|conversation_detected|import

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    lead: Lead = Relationship(back_populates="memories")


# --- Lead Timeline Event ---

class LeadTimelineEvent(SQLModel, table=True):
    __tablename__ = "lead_timeline_events"

    id: str = Field(default_factory=_new_event_id, primary_key=True, index=True)

    # Tenant
    organization_id: str = Field(foreign_key="organizations.id", index=True, nullable=False)
    lead_id: str = Field(foreign_key="leads.id", index=True, nullable=False)

    # Evento
    event_type: str = Field(max_length=50, index=True)
    payload: str = Field(default="{}", max_length=10000)  # JSON

    # Actor
    actor_user_id: Optional[str] = Field(default=None, foreign_key="users.id")

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    lead: Lead = Relationship(back_populates="timeline")
```

### T2: Atualizar `app/models/__init__.py`

```python
"""
SQLModel models do Revenue SDR OS.
"""
from app.models.organization import Organization
from app.models.user import User
from app.models.lead import Lead, LeadMemory, LeadTimelineEvent

__all__ = ["Organization", "User", "Lead", "LeadMemory", "LeadTimelineEvent"]
```

---

## Validacao

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate

# 1. Imports funcionam
python -c "from app.models import Lead, LeadMemory, LeadTimelineEvent; print('OK')"

# 2. Tabelas criam (vai ser usado pela migration depois)
python -c "
from app.database import create_db_and_tables
create_db_and_tables()
print('Tables created')
"

# 3. Lead pode ser instanciado
python -c "
from app.models import Lead
lead = Lead(organization_id='org_test', name='João', phone='+5511...', source='whatsapp')
print(f'Lead: {lead.id} - {lead.name}')
"
```

---

## Checklist

```
[ ] Arquivo app/models/lead.py criado com 3 classes
[ ] Lead tem organization_id (FK NOT NULL)
[ ] LeadMemory tem lead_id (FK NOT NULL, cascade delete)
[ ] LeadTimelineEvent tem lead_id (FK NOT NULL, cascade delete)
[ ] IDs sao prefixed (lead_, mem_, evt_)
[ ] Constantes LEAD_SOURCES, LEAD_STATUSES, MEMORY_CATEGORIES definidas
[ ] app/models/__init__.py exporta os novos models
[ ] Python imports funcionam
[ ] Tabelas criam no DB
```

---

*"Lead sem identidade e' lead perdido."*