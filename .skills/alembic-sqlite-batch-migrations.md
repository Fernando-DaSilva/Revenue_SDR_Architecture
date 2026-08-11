---
name: alembic-postgresql-migrations
description: |
  Carregue esta skill sempre que for criar ou modificar migrações de banco de dados
  no Alembic no Revenue SDR OS para garantir compatibilidade total com o Supabase Managed PostgreSQL.
version: 2.0.0
author: Antigravity (arquiteto)
license: Proprietary
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
metadata:
  hermes:
    tags: [alembic, postgresql, supabase, migrations, schema-evolution, DDL]
---

# Skill: Migrações de Banco de Dados via Alembic em PostgreSQL (Supabase Platform)

## 1. Princípio Fundamental

O Revenue SDR OS utiliza **Supabase Managed PostgreSQL 16+** como banco de dados unificado (ADR-036, ADR-037). O antigo modo batch do SQLite (`render_as_batch=True` / ADR-024) foi **SUPERSEDIDO**. 

Todas as migrações usam DDL transacional ACID nativo do PostgreSQL, executadas via Alembic e compatíveis com a Supabase CLI (`supabase migration` / `supabase db push`).

---

## 2. Configuração do Dialeto no `alembic/env.py`

O `env.py` configura o dialeto relacional PostgreSQL (`postgresql+asyncpg://` ou `psycopg3`):

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    compare_type=True,  # Detecta alteração de tipos de coluna
    compare_server_default=True,
)
```

---

## 3. Conexão com Supabase (Pooler Supavisor vs Direct)

- **Modo Sessão / Conexão Direta (Porta 5432)**: As migrações DDL do Alembic (`alembic upgrade head`) DEVEM ser executadas usando a conexão direta ou modo sessão (porta 5432) do Supabase Postgres, evitando limitações de DDL no modo transação do Supavisor.
- **SSL**: Exige `sslmode=require` na URL de conexão.

---

## 4. Padrão de Script de Migração PostgreSQL (`alembic/versions/`)

```python
"""add_pgvector_and_fields_to_leads

Revision ID: 3b9a8c7d6e5f
Revises: 1a2b3c4d5e6f
Create Date: 2026-08-11
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '3b9a8c7d6e5f'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Garante extensão pgvector no Supabase
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # 2. Adiciona colunas nativas no PostgreSQL
    op.add_column('leads', sa.Column('organization_id', sa.Uuid(), nullable=False))
    op.add_column('leads', sa.Column('embedding', Vector(1536), nullable=True))
    
    # 3. Adiciona FK e Índices HNSW
    op.create_foreign_key('fk_leads_org', 'leads', 'organizations', ['organization_id'], ['id'])
    op.create_index('idx_leads_embedding_hnsw', 'leads', ['embedding'], postgresql_using='hnsw', postgresql_ops={'embedding': 'vector_cosine_ops'})

def downgrade() -> None:
    op.drop_index('idx_leads_embedding_hnsw', table_name='leads')
    op.drop_constraint('fk_leads_org', 'leads', type_='foreignkey')
    op.drop_column('leads', 'embedding')
    op.drop_column('leads', 'organization_id')
```

---

## 5. Harness de Verificação Pré-Commit

```bash
# 1. Aplicar migração
alembic upgrade head

# 2. Testar reversão (downgrade)
alembic downgrade -1

# 3. Re-aplicar (upgrade)
alembic upgrade head
```
