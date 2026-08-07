# Revenue SDR OS

> **White-label multi-tenant sales platform with AI SDR**
> *Nunca mais perca um lead por falta de acompanhamento.*

[![CI](https://github.com/Fernando-DaSilva/Revenue_SDR_OS/workflows/CI/badge.svg)](https://github.com/Fernando-DaSilva/Revenue_SDR_OS/actions)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

```
+----------------------------------------------------------------------+
|   REVENUE SDR OS — v0.2.0                                            |
|   Fundacao reescrita: app factory, service layer, Alembic,           |
|   Argon2id + PyJWT, erros consistentes, testes isolados (57)         |
|   Status: fundacao validada end-to-end                               |
+----------------------------------------------------------------------+
```

---

## O produto

Nao e um CRM (cadastros) nem um disparador de Zap (mensagens).
E um **Sistema Operacional de Vendas orientado a conversas**: a entidade
raiz e o *Relacionamento*, que evolui no tempo, atravessa canais e e
orquestrado por IA. Visao completa em [docs/historico/IDEA.md](docs/historico/IDEA.md).

---

## Quickstart (5 minutos)

### Pre-requisitos

- Python 3.12+
- pip

### Setup

```bash
git clone https://github.com/Fernando-DaSilva/Revenue_SDR_OS.git
cd Revenue_SDR_OS

python3.12 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env

# Schema do banco (obrigatorio antes do seed)
alembic upgrade head

# 2 tenants de demonstracao
python -m scripts.seed
```

### Subir

```bash
./start   # valida .venv/.env, aplica migrations, roda seed se vazio, sobe com --reload
```

### Hosts locais (multi-tenant por subdominio)

```bash
sudo tee -a /etc/hosts << EOF
127.0.0.1   clinica-bela.localhost
127.0.0.1   imob-center.localhost
EOF
```

### Acessar

| Tenant | URL | Email | Senha |
|---|---|---|---|
| Clinica Bela (rosa) | http://clinica-bela.localhost:8000 | admin@clinica-bela.com | senha123 |
| Imob Center (verde) | http://imob-center.localhost:8000 | admin@imob-center.com | senha123 |
| API Docs | http://localhost:8000/docs | — | — |

---

## Arquitetura

### Decisoes de engenharia

| Decisao | Por que |
|---|---|
| **App factory** (`create_app`) | Zero singletons de modulo; testes constroem apps isoladas com engine injetada |
| **Service layer** | Rotas finas; regras de acesso a dados em `*/service.py` |
| **Multi-tenancy por middleware ASGI puro** | Resolve subdominio, custom_domain, header `X-Tenant-Slug` ou query param (dev); injeta `request.state.organization` + **ContextVar** de tenant |
| **Defesa em profundidade** | O `org` do JWT precisa bater com o tenant resolvido — token de um tenant nao opera em outro |
| **Alembic desde o dia zero** | `create_all` so existe em testes; dev/prod sobem schema via `alembic upgrade head` |
| **Argon2id (pwdlib) + PyJWT** | Substituem passlib/python-jose (bibliotecas sem manutencao e com CVEs) |
| **Erros consistentes** | Envelope `{"error": {code, message, details}}` em toda a API |
| **Frontend hypermedia** | HTMX + Alpine **vendored localmente** (self-contained, pronto para VPS on-premise); white-label por CSS variables injetadas no `<head>` |
| **SQLite WAL** | Suficiente ate dezenas de milhares de leads; migracao para Postgres e troca de URL |

### Resolucao de tenant (precedencia)

1. `custom_domain` exato (Host) ou subdominio -> slug
2. Header `X-Tenant-Slug`
3. Query param `?tenant=` (somente `APP_ENV=development`)
4. `DEFAULT_TENANT_SLUG` (se configurado; vazio em producao = 404)

### Estrutura

```
app/
+-- main.py                  # create_app() — wiring completo
+-- core/                    # config, logging, security, errors, pagination, middleware
+-- db/                      # engine factory, session dependency, mixins (Tenant/Timestamp)
+-- tenancy/                 # middleware ASGI + ContextVar de tenant
+-- organizations/           # model, schemas, service, API
+-- users/                   # model, schemas, service, API
+-- auth/                    # service, dependencies, schemas, API (cookie + Bearer)
+-- themes/                  # CSS variables + branding por tenant
+-- health/                  # liveness/readiness
+-- web/                     # templating Jinja2, paginas HTML, templates, static
alembic/                     # env.py + versions/ (schema versionado)
scripts/seed.py              # tenants demo (python -m scripts.seed)
tests/                       # 57 testes isolados (SQLite em memoria)
archive/sprint-1/            # codigo legado v0.1.0 (referencia historica, NAO USAR)
```

---

## API v1

```
# Auth
POST /api/v1/auth/login        Login JSON -> Bearer token (+ cookie de sessao)
POST /api/v1/auth/logout       Logout (limpa cookie)
GET  /api/v1/auth/me           Usuario autenticado (cookie OU Bearer)

# Tenant
GET  /api/v1/organization      Dados publicos do tenant resolvido

# Users (autenticado, escopo do tenant)
GET  /api/v1/users             Lista paginada (?offset=&limit=)
GET  /api/v1/users/{id}        Por ID (404 generico fora do tenant)

# Health
GET  /api/v1/health/           Liveness
GET  /api/v1/health/ready      Readiness (verifica DB)
```

Autenticacao dupla: **cookie HttpOnly** (browser) e **Authorization: Bearer** (API).
Erros seguem o envelope `{"error": {"code", "message", "details"}}`.

---

## Testes e qualidade

```bash
pytest                                    # 57 testes, SQLite em memoria
pytest --cov=app --cov-report=term-missing
ruff check app/ tests/ scripts/           # lint (bandit, bugbear, isort...)
ruff format --check app/ tests/ scripts/  # formatacao
```

Cada teste sobe uma app nova com banco em memoria — **nenhum teste toca
no banco de desenvolvimento**.

## Migrations

```bash
alembic upgrade head                      # aplica
alembic revision --autogenerate -m "..."  # gera nova (models -> migration)
alembic downgrade -1                      # reverte
```

---

## Roadmap

```
Sprint 1 [OK] Fundacao + Auth + White-Label (reescrita v0.2.0)
Sprint 2 [ ]  Lead Brain + Memory Brain (CRUD + merge + timeline)
Sprint 3 [ ]  Conversations + Opportunity Brain (score + cadencia)
Sprint 4 [ ]  AI Sales Brain + integracao Z-API Zap
Sprint 5 [ ]  UI monitoramento + handoff IA<->Humano + Google Calendar
Sprint 6+ [ ] Transcricao, DHS, relatorios pos-conversa
Sprint 8+ [ ] Omnichannel completo (IG, email, voice)
Sprint 9+ [ ] VPS dedicada por cliente + update orchestrator (MyraOS Console)
```

---

## Contribuindo e Seguranca

- [CONTRIBUTING.md](CONTRIBUTING.md) — Conventional Commits, PEP 8 + type hints
- [SECURITY.md](SECURITY.md) — reporte de vulnerabilidades

## Licenca

MIT — ver [LICENSE](LICENSE).

---

*"Nunca mais perca um lead por falta de acompanhamento."*
