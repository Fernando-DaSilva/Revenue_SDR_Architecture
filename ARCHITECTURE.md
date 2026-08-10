# ARCHITECTURE.md — Decisoes Tecnicas e ADRs (v2.2)

> **COMO o produto e construido.** Decisoes arquiteturais vigentes, com
> contexto, decisao e consequencias. Reflete o estado real do codigo
> (v0.2.0+). Quando uma decisao muda, edita-se este arquivo.

---

## 1. Visao de alto nivel

```
                         HOJE (v0.2.0)                     ALVO (Sprint 9+)
        +-----------------------------------+   +-----------------------------------+
        |  Uma instalacao FastAPI por       |   |  Platform Console (MyraOS)        |
        |  ambiente, multi-tenant logico    |   |   + registry de releases          |
        |  (Organizations isoladas por      |   |   + monitoramento agregado        |
        |  organization_id)                 |   |   + billing                       |
        |                                   |   |        |                          |
        |  app self-contained:              |   |  Client Node (VPS por cliente)    |
        |   - Turso (libSQL) / .db local    |   |   + este app, 1 tenant ou poucos  |
        |   - assets vendored (sem CDN)     |   |   + Update Agent (systemd)        |
        |   - Alembic upgrade no boot       |   |   + pull de updates a cada 6h     |
        +-----------------------------------+   |   + rollback automatico           |
                                                 +-----------------------------------+
```

A transicao e incremental: o multi-tenancy logico de hoje vira o
multi-tenancy fisico de amanha sem reescrita, porque o app ja e
self-contained e o schema ja e isolado por tenant.

## 2. Arquitetura do app (v0.2.0 — vigente)

```
Request
  |
  v
SecurityHeadersMiddleware  (headers de endurecimento + CSP)
  v
TenantResolutionMiddleware (ASGI puro: custom_domain/subdominio -> header
  |                         -> query param (dev) -> default; seta
  |                         request.state.organization + ContextVar)
  v
RateLimitingMiddleware     (Rate limit por tenant/IP via Valkey/Redis/DiskCache)
  v
Router (fino)
  |
  v
Dependency (auth/tenancy)  CurrentOrganization, CurrentUser (cookie|Bearer),
  |                        require_role(...)
  v
Service (*/service.py)     regras de negocio + queries (SEMPRE filtradas
  |                        por organization_id)
  v
Model (SQLModel)           TenantMixin (organization_id obrigatorio) +
                           TimestampMixin (UTC aware, onupdate)
```

### Invariantes (verdades que nao se quebram)

1. **App factory**: `create_app(settings, db_engine)` — sem singletons de
   modulo; tudo vive em `app.state` (settings, db_engine, jinja_env).
2. **Camadas**: rota fina -> service -> model. Query NUNCA na rota.
3. **Erros**: envelope `{"error": {code, message, details}}` via
   `AppError` + handlers registrados na factory.
4. **Validacao de entrada nos schemas pydantic**, nao nos table models
   (SQLModel `table=True` NAO valida). Banco garante integridade via
   constraints (unique, FK, NOT NULL).
5. **Schema so muda via migration Alembic (Batch Mode).** `create_all` so em testes.
6. **Templates via `app/web/templating.py::render()`** — injeta tema/branding
   do tenant automaticamente.
7. **Agentes de IA Codificadores**: Devem obrigatoriamente se submeter ao harness de teste e linting (`pytest`, `ruff`, `alembic` round-trip) antes de concluir qualquer pull request ou commit (ADR-026).

## 3. Multi-tenancy — defesa em profundidade Zero-Trust

| Camada | Mecanismo |
|---|---|
| Banco | `organization_id` FK NOT NULL em toda tabela de dominio; uniques compostas (ex: `uq_users_org_email`) |
| Middleware | Resolve tenant por request; seta `request.state.organization` + ContextVar `current_organization` |
| JWT | Claim `org` precisa bater com o tenant do request — token nao opera fora do tenant de origem |
| Services | Toda query filtra `organization_id`; acesso por ID retorna **404 generico** cross-tenant (nao vaza existencia) |
| Testes | Suite de isolamento cross-tenant obrigatoria por feature (57+ testes) |

