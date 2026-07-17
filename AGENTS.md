# AGENTS.md — Manual para Agentes Externos

> **Voce e' um agente de IA (Claude Code, Codex, OpenCode, etc) construindo o Revenue SDR OS.**
> Este manual te diz EXATAMENTE como trabalhar no projeto.

---

## TL;DR

```
1. Carregue SEMPRE a skill `.skills/revenue-sdr-os-architect.md` PRIMEIRO
2. Carregue skills especificas conforme a tarefa
3. Leia o prompt correspondente em `prompts/`
4. Siga o template em `templates/`
5. Code no repo ~/AGENCIA/SDR/ (clone antes de comecar)
6. Valide com checklist do prompt
7. Commit + push no GitHub
```

---

## Setup inicial (faca isso UMA vez)

### 1. Receber o brief do usuario (Fernando)

Ele vai te dizer qual sprint, qual tarefa, ou qual feature implementar. Exemplo:

> "Implementa o CRUD de leads da Sprint 2"

### 2. Carregar skills (nesta ordem)

```
1. .skills/revenue-sdr-os-architect.md     (SEMPRE primeiro)
2. .skills/fastapi-multi-tenant.md          (se for API)
3. .skills/sqlmodel-migration.md            (se for model/migration)
4. .skills/htmx-alpine-component.md         (se for UI)
5. .skills/pytest-tenant-isolation.md       (se for teste - SEMPRE pra features multi-tenant)
6. .skills/whatsapp-zapi-integration.md     (se for WhatsApp)
7. .skills/sse-realtime-pattern.md          (se for SSE/real-time)
8. .skills/observability-stack.md           (se for metricas/logs)
```

### 3. Ler o prompt

`prompts/0X-<task-name>.md` — copy-paste, nao invente.

### 4. Setup do repo

```bash
# Se ainda nao tem o repo
cd ~
git clone https://github.com/Fernando-DaSilva/Revenue_SDR_OS.git AGENCIA/SDR
cd AGENCIA/SDR

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed.py

# Verificar que funciona
pytest tests/ -v
```

---

## Workflow padrao

### A. Entender a tarefa

1. Releia o brief do usuario
2. Verifique em qual sprint a tarefa se encaixa (`docs/sprints/`)
3. Verifique se ja existe algo similar no codigo (buscar por termos-chave)
4. Confirme com o usuario SE houver ambiguidade

### B. Planejar antes de codar

Antes de escrever codigo, defina:

1. **Que model/schema precisa?** (ex: nova tabela Lead)
2. **Que endpoints precisa?** (ex: GET /leads, POST /leads)
3. **Que UI precisa?** (ex: lista de leads com busca)
4. **Que testes precisa?** (ex: tenant isolation, CRUD basico)
5. **Que migrations precisa?** (ex: alembic revision)

### C. Implementar em camadas

1. **Model + migration primeiro** (SQLModel → Alembic)
2. **API endpoints** (FastAPI routers)
3. **UI** (HTMX + Alpine.js)
4. **Testes** (pytest, foco em tenant isolation)
5. **Documentacao** (docstrings, OpenAPI tags)

### D. Validar antes de comitar

```bash
# Codigo compila
python -c "from app.main import app"

# Testes passam
pytest -v

# Tenant isolation passa (CRITICO)
pytest tests/test_tenant_isolation.py -v

# Lint (se ruff configurado)
ruff check app/

# Migration funciona
alembic upgrade head
alembic downgrade -1
alembic upgrade head

# OpenAPI spec regenera
curl http://127.0.0.1:8000/openapi.json | python -m json.tool > /dev/null

# Servidor sobe
uvicorn app.main:app --reload &
sleep 3
curl http://127.0.0.1:8000/api/v1/health/
```

### E. Commit + push

```bash
git add .
git commit -m "feat: <descricao no conventional commits>"
git push origin <branch>
```

**Formato conventional commits**:
- `feat:` nova feature
- `fix:` bug fix
- `docs:` so documentacao
- `refactor:` mudanca que nao adiciona feature nem corrige bug
- `test:` adiciona ou corrige testes
- `chore:` tasks de manutencao (deps, configs, etc)

---

## Padroes inegociaveis (do projeto)

### 1. Multi-tenant
```
Toda tabela de dominio: organization_id (FK NOT NULL)
Toda query: WHERE organization_id = ?
Cross-tenant access: 404 (NAO 403)
```

### 2. White-label
```
Tenant tem 5-10 cores no banco
CSS variables injetadas no <head>
NUNCA hardcode cor no template
```

### 3. API-first
```
Toda UI consome endpoint REST documentado
Toda rota comeca com /api/v1/
OpenAPI spec auto-gerada pelo FastAPI
```

### 4. Eventos append-only
```
Tabela events: TUDO que importa vira evento
Tipos: score_changed, stage_changed, cadence_step_advanced, ...
Permite audit log, analytics, replay
```

### 5. SSE para real-time (NAO WebSocket)
```
Lead ↔ IA: SSE server→client
Transcricao, sugestoes, grafico DHS: SSE
WebSocket so se vendedor for digitar mensagem pela plataforma (Sprint 6+)
```

