# Prompts — Sprint 02 (Lead Brain + Memory Brain)

> **Cada prompt e' uma spec de tarefa, alinhada a v0.2.0.**
> Antes de qualquer um: carregar as skills base.

## Skills a carregar (sempre)

```
1. .skills/revenue-sdr-os-architect.md     (contexto do produto — SEMPRE)
2. .skills/fastapi-multi-tenant.md         (padroes de API/service/schema)
3. .skills/sqlmodel-migration.md           (models + Alembic)
4. .skills/htmx-alpine-component.md        (quando houver UI)
5. .skills/pytest-tenant-isolation.md      (testes — CRITICOS)
```

## Ordem de execucao

```
1. 01-create-models.md          → T1: models Lead/Memory/TimelineEvent
2. 02-create-migration.md       → T2: migration Alembic (+ indices compostos)
3. 03-create-merge-service.md   → T3: LeadMerger (dedup + merge conservador)
4. 04-create-leads-api.md       → T4-T7: API de leads + timeline
5. 05-create-memories-api.md    → T8: API de memories + extractor placeholder
6. 06-create-isolation-tests.md → T11: testes de isolamento (CRITICOS)
99. 99-final-validation.md      → validacao completa + commit
```

UI (lista/detalhe/cadastro) segue `.skills/htmx-alpine-component.md` +
templates do repo de codigo. CSV import (T13) CONFIRMADO no escopo
(decisao D2): upload -> parse -> validacao -> dry-run -> commit, reusando
`LeadService.create` (dedup/merge valem para o CSV tambem).

## Mapeamento tasks x prompts

| Task | Prompt | Esforco |
|---|---|---|
| T1: Models | 01-create-models.md | 4h |
| T2: Migration | 02-create-migration.md | 1h |
| T3: Merge service | 03-create-merge-service.md | 6h |
| T4: Memory extractor (placeholder) | 05-create-memories-api.md | 2h |
| T5-T7: Leads API + timeline | 04-create-leads-api.md | 10h |
| T8: Memories API | 05-create-memories-api.md | 3h |
| T9-T11: UI lista/detalhe/cadastro | skill htmx-alpine | 15h |
| T12: Testes isolamento | 06-create-isolation-tests.md | 8h |
| T13: CSV import (confirmado) | (padroes 04 + merge) | 4h |
| **TOTAL** | | **~53h** |

## Regras

1. Siga a ORDEM — cada task depende da anterior
2. Convencoes v0.2.0: pacotes de dominio, TenantMixin, JSON nativo,
   envelope de erro, validacao nos schemas
3. Decisoes D1 (merge conservador automatico), D2 (CSV no escopo) e
   D3 (status congelado) estao TOMADAS — ver spec da sprint
4. Duvida? Releia o spec (`../README.md`) e as skills. Persistindo,
   pergunte ao usuario com opcoes + trade-offs — NAO invente decisao

---

*"Cada prompt e' um ticket. Cada agente e' um dev. O usuario e' o PM."*