Resolucao de tenant (precedencia): `custom_domain` exato (Host) ou
subdominio -> header `X-Tenant-Slug` -> query param (so dev) ->
`DEFAULT_TENANT_SLUG` (se configurado; vazio em producao = 404).

## 4. Autenticacao

- **Senhas**: Argon2id via pwdlib (recomendacao OWASP).
- **Sessao**: JWT HS256 (PyJWT) com `sub`, `org`, `type=session`, `jti`
  unico (preparado para revogacao futura), expiracao configuravel.
- **Transporte duplo**: cookie HttpOnly `rsdros_session` (precedencia,
  browser) + `Authorization: Bearer` (API). O login JSON entrega os dois.
- Cookie: `secure` em producao, `samesite=lax`, `path=/`.

## 5. Eventos append-only (visao de dados)

Sprint 2 introduz `lead_timeline_events`; Sprint 3 generaliza para uma
tabela central de eventos do dominio. Regras:

- Eventos sao **imutaveis** (append-only) e carregam `payload` JSON.
- Toda mudanca relevante emite evento: `created`, `status_changed`,
  `merged`, `memory_added`, `score_changed`, `cadence_step_advanced`...
- Eventos alimentam: timeline do lead, scoring, analytics e replay.

## 6. Jobs assincronos e Fila de Tarefas (ADR-021)

- Fila resiliente via **Taskiq** (com backend Redis/Valkey ou AioSQLite embarcado para standalone VPS).
- Webhooks do WhatsApp/Instagram respondem `HTTP 202 Accepted` em `< 50ms` e delegam o processamento da LLM para os workers do Taskiq.
- Jobs **idempotentes** por construcao (chaves de dedup `job_key` + checagem de estado antes de agir).
- Retentativas com **Exponential Backoff + Jitter** e salvamento de falhas em **Dead Letter Queue (DLQ)**.

## 7. Estratégia de Banco de Dados, Armazenamento e Vetores (RAG Híbrido)

- **Hot Storage (Turso / libSQL local)**: Armazena dados de atendimento ativo, leads, conversas recentes e vetores ultraleves via `sqlite-vec` com resposta em $< 10\text{ ms}$ (ADR-002, ADR-016, ADR-022).
- **Cold Storage / DW (PostgreSQL / Supabase)**: Recebe réplicas D-1 de conversas históricas, relatórios do Manager Brain e índices semânticos `pgvector` HNSW (ADR-015, ADR-022).
- **Alembic Batch Migrations**: Todas as migrações exigem `render_as_batch=True` para garantir compatibilidade perfeita com SQLite/libSQL (ADR-024).

## 8. Orquestração de LLMs e Sistema Multi-Agente (LangChain, LangGraph & Instructor)

- **LangChain Core (`langchain-core`)**: Padrão oficial para abstração de LLMs, Prompts (`ChatPromptTemplate`), Ferramentas (`@tool`) e composição de fluxos LCEL (ADR-027).
- **LangGraph (`langgraph`)**: Orquestração de agentes baseados em estado (`StateGraph`), ciclos conversacionais, controle de histórico e interrupções para aprovação humana (*Human-in-the-Loop*) (ADR-028).
- **Instructor + Pydantic v2**: Utilizado para extrações de saída estruturada estrita em jobs de background (ADR-023).
- **Cadeia de Fallback Declarativa (`with_fallbacks`)**: Roteamento automático: Gemini 2.5 Flash / Claude 3.5 Sonnet -> GPT-4o-mini / Groq Llama-3.3 em caso de timeout ($> 2.5\text{s}$) ou erro 5xx (ADR-023, ADR-027).
- **Observabilidade & Tracing via LangSmith**: Telemetria visual de grafos, contabilidade de tokens por tenant e suite de Evals (ADR-029).
- **System Prompt Caching & Streaming**: Caching nativo de prompts para economia de 75-90% de tokens e streaming em tempo real SSE via `astream_events` (ADR-005, ADR-019).

---

## 9. ADRs (Architecture Decision Records)

