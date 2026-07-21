# ROADMAP.md — Visao de Sprints

> Status real do projeto. Atualizado em 2026-07-20 (baseline v0.2.0).

---

## Mapa geral

```
Sprint 01 [OK] Foundation + Auth + White-Label        (reescrita v0.2.0)
Sprint 02 [>>] Lead Brain + Memory Brain              PROXIMA
Sprint 03 [DOC] Conversations + Opportunity + Cadence
Sprint 04 [DOC] AI Sales Brain + Z-API WhatsApp
Sprint 05 [DOC] Monitoramento + handoff IA<->Humano + Google Calendar
Sprint 06 [DOC] Transcricao + grafico DHS + sugestoes de objecao (SSE)
Sprint 07 [DOC] Relatorio pos-conversa + Manager/Revenue Brain
Sprint 08 [DOC] Omnichannel completo (IG, email, voice)
Sprint 09 [DOC] VPS dedicada automatizada + Update orchestrator
Sprint 10 [DOC] Playbooks verticais + Marketplace
```

---

## Sprint 01 — Foundation + Auth + White-Label [CONCLUIDA]

Entregue e **reescrita em qualidade profissional (v0.2.0)**:

- Multi-tenancy: middleware ASGI + ContextVar; custom_domain; 404 cross-tenant
- Auth: Argon2id + PyJWT; cookie HttpOnly + Bearer; roles
- White-label: CSS variables por tenant; assets vendored
- **White-label Avançado (v2.1.0)**: Tradução granular por tela e usuário (Locales: `pt-BR`, `es-ES`, `en-GB`, `de-DE`, `lt-LT`); 5 presets de cores iniciais (Sakura Bloom, Emerald Garden, Ocean Breeze, Obsidian Night, Amber Warmth).
- Alembic desde o dia zero; 57 testes isolados; ruff limpo; CI verde
- Script `./start` (setup + migrate + seed + serve)

Docs: [spec](Sprints/01_Sprint_01_Foundation_Auth_WhiteLabel/README.md) |
Codigo: [Revenue_SDR_OS](https://github.com/Fernando-DaSilva/Revenue_SDR_OS)

## Sprint 02 — Lead Brain + Memory Brain [PROXIMA]

Escopo: CRUD de leads com merge de identidades, memories estruturadas,
timeline de eventos append-only, UI de lista/detalhe.

Docs: [spec](Sprints/02_Sprint_02_Lead_Brain_Memory_Brain/README.md) |
[prompts](Sprints/02_Sprint_02_Lead_Brain_Memory_Brain/prompts/README.md)

Decisoes em aberto: ver secao "Decisoes pendentes" no spec da sprint.

## Sprint 03 — Conversations + Opportunity + Cadence

- `conversations` como agregado raiz (lead vira participante)
- `messages` + tabela central `events` (generaliza a timeline)
- Opportunity Brain: scoring por eventos
- Cadence Engine: maquina de estados + jobs agendados (fila leve)

## Sprint 04 — AI Sales Brain + Z-API WhatsApp

- Abstracao `WhatsAppProvider` (Z-API primeiro; ver ADR-003)
- Webhook inbound + envio outbound
- AI Sales Brain: LLM com RAG/Tools, persona de vendedor senior
- Modo `ai` vs `human` por conversa

## Sprint 05 — Monitoramento + handoff + Calendar

- Handoff IA<->Humano com contexto preservado
- Google Calendar sync (agendar reuniao via tool da IA)
- Observabilidade: Prometheus + logs JSON (skill pronta)

## Sprint 06 — Real-time (SSE)

- Notificacoes live, transcricao de audio, grafico DHS
- SSE broker in-memory (skill pronta; ADR-005)

## Sprint 07 — Pos-conversa + Manager/Revenue Brain

- Coach de vendedores (analise IA da conversa)
- Dashboards de funil, CAC, ROI, canal vencedor

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
