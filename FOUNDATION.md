# FOUNDATION.md — Revenue SDR OS (v2.0)

> **Documento fundador do produto.** O QUE estamos construindo e POR QUE.
> O COMO detalhado vive em [ARCHITECTURE.md](ARCHITECTURE.md).
> Historico de ideacao: `~/AGENCIA/SDR/docs/historico/IDEA.md` e
> `IDEA_01_SDR_WhiteLabel.md`.

---

## 1. O paradigma (o "por que")

O Revenue SDR OS **nao e** um CRM tradicional (focado em cadastros) e **nao e**
uma plataforma de disparo de WhatsApp (focada em mensagens).

E um **Sistema Operacional de Vendas orientado a conversas**: a entidade raiz
nao e o *Lead*, mas sim o **Relacionamento (Conversa)** — que evolui no tempo,
atravessa canais (omnichannel) e e orquestrado de forma autonoma por IA.

> **Promessa: "Nunca mais perca um lead por falta de acompanhamento."**

O cliente nao compra WhatsApp, Instagram ou IA. **Ele compra agenda cheia.**

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
| **Omnichannel Engine** | Continuidade entre canais: IG -> WhatsApp -> email -> ligacao | S3/S8 |
| **Cadence Engine** | Maquina de estados da regua de relacionamento por temperatura do lead | S3 |
| **AI Sales Brain** | Abstracao de LLMs (OpenAI/Anthropic) com RAG/Tools; age como vendedor senior, nao chatbot | S4 |
| **Manager Brain** | Numeros do dono: funil, CAC, ROI, canal vencedor, melhor vendedor | S5-S7 |
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
assets vendored (sem CDN), SQLite embarcado, zero dependencia de servicos
externos obrigatorios. (Decidido e aplicado na v0.2.0.)

## 6. Modelo de operacao: consultivo (estilo SAP)

**Nao ha onboarding self-service.** A implantacao e feita pelo nosso time de
Consultoria. Para a engenharia isso significa:

- SEM wizards de onboarding, SEM billing self-service, SEM feature flags no
  frontend
- Foco 100% no core: orquestracao de conversas, eventos, IA e infra

## 7. Tech stack (fixa)

| Camada | Escolha | Motivo |
|---|---|---|
| Backend | Python 3.12+ / FastAPI | Async nativo, OpenAPI, API-first |
| ORM/DB | SQLModel sobre SQLite (WAL) | Pydantic+SQLAlchemy; Postgres depois e troca de URL |
| Schema | Alembic | Versionamento rigido desde o dia zero |
| Auth | PyJWT (HS256) + pwdlib/Argon2id | python-jose/passlib abandonados (CVEs) |
| Frontend | Jinja2 + HTMX + Alpine.js **vendored** | Hypermedia-driven; sem complexidade de SPA |
| Tema | CSS variables por tenant | Trocar tenant = trocar CSS, zero JS |
| Real-time | SSE (nao WebSocket) | Unidirecional server->client, simples |
| Jobs | ARQ/APScheduler (Sprint 3+) | Cadencias e missoes agendadas, idempotentes |

## 8. Principios de dados

1. **Eventos append-only** — tabela central de eventos (timeline): tudo que
   importa vira registro imutavel (`score_changed`, `stage_changed`,
   `objection_detected`). Permite audit log, analytics e replay.
2. **Soft delete** — LGPD: deletar marca `status='deletado'`, nao remove.
3. **Multi-tenant com defesa em profundidade** — constraints no banco,
   filtro por `organization_id` em toda query, 404 generico cross-tenant,
   token JWT nao opera fora do tenant de origem, testes de isolamento.

## 9. Onde vive o que

| O que | Onde |
|---|---|
| **Codigo do produto** | `~/AGENCIA/SDR/` -> [Revenue_SDR_OS](https://github.com/Fernando-DaSilva/Revenue_SDR_OS) |
| **Arquitetura/docs (este repo)** | `~/AGENCIA/Revenue_SDR_Architecture/` -> [Revenue_SDR_Architecture](https://github.com/Fernando-DaSilva/Revenue_SDR_Architecture) |
| Ideacao historica | `~/AGENCIA/SDR/docs/historico/` |

## 10. Estado atual (2026-07-21)

**v0.2.0 (baseline, commit `4513a29`)**: fundacao profissional — multi-tenancy,
auth dupla (cookie+Bearer), white-label, Alembic, 57 testes isolados, CI verde.

O planejamento estratégico **(Sprint 00) está finalizado**, e todas as futuras Sprints (03 a 10) estão com especificações arquiteturais baseadas no `ROADMAP.md` e armazenadas na pasta `Sprints/`.

**Proximo**: Sprint 02 — Lead Brain + Memory Brain
([spec](Sprints/02_Sprint_02_Lead_Brain_Memory_Brain/README.md)).

---

*"A maioria dos CRMs e construida em torno de cadastros. A maioria das
plataformas de WhatsApp, em torno de mensagens. Nos somos construidos em
torno de conversas que evoluem ate a venda."*