### ADR-001 — HTMX + Alpine.js + Tailwind (DaisyUI), NÃO React/Vue/Next
- **Contexto**: SPA pesada adiciona complexidade sem ganho para um app server-driven white-label. O uso prévio de "CSS puro" limitava a estética e escalabilidade visual moderna.
- **Decisão**: Jinja2 + HTMX (requisições parciais) + Alpine (microinteratividade). Adoção do **Tailwind CSS + DaisyUI** para design system e componentização semântica, integrado perfeitamente ao ecossistema sem JS extra (Virtual DOM).
- **Consequências**: Frontend dinâmico, server-rendered, com estética altamente profissional. Necessidade de rodar o CLI do Tailwind (com DaisyUI) localmente para gerar o `theme.css` final e integrá-lo via variáveis nativas para o sistema de White Label (ADR-013). Libs HTMX/Alpine permanecem **vendored**.

### ADR-002 — Turso (libSQL) & Embedded Replicas primeiro, NAO Postgres no MVP
- **Contexto**: uma VPS por cliente pede zero-infra e custo zero, mas exige resiliência de backup e performance.
- **Decisao**: Usar **Turso (libSQL)** com suporte a arquivo local `.db` (modo standalone) e opção de *Embedded Replicas* para backup automático em nuvem via dialect `sqlite+libsql://`. SQLModel/SQLAlchemy e Alembic 100% compatíveis (ver ADR-016).
- **Consequencias**: backups automatizados em nuvem sem travar I/O local; leitura ultrarrápida no `.db` local da VPS; custo R$ 0,00 no modo standalone ou no plano Hobby do Turso.

### ADR-003 — Z-API para Zap no MVP (Sprint 4)
- **Contexto**: API oficial (Meta Cloud) tem friccao de aprovacao/custo no MVP; Z-API (unofficial) funciona hoje.
- **Decisao**: abstracao `ZapProvider`; implementacao Z-API primeiro; migracao para Twilio/Meta e mecanica pela interface.
- **Consequencias**: risco de banimento do numero mitigado pela abstracao e por playbooks de aquecimento.

### ADR-004 — VPS dedicada por cliente, NAO SaaS compartilhado
- **Contexto**: LGPD, isolamento absoluto e white-label real (dominio do cliente).
- **Decisao**: modelo On-Premise-as-a-Service com Platform Console como orquestrador (Sprint 9+).
- **Consequencias**: app precisa ser self-contained (assets vendored, SQLite, Alembic no deploy); distribuicao de updates exige Update Agent + rollback.

### ADR-005 — SSE, NAO WebSocket
- **Contexto**: real-time do produto e predominantemente servidor->cliente (mensagens da IA, transcricao, DHS).
- **Decisao**: SSE (sse-starlette) com broker in-memory, migravel a Redis Pub/Sub. WebSocket so se o vendedor digitar pela plataforma (S6+).
- **Consequencias**: simplicidade de proxy/auth; auto-reconnect nativo.

### ADR-006 — Argon2id + PyJWT, NAO passlib/python-jose (v0.2.0)
- **Contexto**: passlib sem release desde 2020 (incompativel bcrypt>=4.1); python-jose abandonado com CVEs abertos (CVE-2024-33663/64).
- **Decisao**: pwdlib (Argon2id) para senhas; PyJWT para tokens.
- **Consequencias**: stack de seguranca mantida; hashes Argon2id desde o seed; sem legado bcrypt a migrar.

### ADR-007 — App factory + service layer (v0.2.0)
- **Contexto**: v0.1.0 tinha engine/settings em import-time, tornando testes frageis (hack de env antes do import) e acoplando tudo.
- **Decisao**: `create_app(settings, db_engine)`; estado em `app.state`; regras de negocio em `*/service.py`; rotas finas.
- **Consequencias**: testes constroem apps isoladas com engine em memoria injetada; nenhum singleton de modulo.

### ADR-008 — Envelope de erros unico (v0.2.0)
- **Contexto**: respostas de erro inconsistentes (`{"detail": ...}` solto).
- **Decisao**: `AppError` + handlers -> `{"error": {code, message, details}}` em JSON para API e pagina HTML minima para rotas web.
- **Consequencias**: contrato de erro estavel para clients; codigos testaveis (`tenant_not_found`, `authentication_failed`...).

