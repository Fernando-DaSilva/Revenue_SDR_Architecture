# AGENTS.md — Manual para Agentes de Codificacao (v2.3)

> **Voce e um agente de IA construindo o Revenue SDR OS.**
> Este manual diz EXATAMENTE como trabalhar. As regras duras de codigo
> vivem no AGENTS.md do repo de codigo (`~/AGENCIA/SDR/AGENTS.md`) — leia
> os dois.

---

## TL;DR

```
1. Leia FOUNDATION.md (visao) + ARCHITECTURE.md (decisoes vigentes ADR-001 a ADR-032)
2. Carregue .skills/revenue-sdr-os-architect.md + .skills/ai-agent-coding-guidelines.md + .skills/langchain-langgraph-agent-architecture.md + skills da tarefa
3. Leia o spec da sprint em Sprints/XX_*/ (+ prompts por tarefa)
4. Code no repo ~/AGENCIA/SDR/ e ~/AGENCIA/02_ZAP_Prototype/ seguindo as 4 camadas (Model -> Service -> Schema -> API)
5. Valide com o harness de teste pré-commit (pytest >85% + ruff + alembic batch round-trip)
6. Commit + push (Conventional Commits PT-BR)
```

---

## Setup inicial (uma vez)

```bash
git clone https://github.com/Fernando-DaSilva/Revenue_SDR_OS.git ~/AGENCIA/SDR
cd ~/AGENCIA/SDR

python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

./start        # valida env, aplica migrations em modo batch, roda seed se vazio, sobe
pytest         # 57+ testes devem passar
```

Tenants demo: `admin@clinica-bela.com` / `admin@imob-center.com` (senha123),
em `http://<slug>.localhost:8000` (configurar /etc/hosts).

---

## Arquitetura vigente (v0.2.0+) — onde as coisas moram

```
app/
+-- main.py                  # create_app(settings, db_engine) — app factory
+-- core/                    # config, security (Argon2id/PyJWT), errors, logging
+-- db/                      # engine factory, session dep, mixins (TenantMixin)
+-- tenancy/                 # middleware ASGI + ContextVar de tenant (ADR-009, ADR-018)
+-- tasks/                   # Taskiq broker, TenantTaskiqMiddleware + jobs (ADR-021, ADR-030)
+-- ai/                      # Instructor clients, LLM Router, prompt templates, RAG (ADR-022, ADR-023, ADR-027, ADR-028)
+-- organizations/           # models, schemas, service, api
+-- users/                   # models, schemas, service, api
+-- auth/                    # service, dependencies, schemas, api
+-- themes/                  # CSS variables + branding (ADR-013)
+-- health/                  # liveness/readiness
+-- web/                     # templating Jinja2, pages/, templates/, static/
alembic/                     # env.py (render_as_batch=True) + versions/ (ADR-024)
tests/                       # pytest isolado (SQLite em memoria por teste)
```

### Invariantes que NUNCA se quebram

1. **App factory** — sem singletons de modulo; estado em `app.state`.
2. **Camadas** — rota fina -> `*/service.py` -> model. Query NUNCA na rota.
3. **Tenancy Zero-Trust** — toda query filtra `organization_id`; cross-tenant = 404 generico; claim `org` do JWT bate com o tenant do request; desabilitado o override não autenticado de `X-Tenant-Slug` em produção (ADR-018).
4. **Erros** — `AppError` + envelope `{"error": {code, message, details}}`. NAO usar HTTPException solta.
5. **Validacao nos schemas** — table models SQLModel NAO validam entrada.
6. **Schema via Alembic Batch Mode** — `create_all` so em testes; migrations obrigatoriamente testadas via round-trip com `op.batch_alter_table` (ADR-024).
7. **Auth dupla** — cookie (precedencia) + Bearer; senhas via Argon2id (`pwdlib`), JWT HS256 com `jti` (ADR-006 / ADR-018).
8. **Validacao de entrada de tenant** — `organization_id` SEMPRE do contexto ContextVar, NUNCA do payload.
9. **Fila e Jobs Assíncronos com TenantTaskiqMiddleware** — Webhooks respondem HTTP 202 em $< 50\text{ ms}$ e delegam para o Taskiq. O `TenantTaskiqMiddleware` serializa e hidrata o `organization_id` no worker. Em modo standalone, utilizar `taskiq_queue.db` separado do `app_data.db` (ADR-021, ADR-030).
10. **Orquestração de LLMs e Agentes** — Agentes conversacionais e multi-agentes usam obrigatoriamente **LangChain (`langchain-core`)** e **LangGraph (`StateGraph`)** com fallbacks `with_fallbacks()` e checkpointers persistentes de estado (`AsyncSqliteSaver` / Turso `.db` local; uso de `MemorySaver` in-memory é vedado em produção). Chamadas 1-shot de extração usam Instructor + Pydantic v2 (ADR-023, ADR-027, ADR-028).
11. **SLAs de Performance (P95)** — Turso local < 10ms, Core API < 50ms, SSE < 100ms, Webhook < 50ms, Whisper < 1.5s, SDR Agent < 1.2s. Roteador LLM configurado com timeout primário estrito de 900ms e limite acumulado de fallback de 1.8s (ADR-019, ADR-023).
12. **Matriz de Testes & Guardiões de IA** — Cobertura geral > 85%, isolamento multi-tenant 100% (ADR-020, ADR-026).
13. **Observabilidade & Tracing** — Grafos de agente repassam obrigatoriamente `tags` e `metadata` com `organization_id` e `lead_id` para o **LangSmith** (`LANGCHAIN_TRACING_V2=true`) (ADR-029).
14. **Human-in-the-Loop** — Ações sensíveis disparam `interrupt()` no LangGraph para confirmação no Zap Copilot (`02_ZAP_Prototype`). Jobs sem resposta humana após 15 minutos devem escalar notificação no Manager Brain (ADR-028).
15. **Protocolo de Reidratação de Cold Storage** — Ingressos de leads inativos (>30d arquivados no Supabase DW) acionam busca automática no `LeadService` para reidratar perfil, memórias e últimas 10 mensagens no Turso Hot Storage local na VPS. Modelo de embedding fixado em 1536d (`text-embedding-3-small`) em ambos os bancos (ADR-015, ADR-031).
16. **Proteção WhatsApp Anti-Ban & Meta 24h** — Mensagens ativas ou de IA após 24h da última interação do lead são BLOQUEADAS de enviar texto livre (*freeform*), exigindo aprovação/envio de HSM Templates. Envios usam rate limiter (max 1 msg/3-5s), jitter dinâmico (2.0s-6.0s), status `composing` e download assíncrono de áudios no Taskiq (ADR-032).

