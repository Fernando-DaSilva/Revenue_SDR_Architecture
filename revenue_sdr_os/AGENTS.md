# AGENTS.md — Revenue SDR OS

Manual operacional do projeto para agentes de codificacao. Leia antes de
qualquer alteracao. Mantenha este arquivo atualizado quando mudar
arquitetura, comandos ou convencoes.

---

## 1. O produto

**Sistema Operacional de Vendas orientado a conversas** (nao e CRM, nao e
disparador de mensagens). A entidade raiz e o *Relacionamento (Conversa)*.
Promessa: *"Nunca mais perca um lead por falta de acompanhamento."*

- Visao de produto e os 8 "Brains": [docs/historico/IDEA.md](docs/historico/IDEA.md)
- Modelo white-label: [docs/historico/IDEA_01_SDR_WhiteLabel.md](docs/historico/IDEA_01_SDR_WhiteLabel.md)
- Deploy alvo (futuro): uma VPS por cliente + Platform Console (MyraOS).
  Por isso o app e **self-contained** (assets vendored, SQLite, sem CDNs).

## 2. Stack (fixa — nao trocar sem decisao explicita)

- Python **3.12+**, FastAPI, SQLModel sobre SQLite (WAL), Alembic
- Auth: **PyJWT** (HS256) + **pwdlib/Argon2id**. NUNCA python-jose/passlib
  (abandonados, CVEs)
- Frontend: Jinja2 + HTMX + Alpine.js (**vendored** em
  `app/web/static/js/vendor/`) + CSS puro com variables por tenant
- Qualidade: ruff (lint+format), pytest, GitHub Actions

## 3. Arquitetura (invariantes — nao violar)

1. **App factory**: `app/main.py::create_app(settings, db_engine)`. Proibido
   singletons de modulo (engine/settings em import-time). Tudo vive em
   `app.state`.
2. **Camadas**: rota fina -> `*/service.py` (regras + queries) -> model.
   API JSON em `*/api.py`; paginas HTML em `app/web/pages/`.
3. **Multi-tenancy**:
   - Resolucao no middleware ASGI `app/tenancy/middleware.py` (custom_domain/
     subdominio -> header `X-Tenant-Slug` -> query param (so dev) -> default).
   - Tenant disponivel em `request.state.organization` e na ContextVar
     `app.tenancy.context.current_organization`.
   - Todo model de dominio herda `TenantMixin` (`organization_id`
     obrigatorio) e **toda query filtra por organization_id**.
   - Recurso de outro tenant = **404 generico** (nunca vazar existencia).
   - O claim `org` do JWT precisa bater com o tenant do request.
4. **Auth dupla**: cookie HttpOnly (precedencia) + `Authorization: Bearer`.
   Login em `POST /api/v1/auth/login` retorna token E seta cookie.
5. **Erros**: envelope `{"error": {code, message, details}}` via
   `app/core/errors.py` (AppError + subclasses). Nao usar HTTPException solta.
6. **Validacao de entrada vive nos schemas pydantic** (API), NUNCA nos
   table models — SQLModel `table=True` nao executa validacao. Ao banco
   cabem constraints (unique, FK, NOT NULL).
7. **Schema versionado com Alembic**: dev/prod sobem via
   `alembic upgrade head`. `SQLModel.metadata.create_all` existe SOMENTE
   em testes.
8. **Templates**: render via `app/web/templating.py::render()` — injeta
   tema/branding automaticamente. Nao instanciar Jinja2 Environment fora
   da factory.

## 4. Convencoes de codigo

- Type hints em tudo; docstrings em modulos/funcoes publicas
- Comentarios e docstrings em **PT-BR sem acentos** (evitar mojibake);
  identificadores em ingles
- IDs: strings prefixadas (`org_`, `user_`, futuro `lead_`) via
  `db.base.prefixed_id`
- Timestamps: `datetime.now(UTC)` timezone-aware (`db.base.utc_now`)
- Commits: **Conventional Commits** em PT-BR (ex: `feat: adiciona Lead
  Brain (Sprint 2)`)
- Sem emojis em codigo/docs de codigo

## 5. Comandos

```bash
# Setup
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
python -m scripts.seed          # 2 tenants demo (senha: senha123)

# Run
./start                       # setup completo: .env, migrations, seed se vazio, uvicorn --reload
# hosts: 127.0.0.1 clinica-bela.localhost / imob-center.localhost

# Qualidade (rodar ANTES de commitar — tudo precisa passar)
pytest                          # 57+ testes, banco em memoria
ruff check app/ tests/ scripts/ alembic/
ruff format --check app/ tests/ scripts/   # ou: ruff format ...

# Migrations
alembic revision --autogenerate -m "descricao"
alembic upgrade head
```

## 6. Testes (regras duras)

- **NUNCA** apontar testes para `revenue_sdr_os.db` (banco de dev).
  Fixtures em `tests/conftest.py`: app isolada + SQLite em memoria
  (StaticPool) por teste.
- Auth nos testes: Bearer (limpe `client.cookies` para provar que o
  Bearer autentica) e cookie, ambos cobertos.
- Toda feature de dominio nova exige teste de **isolamento cross-tenant**.

## 7. Estado atual e roadmap

- **v0.2.0 (baseline)**: fundacao reescrita — multi-tenancy, auth,
  white-label, health, seed, CI. Sprint 1 original arquivada em
  `archive/sprint-1/` (NAO usar, referencia historica).
- **Proximo**: Sprint 2 — Lead Brain + Memory Brain (CRUD de leads,
  merge de identidades cross-channel, timeline de eventos).
- Depois: Conversas/Opportunity (S3), AI Sales + Z-API (S4), handoff
  IA<->Humano (S5), Omnichannel (S8), VPS orchestrator (S9).

## 8. Hierarquia de tenants (visao)

Platform (MyraOS) -> Brands -> Organizations -> Units -> Teams -> Users.
Implementado hoje: **Organization -> User** (2 niveis). Evoluir sem
quebrar as invariantes da secao 3.

## 9. Ambiente local

- `.env` do desenvolvedor nao e versionado; chaves novas entram primeiro
  no `.env.example`
- Banco de dev: `revenue_sdr_os.db` (gitignored), recriavel via
  `alembic upgrade head && python -m scripts.seed`
- Porta 8000: verificar processos antigos (`lsof -iTCP:8000 -sTCP:LISTEN`)
  antes de smoke tests