### ADR-009 — Tenant por middleware ASGI puro + ContextVar (v0.2.0)
- **Contexto**: BaseHTTPMiddleware quebra propagacao de contextvars e adiciona overhead; futuros jobs/mixins de ORM precisam do tenant sem Request.
- **Decisao**: middleware ASGI puro que seta `request.state.organization` e a ContextVar `current_organization`.
- **Consequencias**: ContextVar disponivel para services/jobs; custo de 1 query por request (cacheavel no futuro).

### ADR-010 — Alembic desde o dia zero (v0.2.0)
- **Contexto**: v0.1.0 criava tabelas via `create_all` (sem versionamento) e a pasta alembic/ era vazia.
- **Decisao**: schema so muda via migration; `create_all` apenas em testes; `./start` roda `alembic upgrade head` antes de subir.
- **Consequencias**: deploy em VPS = pull + migrate; rollback de schema possivel (downgrade testado).

### ADR-011 — Assets frontend vendored, NAO CDN (v0.2.0)
- **Contexto**: CDN quebra o requisito self-contained do modelo VPS (ADR-004) e vaza versao/origem.
- **Decisao**: HTMX/Alpine fixados em `app/web/static/js/vendor/`; CSP `script-src 'self'` (com `unsafe-eval` enquanto Alpine exigir).
- **Consequencias**: app funciona offline; atualizacao de libs e deliberada (download + commit).

### ADR-012 — Validacao nos schemas, NAO nos table models (v0.2.0)
- **Contexto**: SQLModel `table=True` nao executa validacao pydantic — `regex=`/`min_length=` em table models sao decorativos (descoberto na reescrita).
- **Decisao**: validacao de entrada vive nos schemas de API; banco garante integridade via constraints (unique, FK, NOT NULL).
- **Consequencias**: fronteira clara: schemas validam, models persistem, banco reforca.

### ADR-013 — Customização de Idiomas por Tela/Usuário e Presets de Cores (v2.1.0)
- **Contexto**: A internacionalização padrão baseada em arquivos é rígida demais para parceiros white-label que precisam adaptar nomes e termos conforme suas marcas.
- **Decisão**: Criar a tabela `user_translations` para sobrescrever chaves de tradução por tela e por usuário. Definir 5 presets de cores iniciais (Sakura Bloom, Emerald Garden, Ocean Breeze, Obsidian Night e Amber Warmth) e injetar variáveis CSS no template base.
- **Consequências**: Maior flexibilidade no White-label real. Cache LRU em memória para mitigar overhead de query no banco.

### ADR-014 — Logs Estruturados e Observabilidade (JSON, Tracing)
- **Contexto**: Operação em VPS/SaaS exige detecção rápida de gargalos de latência e erros no cliente.
- **Decisão**: Implementar logs unificados em JSON Lines (`structlog`), propagação do `request_id` e endpoint dedicado (`/api/v1/logs/client`) para ingestão de eventos/erros do Client-side.
- **Consequências**: Tracing robusto das jornadas de requests com contexto enriquecido (`tenant_id`, `user_id`).

### ADR-015 — Arquivamento de Dados, Tiering de Histórico e Exportação Analítica (PostgreSQL / Supabase)
- **Contexto**: Manter histórico ilimitado de conversas sobrecarregaria o banco local (Turso/libSQL).
- **Decisão**: Instituir modelo de **Storage Tiering (Hot/Cold)**. O Turso/libSQL local mantém apenas dados ativos. Pipeline de ETL assíncrono (D-1) replica conversas consolidadas para **PostgreSQL / Supabase (Cold Storage / DW)** com `pgvector` e FTS.
- **Consequências**: Turso/libSQL local ultraveloz (< 10ms); histórico completo acessível via DW.

### ADR-016 — Adoção do Turso (libSQL) com Suporte a Embedded Replicas e Fallback Local
- **Contexto**: SQLite isolado trazia desafios para backups em tempo real sem trava de arquivos.
- **Decisão**: Adotar o Turso (libSQL) via `sqlalchemy-libsql`. O sistema grava e lê no arquivo `.db` local da VPS (custo zero, offline-first) e opcionalmente sincroniza em background com o cluster Turso em nuvem.
- **Consequências**: Backup contínuo em nuvem sem travar I/O local; 100% compatível com SQLModel e Alembic.

