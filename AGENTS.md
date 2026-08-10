# AGENTS.md — Manual para Agentes de Codificacao

> **Voce e um agente de IA construindo o Revenue SDR OS.**
> Este manual diz EXATAMENTE como trabalhar. As regras duras de codigo
> vivem no AGENTS.md do repo de codigo (`~/AGENCIA/SDR/AGENTS.md`) — leia
> os dois.

---

## TL;DR

```
1. Leia FOUNDATION.md (visao) + ARCHITECTURE.md (decisoes vigentes)
2. Carregue .skills/revenue-sdr-os-architect.md + .skills/whatsapp-sdr-prototype-architect.md + skills da tarefa
3. Leia o spec da sprint em Sprints/XX_*/ (+ prompts por tarefa)
4. Code no repo ~/AGENCIA/SDR/ e ~/AGENCIA/02_ZAP_Prototype/ seguindo os invariantes da v0.2.0 e ADR-017
5. Valide com o checklist (pytest + ruff + alembic round-trip)
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

./start        # valida env, aplica migrations, roda seed se vazio, sobe
# ou manualmente:
# alembic upgrade head && python -m scripts.seed && uvicorn app.main:app --reload

pytest         # 57+ testes devem passar
```

Tenants demo: `admin@clinica-bela.com` / `admin@imob-center.com` (senha123),
em `http://<slug>.localhost:8000` (configurar /etc/hosts).

---

## Arquitetura vigente (v0.2.0) — onde as coisas moram

```
app/
+-- main.py                  # create_app(settings, db_engine) — app factory
+-- core/                    # config, security (Argon2id/PyJWT), errors,
|                            # pagination, middleware (security headers), logging
+-- db/                      # engine factory, session dep, mixins
+-- tenancy/                 # middleware ASGI + ContextVar de tenant
+-- organizations/           # models, schemas, service, api
+-- users/                   # models, schemas, service, api
+-- auth/                    # service, dependencies, schemas, api
+-- themes/                  # CSS variables + branding
+-- health/                  # liveness/readiness
+-- web/                     # templating Jinja2, pages/, templates/, static/
alembic/                     # env.py + versions/ (schema versionado)
tests/                       # pytest isolado (SQLite em memoria por teste)
```

### Invariantes que NUNCA se quebram

1. **App factory** — sem singletons de modulo; estado em `app.state`.
2. **Camadas** — rota fina -> `*/service.py` -> model. Query NUNCA na rota.
3. **Tenancy Zero-Trust** — toda query filtra `organization_id`; cross-tenant = 404
   generico; claim `org` do JWT bate com o tenant do request (ADR-018).
4. **Erros** — `AppError` + envelope `{"error": {code, message, details}}`.
   NAO usar HTTPException solta em codigo novo.
5. **Validacao nos schemas** — table models SQLModel NAO validam entrada.
6. **Schema via Alembic** — `create_all` so em testes; migrations obrigatoriamente testadas via round-trip.
7. **Auth dupla** — cookie (precedencia) + Bearer; senhas via Argon2id (`pwdlib`), JWT HS256 com `jti` (ADR-006 / ADR-018).
8. **Validacao de entrada de tenant** — `organization_id` SEMPRE do
   contexto ContextVar, NUNCA do payload.
9. **SLAs de Performance (P95)** — Turso local < 10ms, Core API < 50ms, SSE < 100ms, Webhook < 300ms, Whisper < 1.5s, SDR Agent < 1.2s (ADR-019).
10. **Matriz de Testes** — Cobertura geral > 85%, isolamento multi-tenant 100% (ADR-020).
11. **Alinhamento Visual aos Prototipos** — Frontend hypermedia HTMX/Alpine/DaisyUI deve espelhar 100% o design system dos protótipos `01_SDR_Prototype` e `02_ZAP_Prototype`.

---

## Workflow padrao por tarefa

