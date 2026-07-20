# Sprint 02 — Lead Brain + Memory Brain

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 02 — LEAD BRAIN + MEMORY BRAIN                             |
|   Status:  PRONTA PARA EXECUCAO (spec alinhada a v0.2.0)            |
|   Owner:   Agente de codificacao                                     |
|   Quando:  1-2 semanas                                               |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-02-lead-brain                              |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visao geral

Implementar os dois primeiros "cerebros" do Revenue SDR OS:

### Lead Brain
Unifica identidade de uma pessoa atraves de todos os canais. Lead = entidade unica independente de onde veio (WhatsApp, Instagram, site, indicacao, etc). Deteccao de duplicatas por telefone/email + merge conservador.

### Memory Brain
Lembra absolutamente tudo sobre o lead: preferencias, objecoes, datas importantes, contexto financeiro, relacionamento. Notas estruturadas + deteccao automatica em mensagens (placeholder nesta sprint).

---

## Schema (migration Alembic via autogenerate)

Convencoes v0.2.0 aplicadas: models herdam `TenantMixin` (organization_id +
timestamps UTC-aware com onupdate), IDs via `prefixed_id()`, JSON nativo
(`sa.JSON`), StrEnum no codigo + coluna VARCHAR.

### Tabela: leads

```sql
CREATE TABLE leads (
    id VARCHAR PRIMARY KEY,                    -- "lead_<12hex>"
    organization_id VARCHAR NOT NULL,          -- FK organizations.id
    name VARCHAR(200) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(320),
    document VARCHAR(50),                      -- CPF/CNPJ
    source VARCHAR(50) NOT NULL,               -- ver LeadSource
    source_detail JSON NOT NULL,               -- metadata da origem
    tags JSON NOT NULL,                        -- ["VIP", "retorno", ...]
    custom_fields JSON NOT NULL,               -- extensivel por tenant
    status VARCHAR(20) NOT NULL DEFAULT 'novo',-- ver LeadStatus
    assigned_user_id VARCHAR,                  -- FK users.id (nullable)
    last_interaction_at DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,              -- onupdate automatico
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (assigned_user_id) REFERENCES users(id)
);

-- Indices: (organization_id), (organization_id, phone),
--          (organization_id, email), (organization_id, status)
```

### Tabela: lead_memories

```sql
CREATE TABLE lead_memories (
    id VARCHAR PRIMARY KEY,                    -- "mem_<12hex>"
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,                  -- FK leads.id (cascade via ORM)
    category VARCHAR(50) NOT NULL,             -- ver MemoryCategory
    key VARCHAR(100) NOT NULL,                 -- "esposa", "orcamento_max", "data_salario"
    value TEXT NOT NULL,
    confidence FLOAT NOT NULL DEFAULT 1.0,     -- 1.0 = explicito; <1.0 = IA detectou
    source VARCHAR(50) NOT NULL DEFAULT 'manual', -- manual|conversation_detected|import
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Indices: (lead_id), (organization_id, category)
```

### Tabela: lead_timeline_events (append-only)

```sql
CREATE TABLE lead_timeline_events (
    id VARCHAR PRIMARY KEY,                    -- "evt_<12hex>"
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,                  -- FK leads.id (cascade via ORM)
    event_type VARCHAR(50) NOT NULL,           -- created|memory_added|merged|status_changed|assigned
    payload JSON NOT NULL,
    actor_user_id VARCHAR,                     -- quem fez (NULL = sistema)
    created_at DATETIME NOT NULL,              -- imutavel (append-only)
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Indices: (lead_id, created_at)
```

---

## Estrutura de arquivos (padrao v0.2.0 — pacotes de dominio)

```
app/
+-- leads/
|   +-- __init__.py
|   +-- models.py               # Lead, LeadMemory, LeadTimelineEvent + StrEnums
|   +-- schemas.py              # LeadCreate/Update/Response, MemoryCreate/... (VALIDACAO)
|   +-- service.py              # LeadService (CRUD + timeline), MemoryService
|   +-- merge.py                # deteccao de duplicatas + merge conservador
|   +-- api.py                  # /api/v1/leads (JSON)
|
+-- web/
|   +-- pages/leads.py          # paginas HTML (lista, detalhe, novo)
|   +-- templates/leads/
|       +-- index.html          # lista com busca (HTMX)
|       +-- detail.html         # perfil + memories + timeline
|       +-- new.html            # form de cadastro
|   +-- templates/partials/
|       +-- lead_card.html
|       +-- memory_chip.html

alembic/versions/
+-- XXXX_add_leads_domain.py    # autogenerate (revisar antes de aplicar)

tests/
+-- test_leads_api.py           # CRUD + paginacao
+-- test_leads_isolation.py     # cross-tenant (CRITICO)
+-- test_leads_merge.py         # cenarios de duplicata/merge
+-- test_lead_memories.py       # CRUD de memories + timeline
```