---

## Workflow padrao por tarefa

### A. Entender
1. Releia o brief + spec da sprint (`Sprints/XX_*/README.md`)
2. Busque nos protótipos (`01_SDR_Prototype` e `02_ZAP_Prototype`) pelos componentes visuais correspondentes
3. Confirme com o usuario SE houver ambiguidade (nao invente decisao)

### B. Planejar
1. Models/migrations novos em modo batch? 2. Endpoints e Schemas Pydantic? 3. Taskiq background tasks com `TenantTaskiqMiddleware`? 4. Instructor LLM schemas? 5. Testes de isolamento & unitários (>85%)?

### C. Implementar em camadas
1. Model (no pacote de dominio) -> `alembic revision --autogenerate` (validando `op.batch_alter_table`)
2. Service (regras + queries filtradas por tenant via ContextVar)
3. Schemas (validacao de entrada pydantic v2)
4. API (`*/api.py`) e/ou pagina (`app/web/pages/`)
5. Testes (CRUD + isolamento cross-tenant em `tests/`)

### D. Harness de Verificação Pré-Commit (Tudo precisa passar 100%)

```bash
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=85  # Cobertura >85% + 100% isolamento
ruff check app/ tests/ scripts/ alembic/                              # Lint de código e segurança
ruff format --check app/ tests/ scripts/                              # Formatação estrita
alembic upgrade head && alembic downgrade -1 && alembic upgrade head    # Round-trip de migration
./start &                                                             # Teste de inicialização e saúde
curl http://127.0.0.1:8000/api/v1/health/
```

### E. Commit (Conventional Commits PT-BR)

`feat:` nova feature | `fix:` bug | `docs:` documentacao | `refactor:` |
`test:` testes | `chore:` manutencao.

---

## Erros comuns (NUNCA faca)

```
[X] Query sem filtro de tenant        -> SEMPRE .where(org_id == ...)
[X] 403 em cross-tenant               -> use 404 generico
[X] organization_id vindo do payload  -> SEMPRE do contexto ContextVar
[X] Despachar Taskiq sem middleware   -> use TenantTaskiqMiddleware para propagar tenant
[X] MemorySaver em produção           -> use AsyncSqliteSaver (checkpointer persistente)
[X] Timeout LLM primário > 900ms     -> mantenha <= 900ms para respeitar P95 SLA < 1.2s
[X] Freeform message > 24h no Zap     -> forçar uso de HSM Template (Meta 24h Window)
[X] Mesclar app_data.db e queue.db    -> usar taskiq_queue.db separado em standalone VPS
[X] HTTPException solta               -> use AppError + subclasses
[X] Parsing manual de JSON de LLM     -> use Instructor + Pydantic v2 (ADR-023)
[X] Processar LLM dentro de Rota HTTP  -> use Taskiq async background job (ADR-021)
[X] Migration sem op.batch_alter_table -> use modo batch do Alembic (ADR-024)
[X] datetime.utcnow()                 -> use db.base.utc_now (UTC aware)
[X] Commit sem pytest+ruff verdes     -> execute o harness de verificação
```

---

*"Nunca mais perca um lead por falta de acompanhamento."*
