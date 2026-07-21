# Revenue SDR OS — Arquitetura

> **Este repo e onde mora o "COMO" construir o produto.**
> O codigo vive em [Revenue_SDR_OS](https://github.com/Fernando-DaSilva/Revenue_SDR_OS) (`~/AGENCIA/SDR/`).

```
+----------------------------------------------------------------------+
|  Este repo: VISAO, DECISOES (ADRs), SKILLS, SPECS DE SPRINT         |
|  Repo code: ~/AGENCIA/SDR/ -> github.com/Fernando-DaSilva/...       |
|                                                                      |
|  Leitura essencial (nesta ordem):                                   |
|    1. FOUNDATION.md     -> o QUE e POR QUE                          |
|    2. ARCHITECTURE.md   -> o COMO (invariantes + ADRs)              |
|    3. ROADMAP.md        -> sprints e status                         |
|    4. Sprints/XX_*/     -> spec da sprint vigente                   |
+----------------------------------------------------------------------+
```

---

## Documentos centrais

| Doc | Conteudo | Status |
|---|---|---|
| [FOUNDATION.md](FOUNDATION.md) | Visao do produto, 8 Brains, modelo de negocio/deploy, stack | v2.0 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Arquitetura vigente + 12 ADRs | v2.0 |
| [ROADMAP.md](ROADMAP.md) | Sprints 01-10 com status real | v2.0 |
| [AGENTS.md](AGENTS.md) | Manual para agentes de codificacao | v2.0 |

## Estrutura

```
Revenue_SDR_Architecture/
|
+-- FOUNDATION.md / ARCHITECTURE.md / ROADMAP.md / AGENTS.md
|
+-- .skills/                       <- contexto tecnico carregavel por tema
|   +-- revenue-sdr-os-architect.md     (SEMPRE carregar primeiro)
|   +-- fastapi-multi-tenant.md         (padroes de API + tenancy)
|   +-- sqlmodel-migration.md           (models + Alembic)
|   +-- htmx-alpine-component.md        (padroes de UI)
|   +-- pytest-tenant-isolation.md      (testes — CRITICOS)
|   +-- whatsapp-zapi-integration.md    (Sprint 4)
|   +-- sse-realtime-pattern.md         (Sprint 6)
|   +-- observability-stack.md          (Sprint 5+)
|
+-- Sprints/                       <- spec por sprint
|   +-- 00_Sprint_00_Arquitetura_e_Gestao/           [CONCLUIDA]
|   +-- 01_Sprint_01_Foundation_Auth_WhiteLabel/     [CONCLUIDA v0.2.0]
|   +-- 02_Sprint_02_Lead_Brain_Memory_Brain/        [PROXIMA]
|   |   +-- prompts/                <- specs por tarefa (T1-T12)
|   +-- 03_Sprint_03_Conversations_Opportunity/      [DOCUMENTADA]
|   +-- 04_Sprint_04_AI_Sales_Brain_WhatsApp/        [DOCUMENTADA]
|   +-- 05_Sprint_05_Omnichannel_UI_Handoff_Calendar/[DOCUMENTADA]
|   +-- 06_Sprint_06_Transcricao_DHS_Sugestoes/      [DOCUMENTADA]
|   +-- 07_Sprint_07_Relatorio_PosConversa/          [DOCUMENTADA]
|   +-- 08_Sprint_08_VPS_Dedicada_Automatizada/      [DOCUMENTADA]
|   +-- 09_Sprint_09_MultiUnit_Franquias/            [DOCUMENTADA]
|   +-- 10_Sprint_10_Marketplace_Tribo/              [DOCUMENTADA]
|
+-- prompts/                       <- specs genericas reutilizaveis
|   +-- 01-create-api-endpoint.md
|
+-- templates/                     <- codigo base
    +-- fastapi-route.py
```

## Como este repo e usado

### Pelo arquiteto/orquestrador (Fernando + agente de arquitetura)

1. Decide/revisa: FOUNDATION, ARCHITECTURE (ADRs), ROADMAP
2. Detalha a sprint vigente em `Sprints/XX_*/README.md` + `prompts/`
3. Mantem `.skills/` alinhadas com o codigo real

### Pelo agente de codificacao (constroi no repo de codigo)

1. Le `AGENTS.md` do repo de codigo (`~/AGENCIA/SDR/AGENTS.md`) — regras duras
2. Carrega `.skills/revenue-sdr-os-architect.md` + skills da tarefa
3. Le o spec da sprint em `Sprints/XX_*/` e os prompts por tarefa
4. Implementa no `~/AGENCIA/SDR/` seguindo os templates
5. Valida com o checklist do prompt; commit + push

### Convencoes deste repo

- Markdown PT-BR **sem acentos** (evitar mojibake), ASCII art otimizado
- Skills: frontmatter YAML + principios + exemplos + anti-patterns + checklist
- Prompts: contexto + tasks com codigo-guia + validacao + checklist
- Decisoes: registradas como ADR em [ARCHITECTURE.md](ARCHITECTURE.md)

## Estado do projeto (2026-07-21)

| Item | Status |
|---|---|
| Fundacao (Sprint 01) | **v0.2.0 reescrita e validada** (57 testes, CI verde) |
| Estratégia (Sprint 00) | **Concluída**. Todas as Sprints (01 a 10) documentadas. |
| Sprint 02 spec | Revisada e alinhada a v0.2.0 — pronta para execucao |
| Proximo passo | Executar Sprint 02 (Lead Brain + Memory Brain) |

---

*Repo vivo: conforme o produto evolui, estes docs evoluem junto.
Codigo NAO vive aqui.*
