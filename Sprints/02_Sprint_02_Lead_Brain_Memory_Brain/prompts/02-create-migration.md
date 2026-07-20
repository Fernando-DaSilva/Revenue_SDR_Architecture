---
sprint: 02
task: 02-create-migration
---

# Prompt 02.02 — Criar Migration Alembic

> Spec da task T2 da Sprint 02. Alembic JA esta configurado (v0.2.0) —
> NAO recriar `alembic.ini`/`env.py`, apenas registrar o novo pacote.

---

## Contexto

Models `Lead`, `LeadMemory`, `LeadTimelineEvent` criados (T1) em
`app/leads/models.py`. Agora gerar a migration que cria as 3 tabelas.

---

## Tasks

### T1: Registrar o pacote no `alembic/env.py`

O autogenerate so enxerga models importados. Adicionar:

```python
# alembic/env.py (trecho de imports de models)
import app.organizations.models
import app.users.models
import app.leads.models        # <- NOVO
```

### T2: Gerar migration

```bash
cd ~/AGENCIA/SDR && source .venv/bin/activate
alembic revision --autogenerate -m "add leads domain (lead brain + memory brain)"
```

### T3: Revisar o arquivo gerado em `alembic/versions/`

Verificar e completar a mao se necessario:

```
[ ] 3 tabelas: leads, lead_memories, lead_timeline_events
[ ] Colunas JSON nativas (source_detail, tags, custom_fields, payload)
[ ] FKs: memories.lead_id -> leads.id; events.lead_id -> leads.id;
    leads.assigned_user_id -> users.id; events.actor_user_id -> users.id
[ ] Indices simples: leads.status, memories.lead_id, events.lead_id,
    events.event_type, + organization_id (via TenantMixin)
[ ] ADICIONAR indices compostos (autogenerate nao cria):
    op.create_index("ix_leads_org_phone", "leads", ["organization_id", "phone"])
    op.create_index("ix_leads_org_email", "leads", ["organization_id", "email"])
    op.create_index("ix_leads_org_status", "leads", ["organization_id", "status"])
    op.create_index("ix_lead_events_lead_created", "lead_timeline_events",
                    ["lead_id", "created_at"])
    (e drops correspondentes no downgrade)
[ ] updated_at NOT NULL em leads e lead_memories (mixin)
```

### T4: Round-trip

```bash
alembic upgrade head
sqlite3 revenue_sdr_os.db ".tables"          # organizations users leads lead_memories lead_timeline_events alembic_version
sqlite3 revenue_sdr_os.db ".schema leads"    # conferir colunas/indices
alembic downgrade -1                          # remove as 3 tabelas
alembic upgrade head                          # recria
python -m scripts.seed                        # seed continua funcionando
```

---

## Checklist

```
[ ] import app.leads.models no alembic/env.py
[ ] Migration autogerada + revisada (indices compostos a mao)
[ ] upgrade + downgrade + upgrade OK
[ ] .tables mostra as 3 tabelas novas
[ ] python -m scripts.seed OK apos migration
[ ] ruff check alembic/ limpo
```

---

*"Migration reversivel e' migration confiavel."*
