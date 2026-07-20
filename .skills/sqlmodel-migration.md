---
name: sqlmodel-migration
description: |
  Padroes de SQLModel + Alembic para o Revenue SDR OS. Carregue esta skill
  sempre que for criar/alterar models, criar migrations, ou mexer no schema.
version: 2.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# SQLModel + Alembic — Padroes do Revenue SDR OS (v2.0)

## Principio basico

```
Todo model de dominio herda TenantMixin: organization_id (FK NOT NULL).
Todo ID e' prefixed via prefixed_id(): org_, user_, lead_, conv_, msg_, evt_, mem_...
Toda migration e' reversivel (upgrade + downgrade testados).
Timestamps UTC-aware (utc_now); updated_at com onupdate automatico.
JSON e' coluna nativa (sa.JSON), NAO string serializada.
```

---

## Estrutura de model

### Tenant model (multi-tenant) — app/<feature>/models.py

```python
"""Tabelas de <feature>."""
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.db.base import TenantMixin, prefixed_id

if TYPE_CHECKING:
    from app.users.models import User


class <Feature>(TenantMixin, table=True):
    __tablename__ = "<features>"  # SEMPRE plural snake_case

    # ID prefixed (organization_id + timestamps vem do TenantMixin)
    id: str = Field(
        default_factory=lambda: prefixed_id("<feat>"),
        primary_key=True,
    )

    # Campos de dominio
    name: str = Field(max_length=200)
    # ...

    # Relationships (opcional)
    # user: "User" = Relationship(back_populates="<features>")
```

**TenantMixin ja entrega**: `organization_id` (FK index NOT NULL) +
`created_at`/`updated_at` (UTC-aware, `onupdate` automatico).
**TimestampMixin** (sem tenant) para tabelas globais (ex: `Organization`).

### IMPORTANTE: table models NAO validam entrada

SQLModel `table=True` nao executa validacao pydantic — `regex=`,
`min_length=` em table model sao decorativos (ADR-012). Portanto:

- **Validacao de formato** (slug, cor, email, enums) -> nos **schemas**
  pydantic da API (`schemas.py`)
- **Integridade** (unique, FK, NOT NULL) -> constraints no **banco**
- No table model, `max_length` permanece: define o VARCHAR no DDL

### Enum-like fields

```python
# Coluna string + StrEnum para uso no codigo (melhor dos dois mundos):
from enum import StrEnum

class LeadStatus(StrEnum):
    NOVO = "novo"
    QUALIFICADO = "qualificado"
    # ...

class Lead(TenantMixin, table=True):
    status: str = Field(default=LeadStatus.NOVO, max_length=20, index=True)

# StrEnum compara com str: lead.status == LeadStatus.NOVO funciona.
# Validacao do valor permitido: no schema pydantic (Literal ou validator).
```

**Por que nao `sa.Enum`**: CHECK constraints dificultam adicionar valores
depois (exige migration de constraint). Coluna VARCHAR + validacao no
schema e' mais simples de evoluir.

---

## JSON fields (extensibilidade) — coluna NATIVA

```python
from sqlalchemy import JSON, Column
from sqlmodel import Field

class Lead(TenantMixin, table=True):
    tags: list = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    custom_fields: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))

# No codigo: uso direto, sem json.dumps/loads
lead.tags = ["VIP", "retorno"]
lead.custom_fields["orcamento_max"] = 5000
```

**Convencao**: default `list`/`dict` via `default_factory` (nunca `None`).
No SQLite o JSON vira TEXT gerenciado pelo SQLAlchemy; em Postgres vira
JSON/JSONB na migracao — transparente.

---

## Soft delete (LGPD)

```python
# Status inclui "deletado"
LEAD_STATUSES = [..., "deletado"]

# Toda query que lista filtra deletados:
def list_leads(db, organization_id):
    return db.exec(
        select(Lead).where(
            Lead.organization_id == organization_id,
            Lead.status != "deletado",
        )
    ).all()

# DELETE endpoint faz soft delete:
@router.delete("/{lead_id}")
async def delete_lead(lead_id: str, ...):
    lead = db.get(Lead, lead_id)
    if not lead or lead.organization_id != organization.id:
        raise HTTPException(404)
    if lead.status == "deletado":
        raise HTTPException(404)  # idempotente

    lead.status = "deletado"  # NAO db.delete(lead)
    db.add(lead)
    db.commit()
```

