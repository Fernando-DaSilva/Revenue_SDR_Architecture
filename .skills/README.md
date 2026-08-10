# Skills — Indice

> **Todas as skills carregaveis pelos agentes externos.**

## Como usar

Skills sao arquivos markdown em `.skills/` que agentes de IA carregam pra ter contexto tecnico sobre o projeto.

**Workflow**:
1. Abra o agente (Claude Code, Codex, OpenCode, Antigravity Agent, etc)
2. Carregue a skill `revenue-sdr-os-architect.md` (sempre primeiro)
3. Carregue skills especificas conforme a tarefa
4. Carregue o prompt correspondente em `prompts/` ou `Sprints/XX/prompts/`

## Indice de skills

### `.skills/revenue-sdr-os-architect.md` (PRINCIPAL — SEMPRE carregar)

```
Visao geral do produto, stack, principios inegociaveis,
modelo de dados, estrutura do repo, ONDE encontrar tudo.
```

**Quando carregar**: TODA tarefa, ANTES de qualquer outra skill.

### `.skills/ai-agent-coding-guidelines.md` (GUARDIÕES DE CODIFICAÇÃO)

```
Diretrizes e guardiões para Agentes de IA construindo código:
  - Separação de camadas (models, schemas, service, api)
  - Regras de segurança Multi-Tenant Zero-Trust
  - Harness de verificação pré-commit (pytest, ruff, alembic round-trip)
  - Anti-patterns e checklist
```

**Quando carregar**: carregar sempre que for implementar ou refatorar código backend/frontend.

### `.skills/fastapi-multi-tenant.md`

```
Padroes de API FastAPI para o projeto:
  - Estrutura de router (list, create, get, patch, delete)
  - Dependencies padrao (get_current_user, get_current_organization)
  - Tenant resolution (subdomain, header, query)
  - Schemas Pydantic separados do SQLModel
  - CORS, JWT, cookies
  - Anti-patterns (cross-tenant 404, NAO 403)
```

**Quando carregar**: criar/modificar endpoint, router, dependency.

### `.skills/sqlmodel-migration.md` e `.skills/alembic-sqlite-batch-migrations.md`

```
Padroes de SQLModel + Alembic em Modo Batch (SQLite/libSQL):
  - Tenant model (organization_id FK NOT NULL)
  - ID factory (prefixed: user_xxx, lead_xxx)
  - JSON fields (tags, custom_fields)
  - Soft delete (status='deletado')
  - Alembic setup + autogenerate com render_as_batch=True
  - Migrations reversiveis com op.batch_alter_table (upgrade + downgrade)
```

**Quando carregar**: criar/alterar model, criar migration Alembic.

### `.skills/llm-agent-orchestration-and-instructor.md`

```
Orquestração de LLMs e Saídas Estruturadas via Instructor:
  - Instructor + Pydantic v2 para extração estrita de JSON
  - LLM Router com fallback automático (Gemini/Sonnet -> GPT-4o-mini/Llama-3.3)
  - System Prompt Caching (economia de 75-90% de tokens)
  - Prevenção de exceções de parsing JSON
```

**Quando carregar**: implementar extração de memória em batch ou validações estritas de schema.

### `.skills/langchain-langgraph-agent-architecture.md` (ORQUESTRAÇÃO MULTI-AGENTE)

```
Orquestração de Agentes Conversacionais e Grafos de Estado via LangChain & LangGraph:
  - Models com fallbacks nativos (with_fallbacks)
  - Definition de ferramentas @tool com Pydantic args_schema
  - Grafos de estado (StateGraph) com MemorySaver Checkpointer
  - Human-in-the-Loop interrupts (interrupt()) para aprovação no Zap Copilot
  - Streaming SSE via astream_events
  - Observabilidade e Tracing no LangSmith (LANGCHAIN_TRACING_V2=true)
```

**Quando carregar**: implementar ou refatorar qualquer Agente SDR conversacional, fluxo multi-agente, ou tool calling.

### `.skills/background-jobs-taskiq-arq.md`

