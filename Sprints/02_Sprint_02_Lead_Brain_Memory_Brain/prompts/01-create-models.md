---
sprint: 02
task: 01-create-models
---

# Prompt 02.01 — Criar Models (Lead, Memory, Timeline Event)

> Spec da task T1 da Sprint 02. Convencoes v0.2.0 (ver ARCHITECTURE.md).

---

## Skills a carregar ANTES

```
1. .skills/revenue-sdr-os-architect.md
2. .skills/sqlmodel-migration.md
3. .skills/fastapi-multi-tenant.md
```

---

## Contexto

Repo: `~/AGENCIA/SDR/` (baseline v0.2.0). Ja existem:

- `Organization`, `User` (pacotes `app/organizations/`, `app/users/`)
- Mixins em `app/db/base.py`: `TenantMixin` (organization_id + timestamps
  UTC-aware), `TimestampMixin`, `utc_now`, `prefixed_id`
- Tenancy por middleware + ContextVar; auth Argon2id/PyJWT

Criar **3 models novos** no pacote `app/leads/`.

Lembretes duros:
- Table models NAO validam entrada (ADR-012) — formatos vao nos schemas (T4)
- `datetime.utcnow()` DEPRECADO — timestamps vem do TenantMixin
- JSON e' coluna nativa (`sa.JSON`) com `default_factory`

---

## Task

### Criar `app/leads/models.py`

```python
"""
Lead Brain + Memory Brain — models de dominio.

Lead: entidade unica da pessoa, unificada entre canais.
LeadMemory: atributos estruturados de longo prazo.
LeadTimelineEvent: log append-only de tudo que acontece com o lead.
"""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship

from app.db.base import TenantMixin, prefixed_id

if TYPE_CHECKING:
    from app.users.models import User


# --- Enums (coluna VARCHAR + StrEnum no codigo; validacao nos schemas) ---

class LeadSource(StrEnum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    WHATSAPP = "whatsapp"
    SITE = "site"
    LANDING_PAGE = "landing_page"
    LINKEDIN = "linkedin"
    GOOGLE = "google"
    INDICACAO = "indicacao"
    TELEFONE = "telefone"
    EMAIL = "email"
    IMPORT_CSV = "import_csv"
    OUTROS = "outros"


class LeadStatus(StrEnum):
    NOVO = "novo"
    QUALIFICADO = "qualificado"
    REUNIAO_AGENDADA = "reuniao_agendada"
    REUNIAO_FEITA = "reuniao_feita"
    PROPOSTA_ENVIADA = "proposta_enviada"
    EM_NEGOCIACAO = "em_negociacao"
    VENDA = "venda"
    PERDIDO = "perdido"
    INATIVO = "inativo"
    DELETADO = "deletado"  # soft delete (LGPD)


class MemoryCategory(StrEnum):
    PERSONAL = "personal"        # nome conjuge, idade, cidade
    PREFERENCE = "preference"    # estilo, hobbies
    OBJECTION = "objection"      # "muito caro", "vou pensar"
    FINANCIAL = "financial"      # orcamento, renda, dia pagamento
    CONTEXT = "context"          # contexto da compra, urgencia
    FAMILY = "family"
    TEMPORAL = "temporal"        # datas importantes
    OTHER = "other"


class MemorySource(StrEnum):
    MANUAL = "manual"
    CONVERSATION_DETECTED = "conversation_detected"
    IMPORT = "import"


class LeadEventType(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    MERGED = "merged"
    STATUS_CHANGED = "status_changed"
    ASSIGNED = "assigned"
    TAG_ADDED = "tag_added"
    MEMORY_ADDED = "memory_added"


# --- Lead ---

class Lead(TenantMixin, table=True):
    __tablename__ = "leads"

    id: str = Field(default_factory=lambda: prefixed_id("lead"), primary_key=True)

    # Identidade
    name: str = Field(max_length=200)
    phone: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=320)
    document: str | None = Field(default=None, max_length=50)  # CPF/CNPJ

    # Origem
    source: str = Field(max_length=50)  # LeadSource
    source_detail: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))

    # Segmentacao
    tags: list = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    custom_fields: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))

    # Status / dono
    status: str = Field(default=LeadStatus.NOVO, max_length=20, index=True)
    assigned_user_id: str | None = Field(default=None, foreign_key="users.id")

    # Atividade
    last_interaction_at: datetime | None = Field(default=None)

    # Relationships
    memories: list["LeadMemory"] = Relationship(
        back_populates="lead",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    timeline: list["LeadTimelineEvent"] = Relationship(
        back_populates="lead",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# --- Lead Memory ---

class LeadMemory(TenantMixin, table=True):
    __tablename__ = "lead_memories"

    id: str = Field(default_factory=lambda: prefixed_id("mem"), primary_key=True)
    lead_id: str = Field(foreign_key="leads.id", index=True, nullable=False)

    # Conteudo
    category: str = Field(max_length=50)  # MemoryCategory
    key: str = Field(max_length=100)
    value: str = Field(max_length=10000)

    # Metadata
    confidence: float = Field(default=1.0)  # 0.0-1.0 (validado no schema)
    source: str = Field(default=MemorySource.MANUAL, max_length=50)

    # Relationships
    lead: Lead = Relationship(back_populates="memories")


# --- Lead Timeline Event (append-only) ---

class LeadTimelineEvent(TenantMixin, table=True):
    __tablename__ = "lead_timeline_events"

    id: str = Field(default_factory=lambda: prefixed_id("evt"), primary_key=True)
    lead_id: str = Field(foreign_key="leads.id", index=True, nullable=False)

    event_type: str = Field(max_length=50, index=True)  # LeadEventType
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    actor_user_id: str | None = Field(default=None, foreign_key="users.id")

    # Relationships
    lead: Lead = Relationship(back_populates="timeline")
```

Notas de implementacao:
- `TenantMixin` ja traz `organization_id`, `created_at`, `updated_at`
  (UTC-aware + onupdate) — NAO redeclarar
- Indices compostos `(organization_id, phone/email/status)` entram na
  migration (autogenerate detecta os simples; composto revisar a mao)
- `LeadTimelineEvent` e' append-only: sem update/delete em codigo de
  dominio (so inserts)

---

## Validacao

```bash
cd ~/AGENCIA/SDR && source .venv/bin/activate

# 1. Imports funcionam
python -c "from app.leads.models import Lead, LeadMemory, LeadTimelineEvent; print('OK')"

# 2. Instancia sem banco
python -c "
from app.leads.models import Lead, LeadSource
lead = Lead(organization_id='org_x', name='Joao', source=LeadSource.WHATSAPP)
assert lead.id.startswith('lead_') and lead.status == 'novo'
print('OK', lead.id)
"

# 3. Registrar no alembic/env.py (autogenerate da task T2 depende):
#    import app.leads.models
```

## Checklist

```
[ ] app/leads/models.py com 3 classes + StrEnums
[ ] Herda TenantMixin (sem redeclarar org/timestamps)
[ ] IDs prefixed_id('lead'/'mem'/'evt')
[ ] JSON nativo (source_detail, tags, custom_fields, payload)
[ ] cascade 'all, delete-orphan' nos Relationships do Lead
[ ] FKs: memories.lead_id, events.lead_id, assigned_user_id, actor_user_id
[ ] status indexado; default 'novo'; soft delete = 'deletado'
[ ] import app.leads.models adicionado ao alembic/env.py
[ ] ruff check limpo
```

---

*"Lead sem identidade e' lead perdido."*