---

## Prompts (specs por tarefa, nesta pasta)

| # | Prompt | Tarefa |
|---|---|---|
| 01 | `prompts/01-create-models.md` | T1: models Lead/Memory/TimelineEvent |
| 02 | `prompts/02-create-migration.md` | T2: migration Alembic |
| 03 | `prompts/03-create-merge-service.md` | T3: merge de duplicatas |
| 04 | `prompts/04-create-leads-api.md` | T4-T7: API de leads + timeline |
| 05 | `prompts/05-create-memories-api.md` | T8: API de memories |
| 06 | `prompts/06-create-isolation-tests.md` | T11: testes de isolamento |
| 99 | `prompts/99-final-validation.md` | Validacao final + commit |

UI (T8-T10) segue a skill `htmx-alpine-component`. CSV import (T13)
confirmado no escopo (D2) — segue os mesmos padroes de service/merge.

---

## Criterios de aceitacao (Definition of Done)

### Funcionais

```
[ ] Criar lead via POST /api/v1/leads (campos validados pelo schema)
[ ] Lead criado aparece em GET /api/v1/leads (paginado)
[ ] Buscar por ID via GET /api/v1/leads/{id}
[ ] Atualizar via PATCH /api/v1/leads/{id}
[ ] DELETE e soft-delete (status="deletado") — nao remove do banco (LGPD)
[ ] Listar memories via GET /api/v1/leads/{id}/memories
[ ] Adicionar memory via POST /api/v1/leads/{id}/memories
[ ] Timeline do lead em ordem cronologica (GET /api/v1/leads/{id}/timeline)
[ ] Criar lead com telefone/email duplicado NAO duplica (ver "Decisao D1")
[ ] Cross-tenant: lead de Org A NAO aparece em listagem de Org B
[ ] Cross-tenant: GET /api/v1/leads/{id_de_B} com credencial de A = 404
[ ] organization_id do payload e' IGNORADO (sempre do contexto)
[ ] UI lista leads com busca (nome/email/telefone), tema do tenant
[ ] UI detalhe mostra memories + timeline
```

### Tecnicos

```
[ ] pytest 100% verde (suite toda + novos)
[ ] Testes de isolamento cross-tenant cobrem todos os endpoints novos
[ ] ruff check + ruff format --check limpos
[ ] alembic upgrade + downgrade + upgrade OK
[ ] /openapi.json mostra os endpoints novos
[ ] Models herdam TenantMixin; IDs prefixed (lead_, mem_, evt_)
[ ] JSON nativo (tags, custom_fields, payload); StrEnum no codigo
[ ] Envelope de erro padrao; validacao nos schemas
[ ] Timestamps UTC-aware; updated_at automatico
```

---

## Decisoes tomadas (2026-07-20, com Fernando)

```
D1. Duplicata na criacao: MERGE CONSERVADOR AUTOMATICO.
    Match por telefone/email normalizado (mesmo tenant, ignorando
    'deletado') -> preenche SOMENTE campos vazios do lead existente
    (nunca sobrescreve), uniao de tags/custom_fields, evento 'merged'
    auditavel na timeline, resposta da API com merged=true.

D2. CSV import: FICA na Sprint 02 (T13, ~4h).
    Upload -> parse -> validacao -> dry-run -> commit. Reusa o
    LeadService.create (dedup/merge valem para o CSV tambem).

D3. Status do lead: CONGELADO (LeadStatus no codigo).
    Funis customizados por tenant ficam para os Playbooks (Sprint 10),
    sem tabela de estagios por org nesta sprint.
```

---

## Estimativa

```
T1: Models (Lead, Memory, Event)        — 4h
T2: Migration Alembic                   — 1h
T3: Merge service                       — 6h
T4: Memory extractor (placeholder)      — 2h
T5-T7: Leads API + timeline             — 10h
T8: Memories API                        — 3h
T9-T11: UI lista + detalhe + cadastro   — 15h
T12: Testes (isolation + CRUD + merge)  — 8h
T13: CSV Import (se D2 = sim)           — 4h

TOTAL: ~49-53h (1.5-2 semanas para 1 dev)
```

---

## Riscos

| Risco | Mitigacao |
|---|---|
| Merge incorreto fundir pessoas diferentes | Regra conservadora (so campos vazios) + evento auditavel + D1 |
| Memory extractor (IA) detectar errado | Confidence < 1.0 + editavel pelo user + placeholder nesta sprint |
| Performance com 10k+ leads | Indices (org, phone), (org, email), (org, status) |
| Soft delete vazar em queries | `status != 'deletado'` em TODA listagem (padrao do service) |
| Multi-tenant leak | Testes de isolamento + 404 generico + org do contexto |

---

*"Lead sem memoria e' lead perdido."*

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