```
Processamento de Jobs Assíncronos e Fila de Tarefas (Taskiq / SAQ):
  - Retorno HTTP 202 em webhooks (<50ms)
  - Idempotência com job_key e cache deduplication
  - Configuração de retentativas com Exponential Backoff e DLQ
  - Configuração de workers standalone (AioSQLite) ou nuvem (Redis)
```

**Quando carregar**: criar tarefas em segundo plano, webhooks ou cadências.

### `.skills/vector-search-rag-pgvector.md`

```
Busca Vetorial Híbrida e RAG (sqlite-vec + pgvector):
  - Hot RAG local (<15ms) na VPS via sqlite-vec com pré-filtragem por tenant
  - Cold RAG no Data Warehouse via pgvector com índice HNSW
  - Algoritmo Reciprocal Rank Fusion (RRF) combinando BM25/FTS + Cosine Similarity
  - Deduplicação de embeddings via hash MD5
```

**Quando carregar**: criar busca semântica, bases de conhecimento ou RAG comercial.

### `.skills/htmx-alpine-component.md`

```
Padroes de UI:
  - Template base com CSS variables
  - render_template() helper (passa tipos hashable)
  - CSS variables para white-label (NAO hardcode cor)
  - HTMX patterns (partial updates, forms, polling)
  - Alpine.js patterns (toggle, modal, form state)
  - Componentes reusaveis (partials)
  - SSE integration
```

**Quando carregar**: criar pagina, componente, UI interativa.

### `.skills/pytest-tenant-isolation.md`

```
Padroes de testes pytest:
  - Fixtures (reset_db, seed_two_orgs, auth_headers_*)
  - Testes de tenant isolation (CRITICOS, >=5 por endpoint)
  - Testes de CRUD basico (>=3 por endpoint)
  - Naming, docstrings, AAA pattern
  - Anti-patterns (sqlite em memoria, IDs hardcoded)
```

**Quando carregar**: criar testes (SEMPRE pra features multi-tenant).

### `.skills/whatsapp-zapi-integration.md`

```
Integracao WhatsApp via Z-API:
  - Interface WhatsAppProvider (abstracao)
  - ZAPIProvider implementation
  - Webhook handler (validar instance_id, async processing via Taskiq)
  - Factory pattern (migracao futura pra Twilio)
  - Multi-tenant (instance_id por Organization)
```

**Quando carregar**: implementar webhook WhatsApp, envio de mensagem, Z-API.

### `.skills/sse-realtime-pattern.md`

```
Server-Sent Events (real-time):
  - SSE endpoint com EventSourceResponse (sse-starlette)
  - Broker in-memory (publish/subscribe)
  - Keep-alive ping (evita timeout de proxy)
  - Auth obrigatoria + tenant isolation
  - Cliente JS com auto-reconnect
```

**Quando carregar**: implementar notificacoes live, transcricao, grafico DHS.

### `.skills/observability-stack.md`

```
Observabilidade (Prometheus + Grafana + structlog):
  - Metricas Prometheus (latencia, count, errors, LLM tokens)
  - Logger estruturado em JSON
  - Ingestor de client-side logs (/api/v1/logs/client)
```

**Quando carregar**: adicionar observabilidade, logs, métricas.

### `.skills/whatsapp-sdr-prototype-architect.md`

```
Engenharia do Standalone Zap SDR Micro-App (02_ZAP_Prototype):
  - Arquitetura Standalone & Auto-Sync em Background
  - Grid de 3 Colunas e Controle Dinâmico de Painéis
  - Gráfico DHS Score via Chart.js v4
```

**Quando carregar**: integrar a interface standalone do Zap Copilot.

---

## Combinacoes comuns

```
Criar/Refatorar Código de Backend:
  + revenue-sdr-os-architect
  + ai-agent-coding-guidelines
  + fastapi-multi-tenant
  + pytest-tenant-isolation

Criar Agente de IA com RAG e Tool Calling:
  + revenue-sdr-os-architect
  + llm-agent-orchestration-and-instructor
  + vector-search-rag-pgvector
  + background-jobs-taskiq-arq

Criar Model + Migration Alembic:
  + revenue-sdr-os-architect
  + sqlmodel-migration
  + alembic-sqlite-batch-migrations
```

---

*"Skill e' o cerebro carregavel do agente."*