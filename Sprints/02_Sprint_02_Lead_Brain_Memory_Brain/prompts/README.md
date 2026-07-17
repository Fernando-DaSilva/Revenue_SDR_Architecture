# Prompts — Sprint 02 (Lead Brain + Memory Brain)

> **Cada prompt e' copy-paste ready pra um agente de IA externo (Claude Code, Codex, OpenCode).**

## Ordem de execucao

```
1. 01-create-models.md        → T1: criar models Lead, LeadMemory, LeadTimelineEvent
2. 02-create-migration.md     → T2: configurar Alembic + gerar migration
3. 03-create-merge-service.md → T3: criar service de merge automatico
4. 04-create-leads-api.md     → T4-T7: API CRUD de leads + timeline
5. 05-create-memories-api.md  → T8-T10: API CRUD de memories
6. 06-create-isolation-tests.md → T11: testes CRITICOS de tenant isolation
99. 99-final-validation.md    → validar tudo + commit
```

## Skills a carregar (sempre)

```
Antes de QUALQUER prompt:
1. /Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/.skills/revenue-sdr-os-architect.md
2. /Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/.skills/fastapi-multi-tenant.md
3. /Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/.skills/sqlmodel-migration.md
4. /Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/.skills/htmx-alpine-component.md
5. /Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/.skills/pytest-tenant-isolation.md
```

## Estrutura de tasks

| Task | Prompt | Esforco |
|---|---|---|
| T1: Models | 01-create-models.md | 4h |
| T2: Migration | 02-create-migration.md | 1h |
| T3: Merge service | 03-create-merge-service.md | 6h |
| T4: Memory extractor (placeholder) | (sem prompt — implementar basico) | 2h |
| T5: Leads API (CRUD) | 04-create-leads-api.md | 6h |
| T6: Memories API | 05-create-memories-api.md | 3h |
| T7: Lead timeline API | (parte de 04) | 2h |
| T8: UI lista de leads | (sem prompt detalhado — usar skill htmx) | 6h |
| T9: UI detalhe do lead | (sem prompt detalhado) | 6h |
| T10: UI cadastro de lead | (sem prompt detalhado) | 3h |
| T11: Testes tenant isolation | 06-create-isolation-tests.md | 8h |
| T12: CSV Import | (sem prompt detalhado — opcional) | 4h |
| **TOTAL** | | **~51h** |

## Como executar

1. Abra o Claude Code (ou Codex, OpenCode)
2. Carregue as 5 skills (cole os paths)
3. Carregue o prompt 01-create-models.md
4. Execute. Quando terminar, va para o 02, etc.

## Quando um prompt nao cobre uma task

Use o **template** correspondente em `/Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/templates/`:
- `fastapi-route.py` — pra criar endpoint novo
- `sqlmodel-tenant-model.py` — pra criar model novo
- `pytest-isolation-test.py` — pra criar teste de isolation
- `htmx-component.html` — pra criar componente UI

## Se voce (agente) tiver duvida

Releia:
1. `../README.md` (visao geral da sprint)
2. Skills carregaveis (`.skills/`)
3. Templates (se aplicavel)
4. ADRs em `/Volumes/Workspace_iOS/AGENCIA/00_SDR_architecture/decisions/`

Se AINDA nao resolveu, **pergunte ao usuario (Fernando)**. NAO invente decisao.

---

*"Cada prompt e' um ticket. Cada agente e' um dev. O usuario e' o PM."*