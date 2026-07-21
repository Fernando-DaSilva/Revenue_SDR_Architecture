# Sprint 01 — Foundation + Auth + White-Label

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 01 — FOUNDATION + AUTH + WHITE-LABEL                       |
|   Status:  CONCLUIDA — reescrita em qualidade profissional          |
|   Versao:  v0.2.0 (baseline, commit 4513a29)                        |
|   Repo:    https://github.com/Fernando-DaSilva/Revenue_SDR_OS        |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Nota historica (2026-07-17)

A v0.1.0 desta sprint validou o stack, mas acumulou problemas estruturais
(auth Bearer inoperante, testes apontando para o banco de dev, deps
abandonadas — python-jose/passlib, Alembic vazio, assets 404). Foi
**arquivada em `archive/sprint-1/`** e reescrita do zero como **v0.2.0**.
Todos os "issues conhecidos" abaixo foram resolvidos na reescrita.

## Objetivo (alcancado)

- [x] Stack funciona (FastAPI + SQLModel + HTMX + Alpine.js vendored)
- [x] Multi-tenancy funciona (isolamento + middleware ASGI + ContextVar)
- [x] White-label funciona (CSS variables por tenant)
- [x] White-label Avançado (v2.1.0) (customização de idiomas pt-BR, es-ES, en-GB, de-DE, lt-LT por usuário/tela e 5 presets de cores)
- [x] Auth funciona (Argon2id + PyJWT; cookie HttpOnly + Bearer)
- [x] API-first funciona (/docs + envelope de erro consistente)

## Entregaveis (v0.2.0 & v2.1.0)

```
[OK] App factory (create_app) + service layer + pacotes de dominio
[OK] Multi-tenancy: custom_domain, subdominio, header, query (dev), default
[OK] JWT com claim org validado contra o tenant do request
[OK] Erros em envelope {"error": {code, message, details}}
[OK] Alembic real (migration inicial + upgrade/downgrade testados)
[OK] Email unico por tenant (uq_users_org_email)
[OK] Security headers + CSP; assets vendored (HTMX/Alpine, sem CDN)
[OK] 57 testes isolados (SQLite em memoria por teste, 94% cobertura)
[OK] ruff (lint+format+bandit) limpo; CI verde no GitHub Actions
[OK] ./start (setup + migrate + seed + serve em 1 comando)
[OK] Seed: clinica-bela (rosa) + imob-center (verde) / senha123
[OK] AGENTS.md no repo de codigo (regras duras)
[OK] Especificação de White-Label Avançado (ADR-013, Skill, Prompt, Templates de Model e UI)
```

## Issues da v0.1.0 — TODOS RESOLVIDOS

| Issue v0.1.0 | Resolucao v0.2.0 |
|---|---|
| Testes 15/28 (cache Jinja2 + fixtures) | 57/57 — novo padrao de fixtures (app factory + engine em memoria injetada) |
| Bearer token inutil (so cookie auth) | Auth dupla real: cookie + Bearer, com org do JWT validada |
| Testes apagavam o banco de dev | SQLite em memoria por teste (StaticPool) |
| passlib + bcrypt<4.1 | pwdlib/Argon2id (sem pin) |
| python-jose (CVEs) | PyJWT |
| Alembic vazio | Migration inicial real; schema so via migration |
| templates_renderer workaround | app/web/templating.py (env por app) |
| Assets JS/logo 404 | Vendored em static/js/vendor/ + logo SVG |
| requirements.txt duplicado | pyproject.toml como fonte unica |

## Criterios de aceitacao (todos atingidos e mantidos)

| Criterio | Status |
|---|---|
| Login white-label por tenant (cor/logo/nome) | [x] |
| 2 tenants isolados (dados + tema) | [x] |
| Cross-tenant login bloqueado (401) | [x] |
| Cross-tenant recurso = 404 generico | [x] |
| Token de um tenant nao opera em outro (401) | [x] |
| API documentada em /docs | [x] |
| Health + readiness OK | [x] |

## Como rodar

```bash
cd ~/AGENCIA/SDR && ./start
# http://clinica-bela.localhost:8000  admin@clinica-bela.com / senha123
# http://imob-center.localhost:8000   admin@imob-center.com / senha123
```

## Proxima sprint

**Sprint 02 — Lead Brain + Memory Brain** (ver `../02_Sprint_02_Lead_Brain_Memory_Brain/README.md`)
