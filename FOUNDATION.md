# FOUNDATION.md — Revenue SDR OS (v2.3)

> **Documento fundador do produto.** O QUE estamos construindo e POR QUE.
> O COMO detalhado vive em [ARCHITECTURE.md](ARCHITECTURE.md).
> Historico de ideacao: `~/AGENCIA/SDR/docs/historico/IDEA.md` e
> `IDEA_01_SDR_WhiteLabel.md`.

---

## 1. O paradigma (o "por que")

O Revenue SDR OS **nao e** um CRM tradicional (focado em cadastros) e **nao e**
uma plataforma de disparo de Zap (focada em mensagens).

E um **Sistema Operacional de Vendas orientado a conversas**: a entidade raiz
nao e o *Lead*, mas sim o **Relacionamento (Conversa)** — que evolui no tempo,
atravessa canais (omnichannel) e e orquestrado de forma autonoma por IA.

> **Promessa: "Nunca mais perca um lead por falta de acompanhamento."**

O cliente nao compra Zap, Instagram ou IA. **Ele compra agenda cheia.**

## 2. Os 4 pilares (dificeis de copiar)

1. **Memoria persistente do relacionamento** — cada interacao, preferencia e
   objecao fica registrada e alimenta futuras conversas.
2. **Orquestracao inteligente entre canais** — o sistema escolhe o melhor
   momento, canal e formato (texto, audio, video, ligacao) para cada contato.
3. **Inteligencia comercial** — a IA pensa como vendedor experiente:
   qualifica, prioriza e sugere o proximo passo.
4. **Foco em receita** — todos os indicadores convergem para uma pergunta:
   *qual e a proxima acao que maximiza a probabilidade de venda?*

## 3. Os 8 "Brains" (modulos de dominio)

| Brain | Funcao | Sprint |
|---|---|---|
| **Lead Brain** | Unifica identidades cross-channel: uma pessoa, nao N contatos por canal | S2 |
| **Memory Brain** | Extrai e lembra atributos de longo prazo (objecoes, datas, contexto financeiro) | S2 |
| **Opportunity Brain** | Scoring baseado em eventos (respondeu rapido +5, perguntou preco +25...) | S3 |
| **Omnichannel Engine** | Continuidade entre canais: IG -> Zap -> email -> ligacao | S3/S8 |
| **Cadence & Multi-Scenario Follow-up Engine** | Maquina de estados de regua dinamica e follow-up multi-cenario (recuperacao de objecoes, re-venda e lembretes) (ADR-039) | S3/S4 |
| **AI Sales Brain** | Abstracao de LLMs com Instructor/Pydantic, RAG e Tool Calling; age como vendedor senior | S4 |
| **Manager & Native Calendar Operations** | Gestao de relatorios e ferramenta interna integrada de calendario/agendamentos (Google Cal/Cal.com/ics) (ADR-040) | S5-S7 |
| **Revenue Brain** | Pensa dinheiro: por que perdemos leads, onde esta o gargalo, o que sugerir | S7 |


Conceitos derivados (pos-MVP): Playbooks verticais por nicho, Modo Closer,
Coach de vendedores pos-conversa, Radar de abandono, Emotional Timeline,
Missoes diarias do vendedor.

## 4. Modelo de negocio: White Label em 4 niveis

```
Platform Owner (MyraOS)
  +-- White Label Partner (revende como produto proprio)
       +-- Organization (empresa cliente final)
            +-- Units -> Teams -> Users
```

Implementado hoje: **Organization -> User** (2 niveis). Os demais niveis
evoluem sem quebrar as invariantes de tenancy.

## 5. Arquitetura de deploy: On-Premise-as-a-Service

Em vez de um SaaS monolitico centralizado, **cada cliente final roda em sua
propria VPS dedicada** — isolamento absoluto e adequacao nativa a LGPD.

- **Platform Console (MyraOS)** — no central que operamos: registry de
  releases, monitoramento agregado das VPSs, faturamento, distribuicao de
  atualizacoes.
- **Client Node (VPS do cliente)** — dominio proprio, SSL via Let's Encrypt,
  banco isolado, *Update Agent* via `systemd` que faz pull de atualizacoes a
  cada 6h com rollback automatico.

