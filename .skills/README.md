# Skills — Indice

> **Todas as skills carregaveis pelos agentes externos.**

## Como usar

Skills sao arquivos markdown em `.skills/` que agentes de IA carregam pra ter contexto tecnico sobre o projeto.

**Workflow**:
1. Abra o agente (Claude Code, Codex, OpenCode, etc)
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

### `.skills/sqlmodel-migration.md`

```
Padroes de SQLModel + Alembic:
  - Tenant model (organization_id FK NOT NULL)
  - ID factory (prefixed: user_xxx, lead_xxx)
  - JSON fields (tags, custom_fields)
  - Soft delete (status='deletado')
  - Alembic setup + autogenerate
  - Migrations reversiveis (upgrade + downgrade)
  - Indices (quando criar)
```

**Quando carregar**: criar/alterar model, criar migration.

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
  - Webhook handler (validar instance_id, async processing)
  - Factory pattern (migracao futura pra Twilio)
  - Multi-tenant (instance_id por Organization)
  - Anti-patterns (chamada sincrona bloqueante, hardcoded instance)
```

**Quando carregar**: implementar webhook WhatsApp, envio de mensagem, Z-API.

### `.skills/sse-realtime-pattern.md`

```
Server-Sent Events (real-time):
  - SSE endpoint com EventSourceResponse (sse-starlette)
  - Broker in-memory (publish/subscribe)
  - Subscribe + unsubscribe em try/finally
  - Keep-alive ping (evita timeout de proxy)
  - Auth obrigatoria + tenant isolation
  - Cliente JS com auto-reconnect
  - Migracao futura pra Redis Pub/Sub
```

**Quando carregar**: implementar notificacoes live, transcricao, grafico DHS, qualquer real-time.

### `.skills/observability-stack.md`

```
Observabilidade (Prometheus + Grafana + Loki):
  - Metricas Prometheus (latencia, count, errors)
  - Middleware FastAPI instrumenta todos os requests
  - Metricas de negocio (leads, conversations, sales)
  - Metricas de IA (tokens, custo, latencia)
  - Logger estruturado em JSON
  - Grafana dashboards provisionados
  - Alertas Prometheus (VPS down, disco cheio, SSL expirando)
  - Pushgateway (VPS clientes empurram metricas)
```

**Quando carregar**: adicionar Prometheus, Grafana, logs, alertas.

### `.skills/google-auth-integration.md`

```
Integração de Google Sign-up e Login (OAuth2):
  - Fluxo multi-tenant e isolamento por Host
  - Validação de ID Token no backend (Google JWKS ou library)
  - Auto-vinculação com conta de e-mail nativa
  - Estratégia de testes mockados
  - Anti-padrões comuns
```

**Quando carregar**: criar/modificar endpoints de autenticação social, integrar Google One Tap / OAuth2 no login ou cadastro.

## Combinacoes comuns

```
Criar API endpoint novo:
  + revenue-sdr-os-architect
  + fastapi-multi-tenant
  + pytest-tenant-isolation

Criar model + migration:
  + revenue-sdr-os-architect
  + sqlmodel-migration

Criar UI HTMX:
  + revenue-sdr-os-architect
  + htmx-alpine-component

Integrar Google Auth:
  + revenue-sdr-os-architect
  + fastapi-multi-tenant
  + google-auth-integration
  + pytest-tenant-isolation

Integrar WhatsApp:
  + revenue-sdr-os-architect
  + fastapi-multi-tenant
  + whatsapp-zapi-integration
  + pytest-tenant-isolation

Real-time updates:
  + revenue-sdr-os-architect
  + sse-realtime-pattern
  + observability-stack
```


## Adicionar nova skill

Quando uma tecnologia nova precisar de skill (ex: Redis, Kafka, OAuth2):

1. Crie arquivo em `.skills/<nome-descritivo>.md`
2. Use o formato:
   - Frontmatter YAML (name, description, version, platforms)
   - Principio basico
   - Estrutura/codigo exemplo
   - Padroes e convencoes
   - Anti-patterns
   - Checklist
3. Adicione entrada neste README

---

*"Skill e' o cerebro carregavel do agente."*