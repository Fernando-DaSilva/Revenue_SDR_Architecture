# ROADMAP.md — Visao de Sprints

> Status real do projeto. Atualizado em 2026-07-21 (baseline v0.2.0).

---

> [!IMPORTANT]
> **Alinhamento do Roadmap com a Realidade do Produto:**
> - **Sprints 00–01.5 (Fundacao & Prototipos)**: Representam a infraestrutura base de arquitetura e prototipos de design (UI/UX). A **capacidade real do produto** (funcionalidades integradas no backend) inicia formalmente a partir da **Sprint 02 (Lead Brain)**.
> - **Prototipos em Codigo**: `01_SDR_Prototype` e `02_ZAP_Prototype` sao **UI/UX Wireframes em Codigo** (prototipos visuais standalone), NAO funcionalidades integradas ao backend do produto.

---

## Mapa Geral de Execução Hyper-Acelerado (8 Semanas / 60 Dias / Micro-Sprints Horárias)

```
MÊS 1 (SEMANAS 1-4 / DIAS 1-28): CORE ENGINE, IA MULTI-AGENTE & MESSAGING
Semana 1 [MICRO-SPRINTS 02.1-02.8] Lead Brain + Memory Brain + Taskiq Tenant Propagation (ADR-030)
Semana 2 [MICRO-SPRINTS 03.1-03.8] Conversations + Opportunity Brain + Multi-Scenario Follow-up Engine (ADR-039) + Meta 24h HSM (ADR-032)
Semana 3 [MICRO-SPRINTS 04.1-04.8] AI Sales Brain + AsyncPostgresSaver + Z-API WhatsApp Anti-Ban (ADR-036, ADR-037)
Semana 4 [MICRO-SPRINTS 05.1-05.8] Human-AI Handoff + Desconstrução HTML Monólito + Native Integrated Calendar Operations & Sync (ADR-040)


MÊS 2 (SEMANAS 5-8 / DIAS 29-60): REALTIME, OMNICHANNEL & SCALE
Semana 5 [MICRO-SPRINTS 06.1-06.8] Transcrição Whisper + Fix Memory Leak Chart.js + Stream SSE Real-Time
Semana 6 [MICRO-SPRINTS 07.1-07.8] Pós-Conversa Sales Coach + Unified Supabase PostgreSQL RAG & Analytics (ADR-036, ADR-037)
Semana 7 [MICRO-SPRINTS 08.1-08.8] Omnichannel Engine (Instagram DM, Email, Voice Agent)
Semana 8 [MICRO-SPRINTS 09.1-10.8] VPS Single-Tenant Automation + MyraOS Console + Playbooks & Marketplace
```

---

## Sprint 01 — Foundation + Auth + White-Label [CONCLUIDA — FUNDACAO TECNICA]

Entregue e **reescrita em qualidade profissional (v0.2.0)**:

- Multi-tenancy: middleware ASGI + ContextVar; custom_domain; 404 cross-tenant
- Auth: Argon2id + PyJWT; cookie HttpOnly + Bearer; roles
- White-label: CSS variables por tenant; assets vendored
- **White-label Avançado (v2.1.0)**: Tradução granular por tela e usuário (Locales: `pt-BR`, `es-ES`, `en-GB`, `de-DE`, `lt-LT`); 5 presets de cores iniciais (Sakura Bloom, Emerald Garden, Ocean Breeze, Obsidian Night, Amber Warmth).
- Alembic desde o dia zero; 57 testes isolados; ruff limpo; CI verde
- Script `./start` (setup + migrate + seed + serve)