Consequencia direta de engenharia: **o app precisa ser self-contained** —
assets vendored (sem CDN), Supabase Managed PostgreSQL unificado com pooler Supavisor, zero dependencia de servicos externos nao homologados (Decidido na v0.2.0, evoluido nos ADR-036 e ADR-037).

## 6. Modelo de operacao: consultivo (estilo SAP)

**Nao ha onboarding self-service.** A implantacao e feita pelo nosso time de
Consultoria. Para a engenharia isso significa:

- SEM wizards de onboarding, SEM billing self-service, SEM feature flags no
  frontend
- Foco 100% no core: orquestracao de conversas, eventos, IA e infra

## 7. Tech stack (fixa e otimizada para Agentes de IA)

| Camada | Escolha | Motivo |
|---|---|---|
| Backend | Python 3.12+ / FastAPI | Async nativo, OpenAPI 3.1, API-first estrito |
| ORM / Database Unificado | SQLModel (AsyncPG) sobre Supabase Managed PostgreSQL 16+ com `pgvector` | Engine único unificado com pooler Supavisor (Porta 6543/5432) para transações, histórico, RAG e RLS (ADR-036, ADR-037) |
| Schema & Migrations | Alembic (PostgreSQL Dialect) | Versionamento rígido com DDL transactional nativo compatível com Supabase CLI desde o dia zero (ADR-010, ADR-037) |
| Auth | PyJWT (HS256) + pwdlib/Argon2id | python-jose/passlib abandonados (CVEs), claims `jti` para revogação + RLS no Supabase |
| Frontend | Jinja2 + HTMX + Alpine.js **vendored** | Hypermedia-driven; sem complexidade de SPA, Tailwind + DaisyUI (ADR-001) |
| Tema | CSS variables por tenant | Trocar tenant = trocar CSS, zero JS |
| Real-time | SSE / Supabase Realtime | Server-sent events / WebSockets CDC para atualizações instantâneas no cliente (ADR-005, ADR-037) |
| Fila & Jobs | Taskiq + Redis/Postgres Broker | Fila assíncrona com ContextVar tenant propagation via `TenantTaskiqMiddleware`, idempotência via `job_key` e DLQ (ADR-021, ADR-030) |
| LLM Orchestration | LangChain + LangGraph + Instructor + Pydantic v2 | Grafos de estado com checkpointer persistente no Supabase (`AsyncPostgresSaver`), Tool Calling, fallback router Gemini/Sonnet (900ms primary) (ADR-023, ADR-027, ADR-028, ADR-036, ADR-037) |
| Observabilidade & Tracing | LangSmith + Structlog (JSON Lines) | Tracing visual de grafos LangGraph, telemetria de tokens por tenant e Evals (ADR-014, ADR-029) |
| Vector & RAG Search | Supabase Hybrid RAG (`pgvector` HNSW 1536d + Postgres `tsvector`/BM25 + RRF) | Reciprocal Rank Fusion combinando FTS/BM25 + Cosine Similarity sem `sqlite-vec` (ADR-022, ADR-036, ADR-037) |
| Caching & Protection | In-Memory LRU + Valkey/Redis/DiskCache | Cache de temas/locales + Rate Limiting por tenant e IP (ADR-025) |
| Localização | Presets de Cores + Tradução Granular por Usuário | White-Label real com 5 temas e locales `pt-BR`, `es-ES`, `en-GB`, `de-DE`, `lt-LT` (ADR-013) |
| Standalone Micro-App | Zap Copilot Prototype (`02_ZAP_Prototype`) | Sub-produto de atendimento Zap Web leve com Auto-Sync Background (ADR-017) |
| WhatsApp Guardrails | ZapService + CadenceEngine Protection | Rate limiter Anti-Ban (max 1 msg/3-5s, jitter humano), status `composing` e bloqueio de freeform text >24h (Meta 24h Window) (ADR-032) |

## 8. Principios de dados, Segurança e Performance

1. **Eventos append-only** — tabela central de eventos (timeline): tudo que
   importa vira registro imutavel (`score_changed`, `stage_changed`,
   `objection_detected`). Permite audit log, analytics e replay.
