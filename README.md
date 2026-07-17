# Revenue SDR OS — Arquitetura

> **Este folder e' onde mora o "COMO" construir o produto.**
> O codigo em si vive em `~/AGENCIA/SDR/` (repo GitHub).

```
+----------------------------------------------------------------------+
|                                                                      |
|   Este folder: ARQUITETURA, SKILLS, PROMPTS, ADRs                   |
|   Repo code:   ~/AGENCIA/SDR/ → github.com/Fernando-DaSilva/...    |
|                                                                      |
|   Fluxo:                                                             |
|     Eu defino specs/aqui → Voce passa pros agentes → Eles constroem |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Estrutura

```
00_SDR_architecture/
|
+-- README.md                         ← voce esta aqui
+-- FOUNDATION.md                     ← doc principal do projeto (v1.4)
+-- ARCHITECTURE.md                   ← ADRs e decisoes tecnicas
+-- AGENTS.md                         ← manual pra outros agentes
+-- ROADMAP.md                        ← visao geral dos sprints
|
+-- .skills/                          ← skills carregaveis por agentes
|   +-- revenue-sdr-os-architect.md   ← skill principal (SEMPRE carregar)
|   +-- fastapi-multi-tenant.md       ← padroes de API REST + tenant isolation
|   +-- sqlmodel-migration.md         ← schema, migrations Alembic, ID prefixes
|   +-- htmx-alpine-component.md      ← padroes de UI + CSS variables
|   +-- pytest-tenant-isolation.md    ← testes (CRITICOS)
|   +-- whatsapp-zapi-integration.md  ← integracao WhatsApp (Z-API)
|   +-- sse-realtime-pattern.md       ← Server-Sent Events (real-time)
|   +-- observability-stack.md        ← Prometheus + Grafana + logs
|   +-- whatsapp-zapi-integration.md  ← integracao WhatsApp
|   +-- sse-realtime-pattern.md       ← Server-Sent Events
|   +-- observability-stack.md        ← Prometheus + Grafana
|
+-- prompts/                          ← prompts copy-paste pra tarefas
|   +-- README.md                     ← indice dos prompts
|   +-- 01-create-api-endpoint.md
|   +-- 02-create-htmx-page.md
|   +-- 03-create-model.md
|   +-- 04-create-migration.md
|   +-- 05-create-test.md
|   +-- 06-create-cadence-job.md
|   +-- 07-deploy-vps.md
|   +-- 08-add-whatsapp-channel.md
|   +-- 09-add-google-calendar.md
|
+-- templates/                        ← code templates
|   +-- fastapi-route.py
|   +-- sqlmodel-tenant-model.py
|   +-- pytest-isolation-test.py
|   +-- htmx-component.html
|   +-- alembic-migration.py
|
+-- decisions/                        ← Architecture Decision Records
|   +-- README.md
|   +-- 001-why-htmx-alpine-not-react.md
|   +-- 002-why-sqlite-first.md
|   +-- 003-why-z-api-whatsapp.md
|   +-- 004-why-vps-dedicated-not-shared.md
|   +-- 005-why-sse-not-websocket.md
|
+-- docs/sprints/                     ← docs detalhados por sprint
    +-- README.md
    +-- sprint-01-foundation.md
    +-- sprint-02-lead-brain.md
    +-- sprint-03-conversations.md
    +-- ...
```

---

## Como usar

### Para mim (arquiteto — eu)

Quando voce me pedir algo:
1. Eu **atualizo** FOUNDATION.md, ADRs, sprint docs
2. Eu **crio/edito skills** em `.skills/`
3. Eu **crio/edito prompts** em `prompts/`
4. Eu **crio/edito templates** em `templates/`
5. NUNCA escrevo codigo do produto — defino como ele deve ser feito

### Para outros agentes (construtores)

Quando voce passar uma tarefa:
1. Eles **carregam a skill** `revenue-sdr-os-architect.md` (sempre)
2. Eles **carregam skills especificas** conforme a tarefa
3. Eles **leem o prompt** correspondente em `prompts/`
4. Eles **seguem o template** em `templates/`
5. Eles **codam em `~/AGENCIA/SDR/`** (repo separado)
6. Eles **validam com checklist** do prompt
7. Eles **commitam e dao push** no GitHub

### Para voce (orquestrador)

1. Me pede specs/aqui → eu entrego docs + skills + prompts
2. Voce pega os prompts, passa pros agentes (Claude Code, Codex, etc)
3. Agentes constroem no `~/AGENCIA/SDR/`
4. Voce revisa PRs no GitHub
5. Volta pra mim com feedback ou proxima sprint

---

## Convencoes deste folder

- **Markdown**: ASCII art otimizado pra GitHub (caixas, diagramas, setas)
- **Skills**: formato SKILL.md com frontmatter YAML + instrucoes em markdown
- **Prompts**: copy-paste ready, com contexto, passos, criterios de aceitacao
- **Templates**: codigo Python/HTML com TODOs claros pra customizar
- **ADRs**: formato MADR (Markdown Any Decision Record)

---

## Status atual

| Item | Status |
|---|---|
| FOUNDATION.md | A migrar de ~/AGENCIA/SDR/FOUNDATION.md |
| ARCHITECTURE.md | A criar |
| AGENTS.md | A criar |
| ROADMAP.md | A criar |
| Skills | A criar |
| Prompts | A criar |
| Templates | A criar |
| Decisions | A criar |

---

*Esse folder e' vivo. Conforme o projeto evolui, eu atualizo tudo aqui.*
*Codigo em si NAO vive aqui — vive no repo separado.*