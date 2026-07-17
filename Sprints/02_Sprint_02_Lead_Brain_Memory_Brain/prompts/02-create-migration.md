---
sprint: 02
task: 02-create-migration
---

# Prompt 02.02 — Criar Migration Alembic

> **Copy-paste este prompt inteiro pra um agente de IA.**

---

## Skills a carregar

```
1. .skills/revenue-sdr-os-architect.md
2. .skills/sqlmodel-migration.md
```

---

## Contexto

Voce ja criou os models Lead, LeadMemory, LeadTimelineEvent (Sprint 02, T1).
Agora precisa criar a migration Alembic que cria essas tabelas no banco.

Repo: `~/AGENCIA/SDR/`

---

## Tasks

### T1: Garantir que Alembic esta configurado

```bash
cd ~/AGENCIA/SDR
ls alembic.ini alembic/env.py alembic/versions/
```

Se nao existir, configure Alembic:
```bash
alembic init alembic
```

### T2: Configurar `alembic/env.py` para ler do mesmo DATABASE_URL do app

Edite `alembic/env.py`:

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from pathlib import Path

# Adiciona raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import SQLModel
from app.config import get_settings  # importa settings do app

# Importa todos os models para que o autogenerate detecte
from app.models import *  # noqa

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

### T3: Gerar migration automaticamente

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate
alembic revision --autogenerate -m "add leads memories and timeline events"
```

Vai criar arquivo em `alembic/versions/XXXX_add_leads_memories_and_timeline_events.py`.

### T4: Revisar a migration gerada

Abra o arquivo gerado e verifique:
- Cria tabela `leads` com todas as colunas
- Cria tabela `lead_memories` com FK para leads
- Cria tabela `lead_timeline_events` com FK para leads
- Indices estao criados (idx_leads_org, idx_leads_phone, etc)
- FK tem `ondelete="CASCADE"` (ou similar)

Se algo estiver faltando, adicione manualmente.

### T5: Testar upgrade + downgrade

```bash
# Upgrade (cria tabelas)
alembic upgrade head

# Verificar que criou
sqlite3 revenue_sdr_os.db ".tables"
# Deve mostrar: organizations, users, leads, lead_memories, lead_timeline_events, alembic_version

# Downgrade (remove tabelas)
alembic downgrade -1

# Verificar que removeu
sqlite3 revenue_sdr_os.db ".tables"
# Nao deve ter leads, lead_memories, lead_timeline_events

# Upgrade novamente
alembic upgrade head
```

---

## Validacao

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate

# 1. Migration aplica limpa
rm revenue_sdr_os.db 2>/dev/null
alembic upgrade head
sqlite3 revenue_sdr_os.db ".tables" | tr ' ' '\n' | sort

# Esperado:
# alembic_version
# lead_memories
# lead_timeline_events
# leads
# organizations
# users

# 2. Schema da tabela leads
sqlite3 revenue_sdr_os.db ".schema leads"

# 3. Re-rodar seed (cria tenants)
python scripts/seed.py

# 4. Verificar que tenants ainda funcionam
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"email":"admin@clinica-bela.com","password":"senha123"}'
```

---

## Checklist

```
[ ] alembic/env.py importa models do app
[ ] alembic/env.py usa DATABASE_URL do settings
[ ] alembic revision --autogenerate funciona
[ ] Migration gerada cria 3 tabelas
[ ] FKs e indices corretos
[ ] alembic upgrade head funciona
[ ] alembic downgrade -1 funciona
[ ] alembic upgrade head novamente funciona (round-trip)
[ ] Tabelas estao no banco apos upgrade
[ ] Seed.py ainda funciona (cria tenants em paralelo)
```

---

*"Migration reversivel e' migration confiavel."*