2. **Soft delete e LGPD** — deletar marca `status='deletado'`, nao remove. Suporte a anonimização irreversível sob demanda do titular.
3. **Multi-tenant com defesa em profundidade Zero-Trust** — constraints no banco,
   filtro por ContextVar `organization_id` em toda query, 404 generico cross-tenant,
   token JWT (Argon2id + PyJWT HS256 com `jti`) nao opera fora do tenant de origem, precedência rígida de tenant com bloqueio de overrides `X-Tenant-Slug` não autenticados em produção, propagação de `ContextVar` para workers via `TenantTaskiqMiddleware` e suíte de 100% de isolamento (ADR-018, ADR-030).
4. **SLAs de Performance Rigorosos (P95)** — PostgreSQL local/pooled < 15ms, Core API < 50ms, SSE < 100ms, Z-API Webhook < 300ms, Whisper < 1.5s, SDR Agent LLM < 1.2s (com timeout primário de 900ms e limite acumulado de 1.8s) (ADR-019, ADR-023).
5. **Garantia de Qualidade & Cobertura** — Cobertura geral backend > 85%, isolamento multi-tenant 100%, validação round-trip de Alembic migrations e Visual Quality Control (ADR-020).
6. **Desenvolvimento Orientado a Agentes de IA** — Todo o repositório é construído sob guardiões de código estritos legíveis por IA, com contratos Pydantic e harness automático de teste pré-commit (ADR-026).
7. **Arquitetura PostgreSQL Unificada & Continuidade de Dados** — Banco de dados PostgreSQL 16+ único para transações operacionais, histórico de conversas, memórias e vetores `pgvector`, eliminando latência de movimentação e reidratação entre bancos (ADR-036).
8. **Resiliência no WhatsApp & Compliance Meta** — Bloqueio estrito de mensagens em texto livre após a janela de 24h da Meta (forçando HSM Templates), rate limiter token bucket, jitter randômico (2.0s-6.0s), status `composing` e download imediato de áudios no Taskiq (ADR-032).

## 9. Onde vive o que

| O que | Onde |
|---|---|
| **Codigo do produto** | `~/AGENCIA/SDR/` -> [Revenue_SDR_OS](https://github.com/Fernando-DaSilva/Revenue_SDR_OS) |
| **Arquitetura/docs (este repo)** | `~/AGENCIA/Revenue_SDR_Architecture/` -> [Revenue_SDR_Architecture](https://github.com/Fernando-DaSilva/Revenue_SDR_Architecture) |
| **SDR Command Center UI Prototype** | `~/AGENCIA/01_SDR_Prototype/` (Wireframe de Alta Fidelidade + White-Label Theme Studio + Multi-Channel Inbox) |
| **Zap Standalone Micro-App** | `~/AGENCIA/02_ZAP_Prototype/` (Micro-app Zap Copilot + Auto-Sync Background) |
| Ideacao historica | `~/AGENCIA/SDR/docs/historico/` |

## 10. Estado atual (2026-08-10)

**v0.2.0 (baseline, commit `4513a29`)**: fundacao profissional — multi-tenancy,
auth dupla (cookie+Bearer), white-label, Alembic, 57 testes isolados, CI verde.

O planejamento estratégico **(Sprint 00 e Specs de Arquitetura) está finalizado**, e todas as Sprints (01 a 10) contam com especificações arquiteturais alinhadas aos protótipos de alta fidelidade (`01_SDR_Prototype` e `02_ZAP_Prototype`), aos SLAs de Performance (ADR-019), à Segurança Zero-Trust (ADR-018), à Matriz de Qualidade (ADR-020), aos Guardiões de Agentes de IA (ADR-026) e aos novos ADRs de resiliência e compliance (ADR-030, ADR-031, ADR-032).

**Proximo**: Execução técnica da Sprint 02 — Lead Brain + Memory Brain
([spec](Sprints/02_Sprint_02_Lead_Brain_Memory_Brain/README.md)).

---

*"A maioria dos CRMs e construida em torno de cadastros. A maioria das
plataformas de Zap, em torno de mensagens. Nos somos construidos em
torno de conversas que evoluem ate a venda."*