---

## Alembic setup (JA CONFIGURADO na v0.2.0 — nao recriar)

O repo tem `alembic.ini` + `alembic/env.py` funcionando:

- A URL vem de `DATABASE_URL` (ambiente) com fallback para o `.env` —
  **sem exigir SECRET_KEY** (migrations rodam em CI/deploy limpos)
- `target_metadata = SQLModel.metadata`; todo model novo precisa ser
  **importado no `alembic/env.py`** para o autogenerate enxerga-lo:

```python
# alembic/env.py (trecho)
import app.organizations.models
import app.users.models
import app.leads.models        # <- adicionar novos dominios aqui
```

### Criar migration

```bash
# Autogenerate baseado nos models (SEMPRE revisar o arquivo gerado)
alembic revision --autogenerate -m "add <feature> table"

# OU manual (indices, dados, ajustes finos):
alembic revision -m "add custom index on <table>"
```

### 4. Revisar migration gerada

Sempre abrir o arquivo em `alembic/versions/XXXX_<message>.py` e verificar:

```python
def upgrade() -> None:
    # Cria tabela
    op.create_table(
        "<features>",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        # ...
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
    )
    # Cria indices
    op.create_index("idx_<features>_org", "<features>", ["organization_id"])
    # Outros indices...


def downgrade() -> None:
    # Reversivel
    op.drop_index("idx_<features>_org", table_name="<features>")
    op.drop_table("<features>")
```

**Checklist**:
- [ ] `upgrade()` cria tabelas, colunas, FKs, indices
- [ ] `downgrade()` desfaz TUDO na ordem reversa
- [ ] FKs tem `ondelete="CASCADE"` quando apropriado (cascade delete)
- [ ] Indices em colunas frequentemente filtradas (organization_id, status, etc)

### 5. Testar migration

```bash
# Upgrade
alembic upgrade head

# Verificar tabelas
sqlite3 revenue_sdr_os.db ".tables"

# Verificar schema
sqlite3 revenue_sdr_os.db ".schema <features>"

# Downgrade
alembic downgrade -1

# Verificar que removeu
sqlite3 revenue_sdr_os.db ".tables"

# Upgrade novamente (round-trip OK)
alembic upgrade head
```

---

## Alembic patterns comuns

### Adicionar coluna NOT NULL com default

```python
def upgrade() -> None:
    # Adiciona coluna com default (nao quebra dados existentes)
    op.add_column(
        "users",
        sa.Column(
            "phone_verified",
            sa.Boolean(),
            nullable=False,
            server_default="0",  # SQLite
        ),
    )
    # Opcionalmente remove o default depois
    op.alter_column("users", "phone_verified", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "phone_verified")
```

### Adicionar indice composto

```python
def upgrade() -> None:
    op.create_index(
        "idx_leads_org_status",
        "leads",
        ["organization_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("idx_leads_org_status", table_name="leads")
```

### Renomear coluna (SQLite nao suporta direto)

```python
def upgrade() -> None:
    # 1. Cria nova coluna
    op.add_column("users", sa.Column("email_verified_at", sa.DateTime(), nullable=True))
    # 2. Copia dados (se houver)
    op.execute("UPDATE users SET email_verified_at = NULL")
    # 3. Drop coluna antiga (SQLite tem limitacoes)
    # Para SQLite, pode precisar de batch recreate

def downgrade() -> None:
    op.drop_column("users", "email_verified_at")
```

---

## Indices — quando criar

**SEMPRE criar indice em:**
- `organization_id` (em toda tabela de dominio)
- Foreign keys que serao usadas em JOINs
- Colunas usadas em `WHERE` frequente (status, created_at, email)
- Colunas com UNIQUE constraint (slug, email+org)

**Exemplo**:
```python
class Lead(SQLModel, table=True):
    __tablename__ = "leads"

    organization_id: str = Field(foreign_key="organizations.id", index=True)
    phone: Optional[str] = Field(default=None, index=True)  # busca por telefone
    email: Optional[str] = Field(default=None, index=True)  # busca por email
    status: str = Field(default="novo", index=True)  # filtro por status
```

