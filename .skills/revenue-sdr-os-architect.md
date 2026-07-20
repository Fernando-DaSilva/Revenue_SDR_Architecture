---
name: revenue-sdr-os-architect
description: |
  Carregue esta skill SEMPRE que for trabalhar no projeto Revenue SDR OS.
  Fornece contexto fundamental sobre o que e' o produto, arquitetura,
  principios inegociaveis, e onde encontrar skills/prompts especificos.
version: 1.0.0
author: Hermes (arquiteto)
license: Proprietary
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
metadata:
  hermes:
    tags: [revenue-sdr-os, multi-tenant, fastapi, htmx, white-label]
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
+----------+---------------------+--------------------------------+
| Camada   | Tecnologia          | Por que                         |
+----------+---------------------+--------------------------------+
| Frontend | HTMX + Alpine.js    | Hypermedia-driven, server-rendered |
|          | + CSS com tokens    | Cada tenant injeta seu proprio CSS |
| Backend  | FastAPI async       | SSE nativo, async I/O            |
| ORM      | SQLModel            | Pydantic + SQLAlchemy, tipagem fullstack |
| Banco    | SQLite (WAL)        | Zero infra ate dezenas de milhares de leads |
| Real-time| SSE (NÃO WebSocket) | Unidirecional server→client, mais simples |
| Fila     | ARQ + Redis         | Async, leve, in-process          |
| Reverse  | Caddy               | Auto-SSL via Let's Encrypt      |
+----------+---------------------+--------------------------------+
```

**NAO USE** (mesmo que alguem sugira):
- React / Next.js / Vue (frontend)
- Postgres (no MVP — SQLite resolve)
- WebSocket (use SSE)
- MongoDB / NoSQL
- Docker Swarm / Kubernetes (no MVP — unica VPS)

---

## Principios inegociaveis (leia antes de mudar qualquer coisa)

### 1. Multi-tenant e' o CORACAO do produto

```
Toda tabela de dominio TEM organization_id (FK).
Toda query de dominio FILTRA por organization_id.
NUNCA confiar em dados que vem do request sem validar tenant.
```

**Defense in depth**:
- Layer 1: FK constraint + uniques compostas no banco
- Layer 2: middleware ASGI resolve tenant + ContextVar `current_organization`
- Layer 3: services filtram TODA query por organization_id (mixin de ORM
  automatico: evolucao futura sobre a ContextVar)
- Layer 4: claim `org` do JWT precisa bater com o tenant do request
- Layer 5: testes de isolamento cross-tenant (obrigatorios por feature)
- Layer 6: code review verifica manualmente

### 2. White-label via CSS variables

```
Tenant define 5-10 cores no banco.
Backend injeta como :root CSS variables no <head>.
Toda UI usa var(--color-primary), var(--color-text), etc.
Trocar tenant = trocar CSS, zero JS.
```

### 3. API-first interno

```
TODA funcionalidade que frontend usa TEM endpoint REST documentado.
Mesmo HTML routes sao "API + template" internamente.
Toda rota de API comeca com /api/v1/.
```

### 4. Toda mensagem importante vira evento append-only

```
Tabela events: log append-only de TUDO que importa.
Eventos: score_changed, stage_changed, cadence_step_advanced,
         playbook_applied, emotion_detected, abandoned_detected, etc.
Isso permite audit log, analytics, e replay de conversa.
```

### 5. IA e' ferramenta, nao oraculo

```
IA sugere, humano decide.
Score e' exibido ao vendedor, nao usado pra acao automatica irreversivel.
Coach de vendedor usa IA pra ANALISAR humano, nao pra substituir.
Modo Closer e' gatilho pra mudanca de persona, nao pra acao sem review.
```

---

## Modelo de dados (o agregado raiz e' conversation, NAO lead)

```
platforms (singleton)
  +-- brands (White Label Partners)
       +-- organizations (Empresas)
            +-- units (Filiais)
                 +-- teams
                      +-- users

(conversation e' o agregado raiz, lead e' apenas uma pessoa)
conversations  →  o relacionamento em si
leads          →  pessoa fisica
messages       →  cada mensagem
events         →  log append-only

(playbooks verticais por Organization)
playbooks      →  scripts, objecoes, tom, cadencia
ai_agents      →  configuracao do agente IA

(calendar)
calendar_events →  eventos sincronizados com Google Calendar

(coaching pos-conversa)
conversation_reports →  analise IA pos-conversa
```

**Convencoes de IDs**:
- Todos os IDs sao strings prefixed: `org_xxx`, `user_xxx`, `lead_xxx`, `conv_xxx`, `msg_xxx`, `evt_xxx`
- 12 chars randomicos hex apos o prefix (suficiente para escala)
- IDs sao deterministicamente hasheaveis pra comparacao rapida

---

## Estrutura de pastas do codigo (repo ~/AGENCIA/SDR/, v0.2.0)

```
app/
+-- main.py                 # create_app(settings, db_engine) — app factory
+-- core/                   # config, security (Argon2id/PyJWT), errors,
|                           # pagination, middleware (security headers), logging
+-- db/                     # engine factory, session dep, base/mixins
|                           #   (TenantMixin, TimestampMixin, utc_now, prefixed_id)
+-- tenancy/                # middleware ASGI puro + ContextVar de tenant
+-- organizations/          # models.py, schemas.py, service.py, api.py
+-- users/                  # models.py, schemas.py, service.py, api.py
+-- auth/                   # service.py, dependencies.py, schemas.py, api.py
+-- themes/                 # service.py (CSS variables + branding)
+-- health/                 # api.py (liveness/readiness)
+-- web/                    # templating.py (Jinja), pages/, templates/, static/
                            #   static/js/vendor/ = HTMX + Alpine vendored