---

## ONDE encontrar o que voce precisa

| Voce quer... | Olhe em... |
|---|---|
| Visao geral do produto | `FOUNDATION.md` |
| Decisoes arquiteturais | `decisions/0XX-*.md` |
| Como criar API | `.skills/fastapi-multi-tenant.md` + `prompts/01-create-api-endpoint.md` + `templates/fastapi-route.py` |
| Como criar UI | `.skills/htmx-alpine-component.md` + `prompts/02-create-htmx-page.md` + `templates/htmx-component.html` |
| Como criar model | `.skills/sqlmodel-migration.md` + `prompts/03-create-model.md` + `templates/sqlmodel-tenant-model.py` |
| Como criar migration | `.skills/sqlmodel-migration.md` + `prompts/04-create-migration.md` + `templates/alembic-migration.py` |
| Como criar teste | `.skills/pytest-tenant-isolation.md` + `prompts/05-create-test.md` + `templates/pytest-isolation-test.py` |
| Detalhes da sprint X | `docs/sprints/sprint-XX-*.md` |
| Status atual do projeto | `README.md` (este folder) + `~/AGENCIA/SDR/README.md` |

---

## CHECKLIST final antes de avisar o usuario que terminou

```
[ ] Codigo compila sem warnings
[ ] pytest passa (todos, nao so os novos)
[ ] pytest tests/test_tenant_isolation.py passa
[ ] alembic upgrade + downgrade funciona (se criou migration)
[ ] /docs mostra novos endpoints corretamente
[ ] Nenhum secret hardcoded
[ ] Nenhum print() esquecido (usar logger)
[ ] Codigo segue patterns das skills
[ ] Commit message em conventional commits
[ ] Branch com nome semantico (feature/xxx, fix/xxx)
[ ] PR description explica o que e por que
[ ] Testou manualmente no browser (UI) ou curl (API)
```

---

## Erros comuns (NUNCA faca)

```
[X] Inventar decisao quando tem ADR/spec → PERGUNTE ao usuario
[X] Hardcoded cor (#FF0000) → use CSS variable
[X] Query sem filtro de tenant → SEMPRE .where(organization_id=...)
[X] 403 em cross-tenant → use 404
[X] WebSocket → use SSE (no MVP)
[X] PostgreSQL → use SQLite (no MVP)
[X] React → use HTMX + Alpine.js
[X] print() → use logger
[X] SECRET_KEY no codigo → use settings do .env
[X] Schema Pydantic acoplado no SQLModel → separe
[X] ID sem prefixo → use prefixo (org_, user_, lead_, ...)
[X] Migration sem teste reverso → alembic upgrade + downgrade
[X] Commit sem rodar testes → sempre pytest antes
```

---

## Quando pedir ajuda ao usuario

Antes de pedir, verifique:
1. Releu todas as skills relevantes?
2. Leu o prompt correspondente?
3. Verificou ADRs em `decisions/`?
4. Buscou no codigo por exemplos similares?
5. Leu FOUNDATION.md + docs/sprints/?

Se AINDA nao resolveu, faca pergunta ESPECIFICA:

**Errado**: "Nao sei como fazer X, me ajuda"

**Certo**: "Para a feature Y, encontrei 2 abordagens no ADR 003 (link). A abordagem A faz Z mas tem trade-off W. A abordagem B faz V mas tem trade-off U. Qual voce prefere?"

---

## Entrega final

Quando terminar, responda ao usuario com:

1. **O que foi feito** (1-2 paragrafos)
2. **Arquivos criados/modificados** (lista)
3. **Como testar** (comandos curl ou passos no browser)
4. **Screenshots/GIFs** (se for UI)
5. **Limitacoes conhecidas** (se houver)
6. **Proximos passos sugeridos** (opcional)

---

## Exemplo completo

```
Usuario: "Implementa o CRUD de leads da Sprint 2"

Voce:
1. Carrega .skills/revenue-sdr-os-architect.md
2. Carrega .skills/sqlmodel-migration.md (vai criar model)
3. Carrega .skills/fastapi-multi-tenant.md (vai criar API)
4. Carrega .skills/htmx-alpine-component.md (vai criar UI)
5. Carrega .skills/pytest-tenant-isolation.md (vai testar)
6. Le prompts/03-create-model.md (lead model)
7. Le prompts/04-create-migration.md (alembic migration)
8. Le prompts/01-create-api-endpoint.md (CRUD endpoints)
9. Le prompts/02-create-htmx-page.md (lista de leads UI)
10. Le prompts/05-create-test.md (testes)
11. Le templates/* (codigo base)
12. Implementa model Lead
13. Implementa alembic migration
14. Implementa endpoints POST /leads, GET /leads, GET /leads/{id}, PATCH /leads/{id}, DELETE /leads/{id}
15. Implementa UI /leads com HTMX
16. Implementa testes (CRUD + tenant isolation)
17. Roda pytest, alembic upgrade, curl health
18. Commit: "feat: CRUD de leads com tenant isolation"
19. Push
20. Reporta ao usuario com: arquivos, como testar, screenshots
```

---

*"Nunca mais perca um lead por falta de acompanhamento."*