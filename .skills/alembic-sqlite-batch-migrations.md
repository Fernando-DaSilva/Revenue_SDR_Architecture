---
name: alembic-sqlite-batch-migrations
description: |
  Carregue esta skill sempre que for criar ou modificar migrações de banco de dados
  no Alembic para garantir compatibilidade com SQLite/libSQL usando o modo batch (render_as_batch=True).
version: 1.0.0
author: Hermes (arquiteto)
license: Proprietary
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
metadata:
  hermes:
    tags: [alembic, sqlite, libsql, batch-mode, migrations, schema-evolution]
---

# Skill: Migrações de Banco de Dados via Alembic em Modo Batch (SQLite/libSQL)

## 1. Princípio Fundamental

O SQLite/libSQL possui limitações de DDL (`ALTER TABLE`) para alterar colunas, remover Foreign Keys ou modificar constraints em tabelas existentes.
Para evitar que migrações falhem em produção, **TODA** alteração de tabela no Alembic DEVE utilizar o modo batch (`op.batch_alter_table`).

---

## 2. Configuração de Batch no `alembic/env.py`

Garantir que `render_as_batch=True` esteja ativado no contexto do Alembic:

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=True,  # OBRIGATÓRIO PARA SQLITE / LIBSQL
    configure_constraints=True,
)
```

---

## 3. Padrão de Script de Migração Reversível (`alembic/versions/`)

```python
"""add_fields_to_leads

Revision ID: 3b9a8c7d6e5f
Revises: 1a2b3c4d5e6f
Create Date: 2026-08-10
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

def upgrade() -> None:
    # USAR SEMPRE batch_alter_table
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.add_column(sa.Column('company_name', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('score_dhs', sa.Integer(), nullable=False, server_default='0'))
        batch_op.create_index(batch_op.f('ix_leads_company_name'), ['company_name'], unique=False)

def downgrade() -> None:
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_leads_company_name'))
        batch_op.drop_column('score_dhs')
        batch_op.drop_column('company_name')
```

---

## 4. Teste Round-Trip Obrigatório Antes do Commit

Todo script de migração novo deve passar no ciclo completo de upgrade e downgrade localmente:

```bash
# 1. Aplicar a nova migração
alembic upgrade head

# 2. Testar o downgrade (reverter)
alembic downgrade -1

# 3. Re-aplicar a migração
alembic upgrade head
```

---

## 5. Anti-Patterns (NUNCA faça)

```
[X] op.add_column('leads', ...) fora de batch_alter_table -> Falhará em SQLite se alterar constraints
[X] Criar nova coluna NOT NULL sem server_default          -> Quebrará bancos com dados existentes
[X] Deletar ou modificar manualmente migrações antigas     -> Crie uma nova revisão com alembic revision
[X] Esquecer a função downgrade()                         -> Toda migração DEVE ser reversível
```

---

## 6. Checklist de Validação

- [ ] O script em `alembic/versions/` usa `with op.batch_alter_table(...)`
- [ ] Colunas `NOT NULL` novas possuem um `server_default` apropriado
- [ ] A função `downgrade()` reverte exatamente o que `upgrade()` faz
- [ ] O teste round-trip (`upgrade head -> downgrade -1 -> upgrade head`) passou 100%