alembic/                    # env.py + versions/ (schema versionado)
scripts/seed.py             # python -m scripts.seed (2 tenants demo)
tests/                      # pytest isolado — app + SQLite em memoria por teste
archive/sprint-1/           # codigo v0.1.0 (referencia historica, NAO usar)
```

**Padrao por dominio**: cada area de negocio e um pacote com
`models.py` (tabelas) + `schemas.py` (validacao de entrada) +
`service.py` (regras + queries filtradas por tenant) + `api.py` (rotas
JSON finas). Paginas HTML ficam em `app/web/pages/`.

---

## Como o sistema funciona end-to-end (lead manda msg)

```
1. Lead manda msg WhatsApp
   |
2. Z-API webhook → POST /webhooks/zapi/incoming
   |
3. FastAPI identifica lead (Lead Brain)
   |
4. Cria/atualiza conversation com mode="ai"
   |
5. Enfileira job: process_incoming_message (ARQ)
   |
6. Worker pega job:
   a. Carrega contexto (lead.memory, conversation.history, playbook)
   b. Chama AI Sales Brain com prompt rico
   c. IA gera resposta + sugere acoes
   d. IA chama tools (agendar_reuniao, mudar_estagio, etc)
   e. Salva resposta
   f. Envia via Z-API
   g. Emite SSE event: conversation.message_added
   h. Atualiza opportunity_score
   i. Detecta emotional_state
   j. Atualiza Deal Health Score
   |
7. Frontend (via SSE) recebe eventos:
   - Nova mensagem aparece
   - Transcricao atualiza (se audio)
   - Grafico DHS anima
   - Sugestoes de objecao aparecem
   - Notificacao: "Lead respondeu em 12s"
```

---

## Skills especificas (carregar conforme tarefa)

```
+---------------------------+--------------------------------+
| Tarefa                    | Skill a carregar               |
+---------------------------+--------------------------------+
| Criar API endpoint        | .skills/fastapi-multi-tenant.md|
| Criar pagina HTMX         | .skills/htmx-alpine-component.md|
| Criar/criar model         | .skills/sqlmodel-migration.md   |
| Criar migration Alembic   | .skills/sqlmodel-migration.md   |
| Criar teste               | .skills/pytest-tenant-isolation.md|
| Integrar WhatsApp         | .skills/whatsapp-zapi-integration.md|
| Implementar SSE           | .skills/sse-realtime-pattern.md |
| Adicionar Prometheus/Graf| .skills/observability-stack.md  |
+---------------------------+--------------------------------+
```

---

## Prompts (copy-paste em prompts/)

```
+---------------------------+--------------------------------+
| Tarefa                    | Prompt                          |
+---------------------------+--------------------------------+
| Criar endpoint REST       | prompts/01-create-api-endpoint.md|
| Criar pagina HTMX         | prompts/02-create-htmx-page.md   |
| Criar model novo          | prompts/03-create-model.md       |
| Criar migration Alembic   | prompts/04-create-migration.md   |
| Criar suite de testes     | prompts/05-create-test.md        |
| Criar job de cadencia     | prompts/06-create-cadence-job.md |
| Deploy VPS via API        | prompts/07-deploy-vps.md         |
| Adicionar WhatsApp        | prompts/08-add-whatsapp-channel.md|
| Integrar Google Calendar  | prompts/09-add-google-calendar.md|
+---------------------------+--------------------------------+
```

---

## ONDE o codigo vive

**Repo de codigo**: `~/AGENCIA/SDR/` (ou seu clone)
**URL GitHub**: https://github.com/Fernando-DaSilva/Revenue_SDR_OS

**Comandos uteis**:
```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate

./start          # setup completo: .env, migrations, seed se vazio, uvicorn --reload
pytest           # testes (banco em memoria — NUNCA toca o banco de dev)
ruff check app/ tests/ scripts/ alembic/
alembic upgrade head
```

**Credenciais seed**:
- Clinica Bela (rosa #EC4899): `admin@clinica-bela.com` / `senha123`
- Imob Center (verde #10B981): `admin@imob-center.com` / `senha123`

---

## CHECKLIST antes de comitar codigo

```
[ ] Codigo compila sem erro (python -c "import app.main")
[ ] Testes passam (pytest) — suite completa
[ ] Testes de isolamento cross-tenant da feature passam
[ ] ruff check + ruff format --check limpos
[ ] Migration criada e testada (alembic upgrade head && alembic downgrade -1 && alembic upgrade head)
[ ] OpenAPI spec regenerada e consistente (/openapi.json)
[ ] Sem secrets hardcoded (use settings from .env)
[ ] Erros via AppError (envelope), NAO HTTPException solta
[ ] Docstrings PT-BR sem acentos + type hints em funcoes publicas
[ ] Commit message segue Conventional Commits (PT-BR)
```

---

## Quando voce (agente externo) tiver duvida

1. Releia esta skill
2. Verifique se ha skill especifica (lista acima)
3. Verifique o prompt correspondente
4. Verifique ADRs em `decisions/`
5. Verifique FOUNDATION.md
6. Se AINDA nao resolveu: pergunte ao usuario (Fernando) — NAO invente decisao

---

*"Nunca mais perca um lead por falta de acompanhamento."*