### ADR-017 — Standalone Zap SDR Micro-App, Grid de Painéis 3 Colunas e Protocolo de Auto-Sync em Background (`02_ZAP_Prototype`)
- **Contexto**: Permitir atendimento ao vivo rápido por vendedores sem carregar a interface administrativa central.
- **Decisão**: Implementar o sub-produto **02_ZAP_Prototype** em layout grid de 3 colunas com controle independente de painéis, alternador de modo (`Copilot Active` vs `SDR Humano`), player de áudio com Whisper, gráfico DHS Score e protocolo de Auto-Sync em Background com fila offline em `localStorage`.
- **Consequências**: Experiência ultra-leve para o operador com garantia de sincronia total de histórico com o backend.

### ADR-018 — Segurança Multi-Tenant Zero-Trust, Hardening de Auth e Conformidade LGPD
- **Contexto**: Garantia de isolamento absoluto entre organizações comerciais e conformidade LGPD.
- **Decisão**: Padrão **Zero-Trust Multi-Tenancy**. Injeção mandatória do `organization_id` via ContextVar no middleware, retorno de **404 Not Found genérico** em tentativas cross-tenant. Uso exclusivo de Argon2id para senhas, PyJWT (HS256) para sessões, e cookies HttpOnly SameSite=Lax.
- **Consequências**: Isolamento completo a nível de dados e APIs; conformidade regulatória total.

### ADR-019 — SLAs de Performance, Orçamentos de Latência (P95) e Otimização FinOps
- **Contexto**: Atendimento de alta velocidade no Zap sem extrapolar custos de LLM ou CPU da VPS.
- **Decisão**: SLAs de latência P95 (Turso Local $< 10\text{ ms}$, API Core $< 50\text{ ms}$, Eventos SSE $< 100\text{ ms}$, Ingestão Z-API $< 300\text{ ms}$, Transcrição Whisper $< 1.5\text{ s}$, Agente SDR $< 1.2\text{ s}$). Aplicação de Prompt Caching e Roteamento Multi-Tier de LLMs.
- **Consequências**: Resposta instantânea no Zap e previsibilidade financeira por tenant.

### ADR-020 — Garantia de Qualidade (QA), Matriz de Testes e Controle de Qualidade Visual
- **Contexto**: Necessidade de manter zero regressões funcionais e integridade de migrações de banco.
- **Decisão**: Matriz de qualidade obrigatória: **100% de cobertura nos testes de isolamento multi-tenant** (`tests/test_tenant_isolation.py`), **> 85% de cobertura total nos serviços**, validação round-trip de migrations e inspeção de qualidade visual.
- **Consequências**: Deploys seguros e fidelidade aos protótipos visuais.

### ADR-021 — Processamento de Jobs Assíncronos, Filas de Tarefas e Resiliência (Taskiq / SAQ)
- **Contexto**: Evitar travamento do event loop FastAPI durante execuções de LLM e webhooks inbound.
- **Decisão**: Adotar **Taskiq** com brokers Redis (nuvem/multi-worker) ou AioSQLite (standalone VPS). Tarefas idempotentes via `job_key`, retentativas com Exponential Backoff e Dead Letter Queue (DLQ).
- **Consequências**: Resposta HTTP 202 em webhooks em $< 50\text{ ms}$ e desacoplamento total do tempo de execução de LLMs.

### ADR-022 — Arquitetura Híbrida de RAG e Busca Vetorial (sqlite-vec + pgvector)
- **Contexto**: Necessidade de RAG em tempo real na VPS local e busca semântica profunda no histórico analítico.
- **Decisão**: RAG em duas camadas: **Hot RAG** com `sqlite-vec` local ($< 15\text{ ms}$) para playbooks ativos e **Cold RAG** com `pgvector` HNSW no PostgreSQL central. Utilização de **Reciprocal Rank Fusion (RRF)** combinando BM25/FTS + Busca Vetorial.
- **Consequências**: Precisão de recuperação $> 95\%$ com custo zero na VPS do cliente.

