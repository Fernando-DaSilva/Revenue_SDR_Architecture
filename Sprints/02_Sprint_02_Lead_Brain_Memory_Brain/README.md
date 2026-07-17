# Sprint 02 — Lead Brain + Memory Brain

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 02 — LEAD BRAIN + MEMORY BRAIN                             |
|   Status:  A EXECUTAR (codigo)                                       |
|   Owner:   Agente externo (Claude Code / Codex / OpenCode)           |
|   Quando:  1-2 semanas                                               |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-02-lead-brain                              |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visao geral

Implementar as duas primeiras "cerebros" do Revenue SDR OS:

### Lead Brain
Unifica identidade de uma pessoa atraves de todos os canais. Lead = entidade unica independente de onde veio (WhatsApp, Instagram, site, indicacao, etc). Merge automatico baseado em telefone/email/nome similar.

### Memory Brain
Lembra absolutamente tudo sobre o lead: preferencias, objecoes, datas importantes, contexto financeiro, relacionamento. Notas estruturadas + deteccao automatica em mensagens.

---

## Schema (migrations Alembic)

### Tabela: leads

```sql
CREATE TABLE leads (
    id VARCHAR PRIMARY KEY,                  -- "lead_<12hex>"
    organization_id VARCHAR NOT NULL,        -- FK organizations.id
    name VARCHAR(200) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(200),
    document VARCHAR(50),                     -- CPF/CNPJ
    source VARCHAR(50) NOT NULL,              -- instagram|whatsapp|site|indicacao|telefone|email|outros
    source_detail TEXT,                       -- JSON com metadata do source
    tags JSON NOT NULL DEFAULT '[]',          -- ["VIP", "retorno", ...]
    custom_fields JSON NOT NULL DEFAULT '{}', -- extensivel por tenant
    status VARCHAR(20) NOT NULL DEFAULT 'novo', -- novo|qualificado|reuniao|proposta|venda|perdido|inativo
    assigned_user_id VARCHAR,                -- FK users.id (nullable)
    created_at DATETIME NOT NULL,
    updated_at DATETIME,
    last_interaction_at DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (assigned_user_id) REFERENCES users(id)
);

CREATE INDEX idx_leads_org ON leads(organization_id);
CREATE INDEX idx_leads_phone ON leads(organization_id, phone);
CREATE INDEX idx_leads_email ON leads(organization_id, email);
CREATE INDEX idx_leads_status ON leads(organization_id, status);
CREATE INDEX idx_leads_assigned ON leads(organization_id, assigned_user_id);
```

### Tabela: lead_memories

```sql
CREATE TABLE lead_memories (
    id VARCHAR PRIMARY KEY,                  -- "mem_<12hex>"
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,
    category VARCHAR(50) NOT NULL,            -- personal|preference|objection|financial|context|family|temporal
    key VARCHAR(100) NOT NULL,                -- "esposa", "orcamento_max", "data_salario"
    value TEXT NOT NULL,
    confidence FLOAT NOT NULL DEFAULT 1.0,    -- 0.0-1.0 (1.0 = user explicit; <1.0 = IA detected)
    source VARCHAR(50) NOT NULL,              -- manual|conversation_detected|import
    source_message_id VARCHAR,                -- FK messages.id (nullable)
    created_at DATETIME NOT NULL,
    updated_at DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX idx_memories_lead ON lead_memories(lead_id);
CREATE INDEX idx_memories_org_category ON lead_memories(organization_id, category);
```

### Tabela: lead_timeline_events (audit log)

```sql
CREATE TABLE lead_timeline_events (
    id VARCHAR PRIMARY KEY,                  -- "evt_<12hex>"
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,
    event_type VARCHAR(50) NOT NULL,          -- created|memory_added|merged|status_changed|assigned|tag_added
    payload JSON NOT NULL DEFAULT '{}',
    actor_user_id VARCHAR,                    -- quem fez (nullable = sistema)
    created_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX idx_timeline_lead ON lead_timeline_events(lead_id, created_at DESC);
```

---

## Estrutura de arquivos

```
app/
+-- models/
|   +-- lead.py                    # SQLModel: Lead, LeadMemory, LeadTimelineEvent
|   +-- __init__.py                # adicionar imports
|
+-- api/v1/
|   +-- leads.py                   # CRUD de leads
|   +-- memories.py                # CRUD de memories de um lead
|   +-- __init__.py                # registrar routers
|
+-- services/                      # NOVO — logica de negocio
|   +-- __init__.py
|   +-- lead_merge.py              # logica de merge automatico
|   +-- memory_extractor.py        # deteccao de info em mensagens (placeholder)
|
+-- templates/
|   +-- leads/
|   |   +-- index.html            # lista de leads com busca
|   |   +-- detail.html           # perfil do lead + memories + timeline
|   |   +-- new.html              # form de cadastro
|   +-- partials/
|       +-- lead_card.html
|       +-- memory_chip.html
|
alembic/versions/
+-- XXXX_add_leads.py              # gerado por autogenerate

tests/
+-- test_leads.py                  # CRUD basico
+-- test_lead_isolation.py         # tenant isolation (CRITICO)
+-- test_lead_merge.py             # logica de merge
+-- test_memories.py               # CRUD de memories
```

