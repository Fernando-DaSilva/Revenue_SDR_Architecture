---
name: sqlmodel-migration
description: |
  Padroes de SQLModel + Alembic para o Revenue SDR OS. Carregue esta skill
  sempre que for criar/alterar models, criar migrations, ou mexer no schema.
version: 1.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# SQLModel + Alembic — Padroes do Revenue SDR OS

## Principio basico

```
Todo model de dominio TEM organization_id (FK NOT NULL).
Todo ID e' prefixed: org_, user_, lead_, conv_, msg_, evt_, mem_, ...
Toda migration e' reversivel (upgrade + downgrade testados).
```

---

## Estrutura de model

### Tenant model (multi-tenant)

```python
# app/models/<feature>.py
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


def _new_<feature>_id() -> str:
    """Factory: sempre prefixar (lead_, conv_, etc)."""
    return f"<feature>_{uuid4().hex[:12]}"


class <Feature>(SQLModel, table=True):
    __tablename__ = "<features>"  # SEMPRE plural snake_case

    # ID prefixed
    id: str = Field(default_factory=_new_<feature>_id, primary_key=True, index=True)

    # Tenant FK (CRITICO)
    organization_id: str = Field(
        foreign_key="organizations.id",
        index=True,
        nullable=False,
    )

    # Campos de dominio
    name: str = Field(min_length=1, max_length=200)
    # ... outros campos

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships (opcional)
    # user: Optional["User"] = Relationship(...)
```

### Enum-like fields (string constants)

```python
# Quando tem valores finitos, use constants
LEAD_SOURCES = [
    "instagram", "facebook", "whatsapp", "site",
    "indicacao", "telefone", "email", "outros"
]

LEAD_STATUSES = [
    "novo", "qualificado", "reuniao_agendada",
    "proposta_enviada", "venda", "perdido",
    "inativo", "deletado"  # soft delete
]

class Lead(SQLModel, table=True):
    source: str = Field(max_length=50)  # validar contra LEAD_SOURCES
    status: str = Field(default="novo", max_length=20)
```

**Por que string em vez de Enum**: simplicidade, flexibilidade pra migrations, sem dependência Python.

---

## JSON fields (extensibilidade)

```python
from sqlmodel import Field

class Lead(SQLModel, table=True):
    # JSON serializado como string (SQLite nao tem JSON nativo, mas funciona)
    tags: str = Field(default="[]", max_length=10000)
    custom_fields: str = Field(default="{}", max_length=10000)

# No codigo:
import json

lead.tags = json.dumps(["VIP", "retorno"])
db.add(lead)
db.commit()

# Ao ler:
tags_list = json.loads(lead.tags)  # ["VIP", "retorno"]
```

**Convencao**: sempre `"[]"` ou `"{}"` como default (JSON valido, nao `None`).

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

## Alembic setup

### 1. Inicializar (uma vez)

```bash
cd ~/AGENCIA/SDR
alembic init alembic
```

### 2. Configurar `alembic/env.py`

```python
# alembic/env.py
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Adiciona raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import SQLModel
from app.config import get_settings

# Importa TODOS os models (para autogenerate detectar)
from app.models import (
    Organization,
    User,
    Lead,           # Sprint 2
    LeadMemory,
    LeadTimelineEvent,
    # ... adicionar TODOS aqui
)

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 3. Criar migration

```bash
# Autogenerate baseado nos models
alembic revision --autogenerate -m "add <feature> table"

# OU manual:
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

```python
created_at: datetime = Field(default_factory=datetime.utcnow)
updated_at: Optional[datetime] = Field(default=None)  # NAO auto-update
```

Para auto-update, faca manualmente:
```python
lead.updated_at = datetime.utcnow()
db.add(lead)
db.commit()
```

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


# ERRADO: cascade nao definido
class LeadMemory(SQLModel, table=True):
    lead_id: str = Field(foreign_key="leads.id")  # sem cascade!

# CERTO
class LeadMemory(SQLModel, table=True):
    lead_id: str = Field(
        foreign_key="leads.id",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# ERRADO: usar Enum do Python
from enum import Enum

class LeadStatus(str, Enum):
    NOVO = "novo"
    QUALIFICADO = "qualificado"

# Isso complica migrations. Use string constants:
LEAD_STATUSES = ["novo", "qualificado", ...]


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
[ ] Model tem __tablename__ em plural snake_case
[ ] Model tem id prefixed (factory _new_X_id)
[ ] Model tem organization_id (FK NOT NULL) se for de dominio
[ ] FKs tem cascade quando apropriado
[ ] Campos tem max_length definido
[ ] Timestamps: created_at (default factory) + updated_at (optional)
[ ] Enums como string constants (NAO Enum class)
[ ] JSON fields: default "[]" ou "{}", serializados no codigo
[ ] Soft delete: status='deletado' ao inves de db.delete()
[ ] Migration: upgrade() cria tudo
[ ] Migration: downgrade() desfaz TUDO na ordem reversa
[ ] alembic upgrade + downgrade + upgrade testado
[ ] Indices em colunas filtradas frequentemente
[ ] app/models/__init__.py exporta o novo model
```

---

*"Schema bem modelado e' metade do produto pronto."*