# ADR-024: Migrações de Banco de Dados via Alembic em SQLite/libSQL (Batch Mode)

* **Status**: Aprovado
* **Data**: Agosto 2026
* **Autores**: Equipe de Banco de Dados e Engenharia Backend (Revenue SDR OS)

---

## 1. Contexto e Problema

O **Revenue SDR OS** utiliza o **Turso (libSQL)** e arquivos `.db` SQLite locais como mecanismo primário de banco de dados para a VPS dedicada single-tenant (ADR-002 / ADR-016).

Diferente de bancos de dados relacionais como PostgreSQL ou MySQL, o **SQLite/libSQL possui limitações severas em operações DDL (`ALTER TABLE`)**:
- Não suporta remover colunas (`DROP COLUMN`) diretamente em versões mais antigas de driver sem recriar a tabela.
- Não suporta alterar constraints de Foreign Keys (`DROP CONSTRAINT` / `ADD CONSTRAINT`) em tabelas existentes.
- Não suporta alterar colunas para `NOT NULL` sem recriação do esquema.

Se os Agentes de IA ou desenvolvedores gerarem migrations do Alembic no formato padrão de PostgreSQL (ex: `op.alter_column(...)` ou `op.drop_constraint(...)`), as migrações falharão silenciosamente ou travarão o banco de dados em produção na VPS do cliente durante o comando `alembic upgrade head`.

---

## 2. Decisão Arquitetural

Habilitar obrigatoriamente o **Modo Batch (`render_as_batch=True`)** na configuração do Alembic (`alembic/env.py`) e estabelecer padrões estritos de autoramento de migrações compatíveis com SQLite/libSQL e PostgreSQL simultaneamente.

### Funcionamento do Batch Mode no Alembic:
1. Cria uma tabela temporária com o novo esquema desejado (`_alembic_tmp_tabela`).
2. Copia todos os dados da tabela antiga para a tabela temporária.
3. Remove a tabela antiga.
4. Renomeia a tabela temporária para o nome original.
5. Recria todos os índices e Foreign Keys.

---

## 3. Configuração Obrigatória no `alembic/env.py`

```python
# alembic/env.py

def run_migrations_online() -> None:
    connectable = context.config.attributes.get("connection", None)
    
    if connectable is None:
        connectable = engine_from_config(
            context.config.get_section(context.config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # MODO BATCH OBRIGATÓRIO PARA COMPATIBILIDADE COM SQLITE / LIBSQL
            render_as_batch=True,
            # Garantir integridade de Foreign Keys no SQLite
            configure_constraints=True,
        )

        with context.begin_transaction():
            context.run_migrations()
```

---

## 4. Estrutura de Script de Migration Reversível com Batch Op

Toda migração gerada DEVE utilizar o gerenciador de contexto `op.batch_alter_table`:

```python
"""add_category_to_memories

Revision ID: 5a8e9f01b2c3
Revises: 1a2b3c4d5e6f
Create Date: 2026-08-10
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

def upgrade() -> None:
    # MODO BATCH OBRIGATÓRIO
    with op.batch_alter_table('memories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confidence_score', sa.Float(), nullable=False, server_default='1.0'))
        batch_op.create_index(batch_op.f('ix_memories_confidence_score'), ['confidence_score'], unique=False)

def downgrade() -> None:
    with op.batch_alter_table('memories', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_memories_confidence_score'))
        batch_op.drop_column('confidence_score')
```

---

## 5. Validação Round-Trip Obrigatória no CI/CD e Checklist do Agente

Antes de commitar qualquer migration, a suite de testes executa o ciclo de **Validação Round-Trip**:

```bash
# 1. Aplica todas as migrations até a cabeça
alembic upgrade head

# 2. Executa downgrade da última migration criada
alembic downgrade -1

# 3. Re-aplica a migration para garantir consistência
alembic upgrade head
```

---

## 6. Invariantes para Agentes de Codificação (AI Coding Guardrails)

1. **NUNCA** editar ou excluir arquivos de migração antigos já mesclados no repositório. Toda alteração exige a criação de uma nova revisão via `alembic revision --autogenerate`.
2. **SEMPRE** verificar se o arquivo em `alembic/versions/` está utilizando o bloco `with op.batch_alter_table(...)`. Se a autogeração omitir o batch_op, o agente DEVE refatorar o arquivo para usá-lo.
3. **SEMPRE** incluir um `server_default` ou definir `nullable=True` ao adicionar novas colunas em tabelas que já possuem dados para evitar falhas de restrição de não-nulo durante a migração.