### ADR-023 — Orquestração de LLMs, Saídas Estruturadas via Instructor e Cadeia de Fallbacks
- **Contexto**: Eliminar falhas de parsing JSON e respostas malformatadas de modelos de IA.
- **Decisão**: Utilização mandatória do **Instructor + Pydantic v2** para todas as saídas de LLM em jobs batch. Roteador de fallback automático (Gemini 2.5 Flash / Sonnet 3.5 -> GPT-4o-mini / Groq Llama-3.3) em timeouts ($> 2.5\text{s}$).
- **Consequências**: Garantia de tipagem estática Pydantic em todas as interações com LLMs e zero crashes por JSON sintaticamente inválido.

### ADR-024 — Migrações de Banco de Dados via Alembic em SQLite/libSQL (Batch Mode)
- **Contexto**: Limitações de DDL (`ALTER TABLE`) do SQLite travavam migrações de banco em produção.
- **Decisão**: Ativação obrigatória de `render_as_batch=True` no `alembic/env.py` e uso do gerenciador `op.batch_alter_table`. Validação round-trip (`upgrade -> downgrade -> upgrade`) mandatória no CI.
- **Consequências**: Alterações de esquema seguras sem corrupção ou travamento do banco SQLite/libSQL.

### ADR-025 — Estratégia de Caching em Camadas, Rate Limiting e Proteção de Ingestão (Valkey / Redis / In-Memory)
- **Contexto**: Reduzir overhead de queries de tenant/white-label e proteger o sistema contra abusos.
- **Decisão**: Caching em duas camadas (In-Memory LRU para marcas e traduções + Valkey/Redis/DiskCache para sessões e rate limit). Limitação de taxa por tenant/IP em rotas públicas e webhooks.
- **Consequências**: Carregamento instantâneo de páginas ($< 0.1\text{ ms}$ no cache) e proteção contra estouro de custos.

### ADR-026 — Guardiões de Engenharia para Codificação via Agentes de IA (AI-Agent Driven Development)
- **Contexto**: Evitar que Agentes de IA introduzam código sem filtro de tenant, sem migração Alembic ou com exceções não padronizadas.
- **Decisão**: Instituir o **AI Coding Agent Protocol**: separação estrita em camadas (Model -> Service -> Schema -> API), mandamento inegociável de filtro por tenant via `ContextVar`, retorno de 404 genérico e obrigatoriedade de passar 100% no harness de verificação (`pytest`, `ruff`, `alembic round-trip`) antes do commit.
- **Consequências**: Entregas autônomas limpas, alinhadas à arquitetura do projeto e sem regressões.

### ADR-027 — Orquestração de Agentes com Ecossistema LangChain e LangGraph
- **Contexto**: Necessidade de conduzir diálogos complexos, tool calling e fluxos multi-agente robustos.
- **Decisão**: Padronização no ecossistema **LangChain (`langchain-core`)** e **LangGraph (`langgraph`)** para abstração de modelos, ferramentas `@tool`, cadeias LCEL e fallbacks automáticos `with_fallbacks()`.
- **Consequências**: Orquestração multi-agente modular, resiliência contra indisponibilidade de provedores e integração limpa com FastAPI e Taskiq.

### ADR-028 — Workflows de Agentes Baseados em Estado com LangGraph e Human-in-the-Loop
- **Contexto**: Processos comerciais exigem manutenção de estado conversacional persistente e pausa para aprovação humana em ações sensíveis.
- **Decisão**: Modelagem de agentes como **Grafos Dirigidos de Estado (`StateGraph`)** com checkpointers (`MemorySaver` / SQLite / Turso) e suporte a interrupções `interrupt()` para handoff ao vendedor no Zap Copilot (`02_ZAP_Prototype`).
- **Consequências**: Determinismo, prevenção de ações indesejadas por IA e rastreabilidade total do estado conversacional.

### ADR-029 — Observabilidade, Tracing e Avaliação de Agentes com LangSmith
- **Contexto**: Diagnóstico de latência, contabilidade de tokens por tenant e validação de qualidade de prompts em produção.
- **Decisão**: Ingestão unificada via **LangSmith (`LANGCHAIN_TRACING_V2=true`)** integrada aos metadados de tenancy (`organization_id`), aliada a suítes de Evals automatizadas no CI/CD.
- **Consequências**: Visibilidade total de cada nó de execução dos agentes e contabilidade precisa FinOps por tenant.

---

*"Arquitetura e a arte de tomar decisoes faceis de reverter e previsiveis para serem executadas por Agentes de IA."*
