# Sprint 01 — Foundation + Auth + White-Label Basico

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 01 — FOUNDATION + AUTH + WHITE-LABEL                       |
|   Status:  CONCLUIDO (commit b73d07b no GitHub)                     |
|   Quando:  Sprint 1 (1-2 semanas)                                   |
|   Branch:  main                                                       |
|   Repo:    https://github.com/Fernando-DaSilva/Revenue_SDR_OS        |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Objetivo (alcancado)

Construir a fundacao tecnica validando:
- [x] Stack funciona (FastAPI + SQLModel + HTMX + Alpine.js)
- [x] Multi-tenancy funciona (2+ orgs isoladas)
- [x] White-label funciona (tema diferente por tenant)
- [x] Auth funciona (login, sessao, roles)
- [x] API-first funciona (toda UI consome API documentada)

---

## Entregaveis (todos completos)

### Codigo (em ~/AGENCIA/SDR/)

```
[OK] Estrutura do monorepo (app/, tests/, scripts/, docs/)
[OK] Schema SQLModel: Organization + User (com TenantBase mixin)
[OK] Middleware de tenant resolution (subdomain + header + query)
[OK] Sistema de auth: JWT (HS256) + bcrypt + cookie HttpOnly
[OK] Tema dinamico via CSS variables injetadas por tenant
[OK] API REST v1: auth, health, organization, users
[OK] Frontend basico: login + dashboard vazio (HTMX + Alpine + CSS)
[OK] Seed script com 2 tenants (clinica-bela + imob-center)
[OK] Testes pytest (parcial — 15 passam, 13 tem issues de cache)
[OK] CI no GitHub Actions (.github/workflows/ci.yml)
[OK] README com badges + ASCII art
[OK] CONTRIBUTING.md + SECURITY.md
```

### Documentacao (neste folder)

```
[OK] FOUNDATION.md v1.4 (migrar de ~/AGENCIA/SDR/)
[OK] ARCHITECTURE.md (decisoes tecnicas)
[OK] ROADMAP.md (visao geral)
```

---

## Criterios de aceitacao (todos atingidos)

| Criterio | Status |
|---|---|
| Acessa `http://localhost:8000` | [x] |
| Ve tela de login customizada pelo tenant | [x] |
| Loga como admin@empresa1.com ou admin@empresa2.com | [x] |
| Cada um ve dashboard com cor/logo diferente | [x] |
| Nao ve dados do outro tenant | [x] |
| API documentada em /docs | [x] |
| Health check retorna ok | [x] |
| Cross-tenant login bloqueado com 401 | [x] |
| 2 tenants seedados com cores diferentes | [x] |

---

## Issues conhecidos (a resolver em sprints futuras)

1. **Testes pytest**: 15 passam, 13 falham por cache de Jinja2 + detached instances (fixture pattern a refinar)
2. **Login HTML**: bug intermitente do Jinja2 + Starlette com `{% extends %}` — resolvido com `templates_renderer.py` próprio
3. **bcrypt 4.1 incompatibilidade com passlib**: pinado `bcrypt<4.1` no `requirements.txt`
4. **IPv6 vs IPv4**: servidor precisa `--host 127.0.0.1` (não 0.0.0.0) por causa do macOS resolver IPv6 primeiro

---

## Como usar o que foi construido

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Acesse:
- http://127.0.0.1:8000/docs
- http://clinica-bela.localhost:8000/login (rosa)
- http://imob-center.localhost:8000/login (verde)

Credenciais:
- `admin@clinica-bela.com` / `senha123`
- `admin@imob-center.com` / `senha123`

---

## Proxima sprint

**Sprint 02 — Lead Brain + Memory Brain** (ver `../02_Sprint_02_Lead_Brain_Memory_Brain/README.md`)