**Indices compostos** (mais especificos):
```python
# Em migration:
op.create_index(
    "idx_leads_org_phone",
    "leads",
    ["organization_id", "phone"],  # busca por telefone DENTRO do tenant
)
```

---

## Conventions do projeto

### IDs

```python
# Sempre prefixed com 12 chars hex
def _new_lead_id() -> str:
    return f"lead_{uuid4().hex[:12]}"
```

### Timestamps

Entregues pelos mixins — **nao redeclarar no model**:

```python
# app/db/base.py (ja implementado):
#   created_at: default_factory=utc_now  (datetime.now(UTC), timezone-aware)
#   updated_at: default_factory=utc_now + sa_column_kwargs={"onupdate": utc_now}
```

`datetime.utcnow()` esta DEPRECADO no Python 3.12 — sempre `utc_now` de
`app.db.base`.

### Boolean

```python
is_active: bool = Field(default=True)
```

### Nullable

```python
# Default e' nullable=True (a menos que voce force nullable=False)
phone: Optional[str] = Field(default=None)  # OK
phone: str = Field(...)  # NOT NULL
```

### Tamanho de strings

```python
# Definir max_length SEMPRE
name: str = Field(max_length=200)
description: Optional[str] = Field(default=None, max_length=2000)
```

---

## Anti-patterns (NUNCA faca)

```python
# ERRADO: ID sem prefixo
id: str = Field(default_factory=lambda: uuid4().hex)  # NUNCA!

# CERTO
id: str = Field(default_factory=lambda: f"user_{uuid4().hex[:12]}")


# ERRADO: sem FK para organization
class Lead(SQLModel, table=True):
    name: str  # esqueceu organization_id! NUNCA!


# ERRADO: cascade no lugar errado (sa_relationship_kwargs e' de Relationship, NAO de Field)
class LeadMemory(TenantMixin, table=True):
    lead_id: str = Field(
        foreign_key="leads.id",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},  # NUNCA!
    )

# CERTO: cascade vai no Relationship; FK no Field
class Lead(TenantMixin, table=True):
    memories: list["LeadMemory"] = Relationship(
        back_populates="lead",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

class LeadMemory(TenantMixin, table=True):
    lead_id: str = Field(foreign_key="leads.id", index=True, nullable=False)
    lead: Lead = Relationship(back_populates="memories")


# ERRADO: usar sa.Enum (CHECK constraint dificulta adicionar valores)
role: str = Field(sa_column=Column(sa.Enum(Role)))

# CERTO: coluna VARCHAR + StrEnum no codigo + validacao no schema
role: str = Field(default=Role.MEMBER, max_length=20)


# ERRADO: migration nao reversivel
def upgrade():
    op.execute("DELETE FROM users")  # destrutivo, sem volta!


# ERRADO: esquecer de testar round-trip
alembic upgrade head
# pronto!  # NAO — sempre teste downgrade tambem
```

---

## Checklist de review de model/migration

```
[ ] Model no pacote do dominio (app/<feature>/models.py), __tablename__ plural snake_case
[ ] Herda TenantMixin (dominio) ou TimestampMixin (global)
[ ] ID via prefixed_id("<prefix>") (default_factory)
[ ] Validacao de formato nos SCHEMAS (table model nao valida!)
[ ] FKs com cascade no Relationship quando apropriado
[ ] Campos tem max_length (DDL) — sem regex/min_length decorativos
[ ] JSON como coluna nativa (sa.JSON), default_factory=list/dict
[ ] StrEnum no codigo + coluna VARCHAR (nunca sa.Enum)
[ ] Soft delete: status='deletado' ao inves de db.delete()
[ ] Model importado no alembic/env.py (autogenerate enxergar)
[ ] Migration: upgrade() cria tudo; downgrade() desfaz TUDO na ordem reversa
[ ] alembic upgrade + downgrade + upgrade testado
[ ] Indices em colunas filtradas frequentemente (org, status, phone, email)
```

---

*"Schema bem modelado e' metade do produto pronto."*