### A. Entender
1. Releia o brief + spec da sprint (`Sprints/XX_*/README.md`)
2. Busque nos protótipos (`01_SDR_Prototype` e `02_ZAP_Prototype`) pelos componentes visuais correspondentes
3. Confirme com o usuario SE houver ambiguidade (nao invente decisao)

### B. Planejar
1. Models/migrations novos? 2. Endpoints? 3. UI Jinja2/HTMX/Alpine? 4. Testes de isolamento & unitários (>85%)?

### C. Implementar em camadas
1. Model (no pacote de dominio) -> `alembic revision --autogenerate`
2. Service (regras + queries filtradas por tenant)
3. Schemas (validacao de entrada pydantic)
4. API (`*/api.py`) e/ou pagina (`app/web/pages/`)
5. Testes (CRUD + isolamento cross-tenant em `tests/`)

### D. Validar ANTES de commitar (tudo precisa passar)

```bash
pytest                                            # suite completa (>85% cobertura)
ruff check app/ tests/ scripts/ alembic/          # lint
ruff format --check app/ tests/ scripts/          # formatacao
alembic upgrade head && alembic downgrade -1 && alembic upgrade head # round-trip de migration
./start &                                         # sobe e responde?
curl http://127.0.0.1:8000/api/v1/health/
curl http://127.0.0.1:8000/openapi.json | python -m json.tool > /dev/null
```

### E. Commit (Conventional Commits PT-BR)

`feat:` nova feature | `fix:` bug | `docs:` documentacao | `refactor:` |
`test:` testes | `chore:` manutencao. Branch semantica quando a tarefa for
grande (`feature/sprint-02-lead-brain`).

---

## Erros comuns (NUNCA faca)

```
[X] Query sem filtro de tenant        -> SEMPRE .where(org_id == ...)
[X] 403 em cross-tenant               -> use 404 generico
[X] organization_id vindo do payload  -> SEMPRE do contexto ContextVar
[X] HTTPException solta               -> use AppError + subclasses
[X] Validacao no table model          -> valide no schema pydantic
[X] datetime.utcnow()                 -> use db.base.utc_now (UTC aware)
[X] Tabela sem migration              -> alembic revision --autogenerate
[X] Migration sem teste round-trip    -> alembic upgrade/downgrade/upgrade
[X] JSON serializado como string      -> use coluna JSON nativa
[X] Hardcoded cor/asset externo       -> CSS variables + assets vendored
[X] WebSocket                         -> SSE (ADR-005)
[X] print()                           -> logger
[X] SECRET_KEY no codigo              -> settings
[X] ID sem prefixo                    -> prefixed_id("lead") etc
[X] Commit sem pytest+ruff verdes     -> valide antes
[X] Teste apontando pro banco de dev  -> fixtures em memoria (conftest)
```

## CHECKLIST final de entrega

```
[ ] pytest 100% verde (>85% cobertura na suite toda)
[ ] Testes de isolamento cross-tenant da feature passando (100% isolamento)
[ ] ruff check + ruff format --check limpos
[ ] alembic upgrade + downgrade + upgrade OK (se criou migration)
[ ] SLAs de latência P95 dentro dos orçamentos (ADR-019)
[ ] Fidelidade aos protótipos 01_SDR_Prototype e 02_ZAP_Prototype validada
[ ] /docs mostra os endpoints novos corretamente
[ ] Sem secrets/prints; docstrings PT-BR sem acentos; type hints
[ ] Smoke test manual (browser ou curl) com 2 tenants
[ ] Commit em Conventional Commits PT-BR
[ ] Resposta ao usuario: o que foi feito, arquivos, como testar,
    limitacoes conhecidas, proximos passos
```

## Quando pedir ajuda

Antes: releu skills? spec da sprint? ARCHITECTURE.md (ADRs)? codigo
similar? Se ainda sim, faca pergunta ESPECIFICA com opcoes e trade-offs —
nunca "nao sei, me ajuda".

---

*"Nunca mais perca um lead por falta de acompanhamento."*