---

## Prompts a usar (nesta pasta)

| Tarefa | Prompt |
|---|---|
| Criar models (Lead, LeadMemory, LeadTimelineEvent) | `prompts/01-create-models.md` |
| Criar migration Alembic | `prompts/02-create-migration.md` |
| Criar service de merge automatico | `prompts/03-create-merge-service.md` |
| Criar API CRUD de leads | `prompts/04-create-leads-api.md` |
| Criar API CRUD de memories | `prompts/05-create-memories-api.md` |
| Criar UI HTMX (lista de leads) | `prompts/06-create-leads-ui.md` |
| Criar UI HTMX (detalhe do lead) | `prompts/07-create-lead-detail-ui.md` |
| Criar testes de tenant isolation | `prompts/08-create-isolation-tests.md` |
| Criar import CSV de leads | `prompts/09-create-csv-import.md` |

---

## Criterios de aceitacao (Definition of Done)

### Funcionais

```
[ ] Consigo criar lead via POST /api/v1/leads com campos obrigatorios
[ ] Lead criado aparece em GET /api/v1/leads
[ ] Consigo buscar lead por ID via GET /api/v1/leads/{id}
[ ] Consigo atualizar lead via PATCH /api/v1/leads/{id}
[ ] Consigo deletar lead via DELETE /api/v1/leads/{id}
[ ] Delete e soft-delete (status="deletado") — nao remove do banco (LGPD)
[ ] Consigo listar memories de um lead via GET /api/v1/leads/{id}/memories
[ ] Consigo adicionar memory via POST /api/v1/leads/{id}/memories
[ ] Timeline do lead mostra todos os eventos em ordem cronologica
[ ] Merge automatico: criar lead com telefone duplicado faz merge
[ ] Cross-tenant: lead de Org A NAO aparece em GET /api/v1/leads de Org B
[ ] Cross-tenant: tentativa de GET /api/v1/leads/{id_do_B} retorna 404
[ ] UI mostra lista de leads com cor do tenant
[ ] UI permite buscar lead por nome/email/telefone
[ ] UI de detalhe mostra memories + timeline
[ ] CSV import funciona (parse, validate, dry-run, commit)
```

### Tecnicos

```
[ ] pytest tests/test_lead_isolation.py passa (10+ casos)
[ ] pytest tests/test_leads.py passa (CRUD)
[ ] pytest tests/test_lead_merge.py passa (cenarios de merge)
[ ] alembic upgrade head + downgrade -1 + upgrade head funciona
[ ] /openapi.json mostra novos endpoints
[ ] Codigo segue padroes das skills (carregadas via skill principal)
[ ] Multi-tenant: toda query tem .where(Lead.organization_id == organization.id)
[ ] Soft delete: deletar lead nao remove do banco, marca status='deletado'
[ ] IDs prefixed (lead_, mem_, evt_)
[ ] Pydantic schemas separados do SQLModel
[ ] Nenhum secret hardcoded
[ ] Docstrings em funcoes publicas
```

---

## Estimativa

```
Tasks:
  T1: Models (Lead, Memory, Event)     — 4h
  T2: Migration Alembic               — 1h
  T3: Lead Merge Service              — 6h
  T4: Memory Extractor (placeholder)  — 2h
  T5: Leads API (CRUD)                 — 6h
  T6: Memories API                     — 3h
  T7: Lead Timeline API                — 2h
  T8: UI lista de leads                — 6h
  T9: UI detalhe do lead               — 6h
  T10: UI cadastro de lead             — 3h
  T11: Testes (isolation + CRUD + merge) — 8h
  T12: CSV Import                      — 4h

TOTAL: ~51h (1.5-2 semanas para 1 dev)
```

---

## Riscos

| Risco | Mitigacao |
|---|---|
| Merge automatico causar duplicatas | Threshold de confianca + review manual |
| Memory Extractor detectar coisas erradas | Confidence < 1.0 + editable pelo user |
| Performance com 10k+ leads | Indices em (org, phone), (org, email), (org, status) |
| Soft delete confundir queries | Filtrar status='deletado' em TODA listagem |
| Multi-tenant leak (lead de outra org aparecer) | Tenant isolation test + 404 cross-tenant |

---

## Como executar esta sprint (para o agente externo)

1. **Carregue as skills** (na ordem):
   - `.skills/revenue-sdr-os-architect.md`
   - `.skills/sqlmodel-migration.md`
   - `.skills/fastapi-multi-tenant.md`
   - `.skills/htmx-alpine-component.md`
   - `.skills/pytest-tenant-isolation.md`

2. **Leia os prompts** (na ordem numerica em `prompts/`)

3. **Use os templates**:
   - `templates/sqlmodel-tenant-model.py`
   - `templates/fastapi-route.py`
   - `templates/pytest-isolation-test.py`
   - `templates/htmx-component.html`

4. **Implemente em ordem** (T1 → T12)

5. **Valide** com `prompts/99-validacao-final.md`

6. **Commit + push**

---

*"Lead sem memoria e' lead perdido."*