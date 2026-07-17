# Sprint 00 — Arquitetura e Gestao

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 00 — ARQUITETURA E GESTAO                                  |
|   Status:  Em andamento (este folder)                                |
|   Owner:   Hermes (arquiteto/orquestrador)                           |
|   Quando:  Continuo (nao tem fim — evolui com o projeto)             |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Objetivo

Construir a fundacao de GESTAO do projeto: skills, prompts, templates, ADRs, sprint docs.
NÃO escreve codigo do produto — isso e' trabalho de outros agentes que consomem este material.

---

## Entregaveis

```
[OK] Estrutura de pastas (Sprints/, .skills/, prompts/, templates/, decisions/, docs/)
[OK] README.md (indice geral)
[OK] AGENTS.md (manual para agentes externos)
[OK] .skills/revenue-sdr-os-architect.md (skill principal)
[OK] .skills/fastapi-multi-tenant.md (padroes de API)
[OK] prompts/01-create-api-endpoint.md (prompt exemplo)
[OK] templates/fastapi-route.py (template de codigo)
[OK] Sprints/ (estrutura das 11 sprints futuras)
[ ] FOUNDATION.md (migrar de ~/AGENCIA/SDR/)
[ ] ARCHITECTURE.md
[ ] ROADMAP.md
[ ] Resto das skills (htmx, sqlmodel, pytest, whatsapp, sse, observability)
[ ] Resto dos prompts (02-09)
[ ] Resto dos templates
[ ] ADRs (001-005+)
[ ] Sprint docs (02-10 detalhadas)
```

---

## Como este sprint se encaixa no projeto

```
Projeto = Sprint 00 (este) + Sprint 01 (feito) + Sprint 02+ (a fazer)

Sprint 00 → define COMO construir (skills, prompts, ADRs)
Sprint 01 → probo que o stack funciona (auth + multi-tenant + white-label)
Sprint 02+ → features do produto (lead, conversas, IA, WhatsApp, etc)
```

---

## Workflow

1. **Eu (Hermes)** defino skills, prompts, templates, ADRs, sprint docs
2. **Voce (Fernando)** orquestra: pega os artefatos, passa pros agentes externos
3. **Agentes externos** (Claude Code, Codex, OpenCode) constroem no `~/AGENCIA/SDR/`
4. **Voce** revisa PRs no GitHub
5. **Eu** documento decisoes em ADRs baseado no feedback

---

## Status detalhado

Ver `STATUS.md` (a criar) ou `README.md` na raiz do folder.

---

*"Arquitetura e' a arte de tomar decisoes faceis de reverter."*
— atribuido a various