# ARCHITECTURE.md — Decisoes Tecnicas e ADRs (v2.0)

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
        |   - SQLite WAL                    |   |   + este app, 1 tenant ou poucos  |
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
5. **Schema so muda via migration Alembic.** `create_all` so em testes.
6. **Templates via `app/web/templating.py::render()`** — injeta tema/branding
   do tenant automaticamente.

## 3. Multi-tenancy — defesa em profundidade

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

## 6. Jobs assincronos (Sprint 3+)

- Fila leve (ARQ ou APScheduler) para cadencias, missoes diarias e
  processamento de webhooks.
- Jobs **idempotentes** por construcao (chaves de dedup + checagem de
  estado antes de agir).
- Hoje (S2): processamento e sincrono; a fila entra com a Cadence Engine.

---

## 7. ADRs (Architecture Decision Records)

### ADR-001 — HTMX + Alpine.js, NAO React/Vue/Next
- **Contexto**: SPA pesada adiciona build pipeline, estado cliente e
  complexidade sem ganho para um app server-driven white-label.
- **Decisao**: Jinja2 + HTMX (requisicoes parciais) + Alpine
  (microinteratividade). CSS puro com variables por tenant.
- **Consequencias**: frontend simples, server-rendered; tema por CSS;
  libs **vendored** (self-contained para VPS offline).

### ADR-002 — SQLite (WAL) primeiro, NAO Postgres no MVP
- **Contexto**: uma VPS por cliente pede zero-infra; SQLite suporta
  dezenas de milhares de leads com WAL.
- **Decisao**: SQLite com `journal_mode=WAL`, `foreign_keys=ON`; SQLModel/
  SQLAlchemy desde o inicio, entao Postgres futuro e troca de URL.
- **Consequencias**: backups = copiar arquivo; sem servidor de banco;
  atencao a concorrencia de escrita (fila de jobs serializa quando entrar).

### ADR-003 — Z-API para WhatsApp no MVP (Sprint 4)
- **Contexto**: API oficial (Meta Cloud) tem friccao de aprovacao/custo no
  MVP; Z-API (unofficial) funciona hoje.
- **Decisao**: abstracao `WhatsAppProvider`; implementacao Z-API primeiro;
  migracao para Twilio/Meta e mecanica pela interface.
- **Consequencias**: risco de banimento do numero mitigado pela abstracao
  e por playbooks de aquecimento.

### ADR-004 — VPS dedicada por cliente, NAO SaaS compartilhado
- **Contexto**: LGPD, isolamento absoluto e white-label real (dominio do
  cliente).
- **Decisao**: modelo On-Premise-as-a-Service com Platform Console como
  orquestrador (Sprint 9+).
- **Consequencias**: app precisa ser self-contained (assets vendored,
  SQLite, Alembic no deploy); distribuicao de updates exige Update Agent +
  rollback.

### ADR-005 — SSE, NAO WebSocket
- **Contexto**: real-time do produto e predominantemente servidor->cliente
  (mensagens da IA, transcricao, DHS).
- **Decisao**: SSE (sse-starlette) com broker in-memory, migravel a Redis
  Pub/Sub. WebSocket so se o vendedor digitar pela plataforma (S6+).
- **Consequencias**: simplicidade de proxy/auth; auto-reconnect nativo.

### ADR-006 — Argon2id + PyJWT, NAO passlib/python-jose (v0.2.0)
- **Contexto**: passlib sem release desde 2020 (incompativel bcrypt>=4.1);
  python-jose abandonado com CVEs abertos (CVE-2024-33663/64).
- **Decisao**: pwdlib (Argon2id) para senhas; PyJWT para tokens.
- **Consequencias**: stack de seguranca mantida; hashes Argon2id desde o
  seed; sem legado bcrypt a migrar.

### ADR-007 — App factory + service layer (v0.2.0)
- **Contexto**: v0.1.0 tinha engine/settings em import-time, tornando
  testes frageis (hack de env antes do import) e acoplando tudo.
- **Decisao**: `create_app(settings, db_engine)`; estado em `app.state`;
  regras de negocio em `*/service.py`; rotas finas.
- **Consequencias**: testes constroem apps isoladas com engine em memoria
  injetada; nenhum singleton de modulo.

### ADR-008 — Envelope de erros unico (v0.2.0)
- **Contexto**: respostas de erro inconsistentes (`{"detail": ...}` solto).
- **Decisao**: `AppError` + handlers -> `{"error": {code, message,
  details}}` em JSON para API e pagina HTML minima para rotas web.
- **Consequencias**: contrato de erro estavel para clients; codigos
  testaveis (`tenant_not_found`, `authentication_failed`...).

### ADR-009 — Tenant por middleware ASGI puro + ContextVar (v0.2.0)
- **Contexto**: BaseHTTPMiddleware quebra propagacao de contextvars e
  adiciona overhead; futuros jobs/mixins de ORM precisam do tenant sem
  Request.
- **Decisao**: middleware ASGI puro que seta `request.state.organization`
  e a ContextVar `current_organization`.
- **Consequencias**: ContextVar disponivel para services/jobs; custo de 1
  query por request (cacheavel no futuro).

### ADR-010 — Alembic desde o dia zero (v0.2.0)
- **Contexto**: v0.1.0 criava tabelas via `create_all` (sem versionamento)
  e a pasta alembic/ era vazia.
- **Decisao**: schema so muda via migration; `create_all` apenas em
  testes; `./start` roda `alembic upgrade head` antes de subir.
- **Consequencias**: deploy em VPS = pull + migrate; rollback de schema
  possivel (downgrade testado).

### ADR-011 — Assets frontend vendored, NAO CDN (v0.2.0)
- **Contexto**: CDN quebra o requisito self-contained do modelo VPS
  (ADR-004) e vaza versao/origem.
- **Decisao**: HTMX/Alpine fixados em `app/web/static/js/vendor/`; CSP
  `script-src 'self'` (com `unsafe-eval` enquanto Alpine exigir).
- **Consequencias**: app funciona offline; atualizacao de libs e
  deliberada (download + commit).

### ADR-012 — Validacao nos schemas, NAO nos table models (v0.2.0)
- **Contexto**: SQLModel `table=True` nao executa validacao pydantic —
  `regex=`/`min_length=` em table models sao decorativos (descoberto na
  reescrita).
- **Decisao**: validacao de entrada vive nos schemas de API; banco garante
  integridade via constraints (unique, FK, NOT NULL).
- **Consequencias**: fronteira clara: schemas validam, models persistem,
  banco reforca.

---

*"Arquitetura e a arte de tomar decisoes faceis de reverter."*
