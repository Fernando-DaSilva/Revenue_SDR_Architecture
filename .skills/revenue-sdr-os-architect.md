---
name: revenue-sdr-os-architect
description: |
  Carregue esta skill SEMPRE que for trabalhar no projeto Revenue SDR OS.
  Fornece contexto fundamental sobre o que e' o produto, arquitetura,
  principios inegociaveis, e onde encontrar skills/prompts especificos.
version: 2.2.0
author: Hermes (arquiteto)
license: Proprietary
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
metadata:
  hermes:
    tags: [revenue-sdr-os, multi-tenant, fastapi, htmx, white-label, taskiq, instructor, rag]
    homepage: https://github.com/Fernando-DaSilva/Revenue_SDR_OS
---

# Revenue SDR OS — Skill Principal

## O que e' o produto

**Revenue SDR OS** e' uma plataforma white-label multi-tenant que entrega o proprio sistema operacional de vendas (IA, omnichannel, playbooks, dashboards) pra empresas, agencias e redes de franquia.

**Promessa central**: Nunca mais perca um lead por falta de acompanhamento.

**Posicionamento**: A primeira Plataforma Operacional de Receita (Revenue OS) White Label.

**Diferencial**: VPS dedicada por cliente (dados nunca saem do servidor do cliente), multi-nivel (Platform → Brand → Organization → Unit → Team → User), white-label real.

---

## Stack inegociavel

```
+----------+---------------------+------------------------------------------------+
| Camada   | Tecnologia          | Por que                                         |
+----------+---------------------+------------------------------------------------+
| Frontend | HTMX + Alpine.js    | Hypermedia-driven, server-rendered             |
|          | + Tailwind/DaisyUI  | Cada tenant injeta seu proprio CSS (white-label)|
| Backend  | FastAPI async       | SSE nativo, async I/O, OpenAPI 3.1             |
| ORM      | SQLModel            | Pydantic + SQLAlchemy, tipagem fullstack       |
| Database | Supabase PostgreSQL | PostgreSQL 16+ gerenciado unificado (ADR-037)  |
| Pooler   | Supavisor           | Transaction pooler (6543) / Session DDL (5432) |
| Schema   | Alembic PostgreSQL  | DDL transacional nativo PostgreSQL             |
| Real-time| SSE / Supabase RT   | Unidirecional server→client / WebSockets CDC    |
| Fila     | Taskiq + Postgres   | Jobs assíncronos desacoplados com ContextVar   |
| IA Engine| Instructor/Pydantic | Saídas estruturadas estritas sem exceções JSON |
| RAG      | Supabase pgvector   | pgvector HNSW 1536d + tsvector BM25 (RRF)      |
| Checkpoint| AsyncPostgresSaver  | Persistência de grafos LangGraph no Supabase   |
| Caching  | In-Memory + Redis   | LRU para temas/traduções + Rate Limiter por IP |
| Reverse  | Caddy               | Auto-SSL via Let's Encrypt                      |
+----------+---------------------+------------------------------------------------+
```

**NAO USE** (mesmo que alguem sugira):
- React / Next.js / Vue (frontend)
- WebSocket (use SSE)
- MongoDB / NoSQL
- Docker Swarm / Kubernetes (no MVP — unica VPS)
- Parsing manual de JSON de LLMs (use Instructor + Pydantic)

---

## Principios inegociaveis (leia antes de mudar qualquer coisa)

### 1. Multi-tenant e' o CORACAO do produto (Zero-Trust)

```
Toda tabela de dominio TEM organization_id (FK).
Toda query de dominio FILTRA por organization_id.
NUNCA confiar em dados que vem do request sem validar tenant.
```

**Defense in depth**:
- Layer 1: FK constraint + uniques compostas no banco
- Layer 2: middleware ASGI resolve tenant + ContextVar `current_organization`
- Layer 3: services filtram TODA query por organization_id
- Layer 4: claim `org` do JWT precisa bater com o tenant do request (Argon2id + PyJWT HS256 com `jti`)
- Layer 5: testes de isolamento cross-tenant (obrigatorios por feature)
- Layer 6: code review e guardiões de IA verificam manualmente

### 2. White-label via CSS variables
Tenant define cores no banco -> Backend injeta CSS variables -> UI usa var(--color-primary).

### 3. API-first interno
TODA funcionalidade que frontend usa TEM endpoint REST documentado sob `/api/v1/`.

### 4. Toda mensagem importante vira evento append-only
Tabela `events`: log append-only de TUDO que importa (`score_changed`, `stage_changed`, etc).

### 5. Orquestração de LLMs com Saídas Estruturadas
Saídas de LLM usam obrigatoriamente Instructor + Pydantic v2. Respostas síncronas no Zap possuem SLA $< 1.2\text{s}$ com Prompt Caching.

---

## Estrutura de pastas do codigo (repo ~/AGENCIA/SDR/, v0.2.0)

```
app/
+-- main.py                 # create_app(settings, db_engine) — app factory
+-- core/                   # config, security (Argon2id/PyJWT), errors, logging
+-- db/                     # engine factory, session dep, base/mixins (TenantMixin)
+-- tenancy/                # middleware ASGI puro + ContextVar de tenant
+-- tasks/                  # Taskiq broker + definições de jobs assíncronos
+-- ai/                     # Instructor clients, LLM Router, prompt templates, RAG
+-- organizations/          # models.py, schemas.py, service.py, api.py
+-- users/                  # models.py, schemas.py, service.py, api.py
+-- auth/                   # service.py, dependencies.py, schemas.py, api.py
+-- themes/                 # service.py (CSS variables + branding)
+-- health/                 # api.py (liveness/readiness)
+-- web/                    # templating.py (Jinja), pages/, templates/, static/
alembic/                    # env.py (render_as_batch=True) + versions/
scripts/                    # seed.py, verify.sh (harness de teste para agentes de IA)
tests/                      # pytest isolado — app + SQLite em memoria por teste
```

---

## CHECKLIST antes de comitar codigo (Guardião de IA)

```
[ ] Codigo compila sem erro (python -c "import app.main")
[ ] Testes passam (pytest) — suite completa (>85% cobertura)
[ ] Testes de isolamento cross-tenant da feature passam (100% isolamento)
[ ] ruff check + ruff format --check limpos
[ ] Migration criada com op.batch_alter_table e testada (upgrade head && downgrade -1 && upgrade head)
[ ] OpenAPI spec regenerada e consistente (/openapi.json)
[ ] Sem secrets hardcoded (use settings from .env)
[ ] Erros via AppError (envelope), NAO HTTPException solta
[ ] Docstrings PT-BR sem acentos + type hints em funcoes publicas
[ ] Commit message segue Conventional Commits (PT-BR)
```

---

*"Nunca mais perca um lead por falta de acompanhamento."*