Docs: [spec](Sprints/01_Sprint_01_Foundation_Auth_WhiteLabel/README.md) |
Codigo: [Revenue_SDR_OS](https://github.com/Fernando-DaSilva/Revenue_SDR_OS)

## Sprint 01.5 — Standalone Zap Micro-App Prototype (02_ZAP_Prototype) [CONCLUIDA — PROTOTIPO UI/UX]

Prototipo visual interativo (`02_ZAP_Prototype`):
- **Classificacao**: UI/UX Wireframe em Codigo (Standalone Prototype), NAO uma funcionalidade integrada ao backend central.
- UI Grid 3 Colunas, DHS Chart, RAG Suggestions, 5 Themes, Auto-Sync Background Protocol

## Sprint 02 — Lead Brain + Memory Brain [PROXIMA — INICIO DO PRODUTO REAL]

Escopo: CRUD de leads com merge de identidades, memories estruturadas,
timeline de eventos append-only, UI de lista/detalhe.

Docs: [spec](Sprints/02_Sprint_02_Lead_Brain_Memory_Brain/README.md) |
[prompts](Sprints/02_Sprint_02_Lead_Brain_Memory_Brain/prompts/README.md)

Decisoes em aberto: ver secao "Decisoes pendentes" no spec da sprint.

## Sprint 03 — Conversations + Opportunity + Cadence & Multi-Scenario Follow-up Engine

- `conversations` como agregado raiz (lead vira participante)
- `messages` + tabela central `events` (generaliza a timeline)
- Opportunity Brain: scoring por eventos
- Motor de Follow-up Multi-Cenário Automatizado: recuperação de objeções, cadências dinâmicas por temperatura e reagendamento de contatos (ADR-039)

## Sprint 04 — AI Sales Brain + Z-API Zap (LangChain & LangGraph Multi-Agent Engine)

- Abstracao `ZapProvider` (Z-API primeiro; ver ADR-003)
- Webhook inbound + envio outbound via fila Taskiq (ADR-021)
- AI Sales Brain: Grafo **LangGraph (`StateGraph`)** com checkpointer de memória, `@tool` calling, fallbacks `with_fallbacks()` (Gemini 2.5 Flash / Sonnet 3.5 -> GPT-4o-mini), e tracing no **LangSmith** (ADR-027, ADR-028, ADR-029)
- Modo `ai` vs `human` por conversa via interrupção `interrupt()` (Human-in-the-Loop no `02_ZAP_Prototype`)

## Sprint 05 — Monitoramento + Handoff + Ferramenta Interna Integrada de Calendário (ADR-040)

- Handoff IA<->Humano com contexto preservado
- Sistema Interno Integrado de Calendário & Agendamentos: Dashboard de Eventos, disponibilidade de vendedores, ciclo de vida de reuniões e sincronização bidirecional/exportação com Google Calendar, Cal.com e `.ics` (ADR-040)
- Observabilidade: Prometheus + logs JSON (skill pronta; ADR-014)


## Sprint 06 — Real-time (SSE)

- Notificacoes live, transcricao de audio, grafico DHS
- SSE broker in-memory (skill pronta; ADR-005)

## Sprint 07 — Pos-conversa, Dashboards e Pipeline Analítico (ADR-015)

- Pipeline ETL/CDC para Data Warehouse externo (Supabase/Postgres/MS-SQL)
- Rotina de Arquivamento (Cold Storage) e expurgo no SQLite local
- Coach de vendedores (analise IA da conversa)
- Dashboards Analíticos de funil, CAC, ROI, canal vencedor (Lendo do DW)

## Sprint 08 — Omnichannel completo

- Instagram DM, email, voice como canais plenos
- Omnichannel Engine: continuidade inteligente entre canais

## Sprint 09 — VPS por cliente + Update orchestrator

- Platform Console (MyraOS): registry, monitoramento, billing
- Update Agent (systemd): pull a cada 6h + rollback (ADR-004)

## Sprint 10 — Playbooks verticais + Marketplace

- Playbooks por nicho (clinica, imobiliaria, consorcio...)
- Marketplace de playbooks/agentes (Tribo)

---

*Ordem de leitura para contexto completo:
[FOUNDATION.md](FOUNDATION.md) -> [ARCHITECTURE.md](ARCHITECTURE.md) ->
spec da sprint vigente.*
