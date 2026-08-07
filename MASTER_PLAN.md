# MASTER PLAN — Revenue SDR OS & AI Conversational Architecture

> **Executive & Technical Blueprint for End-to-End Solution Development**  
> **Prepared by**: Engineering Taskforce (Software Architects, AI Engineers, Systems Developers & FinOps Engineers)  
> **Version**: 1.0.0 (Post v0.2.0 Baseline)  
> **Date**: August 2026  

---

## 1. Solution Overview & Strategic Vision

The **Revenue SDR OS** is an **Autonomous Conversational Sales Operating System** designed around a fundamental paradigm shift: **the root entity of sales automation is not the static Lead record or a mass message batch, but the evolving Relationship (Conversation)** across channels.

### Core Value Proposition
> *"Never lose a lead due to lack of follow-up. The client buys a full calendar."*

### Key Architectural Pillars
1. **Persistent Relationship Memory**: Long-term extracted memories (budget, decision makers, objections, timeline) stored per lead and fed dynamically to AI Agents.
2. **Multi-Agent Conversational AI Engine**: Specialized autonomous agents acting as senior SDRs, background memory extractors, lead qualifiers, cadence schedulers, and post-call sales coaches.
3. **Omnichannel Engine**: Seamless conversation continuity across WhatsApp (Z-API), Instagram DM, Email, and Voice.
4. **On-Premise-as-a-Service Deployment**: Dedicated single-tenant VPS nodes per organization managed centrally via the **MyraOS Platform Console**, guaranteeing LGPD compliance, zero data co-mingling, and local execution resilience.
5. **Self-Contained Tech Stack**: FastAPI backend + SQLModel over Turso (libSQL) embedded databases + Jinja2/HTMX/Alpine.js hypermedia frontend + SSE real-time streaming.

---

## 2. Engineering Team Structure & Roles

Executing this solution requires a disciplined, multi-disciplinary engineering taskforce:

| Role | Core Responsibilities |
|---|---|
| **Principal Software Architect** | System topology, multi-tenancy invariants, schema evolution, VPS orchestration, On-Premise-as-a-Service architecture. |
| **Lead AI Systems Engineer** | Multi-agent framework design, prompt engineering, RAG pipelines, function calling schemas, LLM fallback routing, context window compression. |
| **Senior Backend & Data Engineer** | FastAPI domain services, Turso/libSQL database integration, event-driven timeline architecture, ARQ/APScheduler background jobs, SSE broker. |
| **Senior Frontend & UX Engineer** | Jinja2 + HTMX + Alpine.js implementation, white-label color preset translation system, ZAP Copilot Prototype integration. |
| **FinOps & Cost Optimization Specialist** | Token consumption forecasting, multi-tier LLM routing, prompt caching strategies, monthly unit economics per tenant. |
| **QA & Infrastructure/Security Engineer** | Pytest cross-tenant isolation test suite, ruff linting, Alembic migration verification, systemd Update Agent security. |

---

## 3. Comprehensive Phased Roadmap & Timeframe Estimation

The total estimated development timeline is **22 Weeks (~5.5 Months)** divided into **10 execution sprints**, assuming a dedicated core team.

```
Sprint 00 [DONE] Architecture & Governance
Sprint 01 [DONE] Foundation + Auth + White-Label (v0.2.0 Baseline)
Sprint 01.5 [DONE] Standalone ZAP Copilot Prototype (02_ZAP_Prototype)
Sprint 02 [W1-W2] Lead Brain + Memory Brain
Sprint 03 [W3-W4] Conversations + Opportunity Brain + Cadence Engine
Sprint 04 [W5-W7] AI Sales Brain + Z-API WhatsApp Integration
Sprint 05 [W8-W9] Human-AI Handoff + Google Calendar Integration + Observability
Sprint 06 [W10-W11] Audio Whisper Transcription + DHS Chart + SSE Real-Time Stream
Sprint 07 [W12-W14] Post-Call Analysis + Data Warehouse ETL/CDC + Analytics Dashboards
Sprint 08 [W15-W17] Omnichannel Engine (Instagram DM, Email, Voice Agent)
Sprint 09 [W18-W19] Single-Tenant VPS Automation + MyraOS Update Orchestrator
Sprint 10 [W20-W22] Vertical Playbooks + Tribo Agent Marketplace
```

### Detailed Breakdown & Milestone Deliverables

#### Phase 1: Core Intelligence & Engine Foundation (Sprints 02 - 04) | Timeline: Weeks 1 - 7
* **Sprint 02: Lead Brain & Memory Brain (2 Weeks)**
  * Unification of cross-channel identities under `leads` and `lead_identities`.
  * Structured long-term `memories` table with confidence scores & category classifications.
  * Append-only event timeline (`events`).
* **Sprint 03: Conversations, Opportunity Scoring & Cadence Engine (2 Weeks)**
  * `conversations` as root aggregate with `messages`.
  * Event-driven lead scoring system (`Opportunity Brain`) calculating dynamic Hot/Warm/Cold temperature.
  * Lightweight background job queue (ARQ/APScheduler) for cadence follow-up triggers.
* **Sprint 04: AI Sales Brain & Z-API WhatsApp Engine (3 Weeks)**
  * `ZapProvider` abstraction for Z-API inbound webhooks and outbound messaging.
  * AI Sales Brain conversational agent with tool calling (`schedule_meeting`, `add_memory`, `change_stage`).
  * `ai_mode` toggle with real-time sync for `02_ZAP_Prototype` copilot interface.

#### Phase 2: Real-time Operations, Human Handoff & Analytics (Sprints 05 - 07) | Timeline: Weeks 8 - 14
* **Sprint 05: Human-AI Handoff & Calendar Sync (2 Weeks)**
  * Seamless transfer between AI agent and human operator with context summary generation.
  * Two-way Google Calendar integration via AI tool invocation.
  * Structured JSON logging and Prometheus metric endpoints.
* **Sprint 06: Audio Processing & SSE Real-time Streaming (2 Weeks)**
  * Inbound audio message transcription via OpenAI Whisper / Groq API.
  * Server-Sent Events (SSE) broker for live UI updates without WebSockets.
  * DHS (Dynamic Health Score) real-time conversation progress chart.
* **Sprint 07: Post-Call Analysis, Data Warehouse & Dashboards (3 Weeks)**
  * Post-conversation sales coaching agent (identifying objection patterns and missed opportunities).
  * Data archiving & ETL/CDC pipeline exporting local Turso data to external analytical storage (PostgreSQL/Supabase).
  * Manager Brain analytical dashboards (Funnel conversion, CAC, ROI, top channels).

#### Phase 3: Omnichannel Expansion, Infrastructure & Marketplace (Sprints 08 - 10) | Timeline: Weeks 15 - 22
* **Sprint 08: Omnichannel Engine (3 Weeks)**
  * Native connectors for Instagram DMs, Email, and Voice AI calling.
  * Channel continuity manager allowing lead conversations to jump between platforms seamlessly.
* **Sprint 09: VPS Dedication & Update Orchestration (2 Weeks)**
  * MyraOS Central Platform Console for client VPS provisioning and fleet monitoring.
  * Automated background `systemd` Update Agent pulling releases every 6 hours with automatic rollback capabilities.
* **Sprint 10: Vertical Playbooks & Agent Marketplace (3 Weeks)**
  * Pre-packaged niche playbooks (Healthcare/Clinics, Real Estate, Automotive, Financial Services).
  * Marketplace framework for custom agent personas and workflow distribution.

---

## 4. Multi-AI Agent System Architecture

The solution operates as an **orchestrated ecosystem of 6 specialized AI Agents**, ensuring modularity, clear separation of concerns, and cost/latency optimization:

```
                          +-----------------------------------+
                          |     Inbound Message / Event       |
                          +-----------------+-----------------+
                                            |
                                            v
+-----------------------------------------------------------------------------------+
|                              1. AI Sales SDR Agent                                |
|  - Conducts active conversation with Lead via Z-API / Instagram / Email / Voice   |
|  - Accesses RAG Knowledge Base, System Prompt Persona, and Lead Memories          |
|  - Invokes Tools: schedule_meeting(), update_stage(), add_lead_memory()          |
+-------------------+-------------------------------------------+-------------------+
                    |                                           |
                    v (Async Background)                        v (Async Background)
+---------------------------------------+   +---------------------------------------+
|       2. Memory Extraction Agent      |   | 3. Opportunity Scoring Classifier     |
| - Analyzes dialogue for facts, dates, |   | - Evaluates lead intent & sentiment   |
|   budget, objections, and preferences |   | - Updates DHS score & temperature     |
| - Saves structured records to DB      |   | - Triggers priority alert if Hot      |
+---------------------------------------+   +---------------------------------------+
                    |                                           |
                    +-------------------+-----------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                         4. Cadence & Re-Engagement Agent                          |
| - Triggered by ARQ scheduler on lead inactivity or rule breaches                  |
| - Generates contextual follow-up message using past conversation memories         |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                        5. Voice & Audio Processing Agent                          |
| - Transcribes inbound/outbound audio messages with Whisper API                    |
| - Formats text for downstream processing by Sales SDR Agent                       |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                      6. Post-Call Sales Coach & Analyst                           |
| - Runs post-conversation close/abandonment to evaluate SDR performance           |
| - Feeds analytical insights to Manager Brain & Revenue Brain                      |
+-----------------------------------------------------------------------------------+
```

### Agent Specifications & Model Selection Strategy

| Agent Name | Primary Function | Execution Triggers | Recommended LLM Model | Key Features |
|---|---|---|---|---|
| **1. AI Sales SDR Agent** | Direct lead engagement, qualification & booking | Inbound Lead message | **Claude 3.5 Sonnet / GPT-4o** (High stakes); **Gemini 1.5 Flash** (Standard) | Tool Calling, RAG vector retrieval, Persona adaptation, Copilot Mode suggestion. |
| **2. Memory Extraction Agent** | Long-term memory extraction | Async post-message batch | **Gemini 1.5 Flash-Lite / GPT-4o-mini** | Strict JSON Schema output, Pydantic validation, low cost. |
| **3. Opportunity & Intent Classifier** | Intent scoring & temperature assignment | Async post-turn | **Gemini 1.5 Flash / Claude 3.5 Haiku** | Fast classification, sentiment scoring, DHS adjustment. |
| **4. Cadence & Re-Engagement Agent** | Re-activating cold/dormant leads | ARQ scheduled timer | **Claude 3.5 Haiku / Gemini 1.5 Flash** | Contextual re-entry, anti-spam tone, memory integration. |
| **5. Voice Processing Agent** | Audio transcription & diarization | Inbound voice note | **Groq Whisper Large v3 / OpenAI Whisper** | High accuracy in PT-BR, audio-to-text formatting. |
| **6. Sales Coach & Revenue Analyst** | Sales performance audit & deal loss analysis | Conversation end / stage change | **Claude 3.5 Sonnet / Gemini 1.5 Pro** | Deep reasoning, sales technique scoring, managerial reports. |

---

## 5. Token Estimation, Forecasting & Pricing Model (FinOps)

To guarantee commercial viability and predictable margins, token consumption is modeled across single lead lifecycles and scaled to tenant operational profiles.

### 5.1 Token Consumption Baseline per Lead Lifecycle

Assuming an average lead lifecycle of **12 conversational turns** (inbound/outbound pairs):

```
Turn Context Breakdown (Sales SDR Agent):
- System Persona Prompt & Instructions: ~1,000 tokens
- Extracted Lead Memory & Context: ~500 tokens
- Relevant RAG Product Context: ~500 tokens
- Chat History (sliding window of last 6 turns): ~500 tokens
--------------------------------------------------------------
Average Input per turn:  2,500 Tokens
Average Output per turn: 250 Tokens
```

| Agent Task | Frequency per Lead | Tokens per Trigger | Total Tokens / Lead Lifecycle |
|---|---|---|---|
| **AI Sales SDR Agent** | 12 turns | 2,500 Input / 250 Output | **30,000 Input / 3,000 Output** |
| **Memory Extraction Agent** | 4 batches (every 3 turns) | 1,500 Input / 150 Output | **6,000 Input / 600 Output** |
| **Opportunity Classifier Agent** | 3 evaluations | 1,000 Input / 50 Output | **3,000 Input / 150 Output** |
| **Cadence Re-engagement Agent** | 2 re-engagement triggers | 2,000 Input / 200 Output | **4,000 Input / 400 Output** |
| **Sales Coach & Revenue Analyst** | 1 post-conversation run | 4,000 Input / 400 Output | **4,000 Input / 400 Output** |
| **Audio Processing (Whisper)** | 2 audio notes per lead | 2 minutes audio | **2.0 Audio Minutes** |
| **TOTAL LIFECYCLE PER LEAD** | — | — | **47,000 Input / 4,550 Output + 2 min Audio** |

---

### 5.2 Model Pricing Benchmark Matrix (Per 1 Million Tokens)

*Based on current August 2026 API provider pricing:*

| Provider / Model | Input Price / 1M Tokens | Output Price / 1M Tokens | Cached Input Price / 1M Tokens |
|---|---|---|---|
| **Google Gemini 1.5 Flash-Lite** | $0.0375 | $0.150 | $0.009 |
| **Google Gemini 1.5 Flash** | $0.075 | $0.300 | $0.018 |
| **Google Gemini 1.5 Pro** | $1.250 | $5.000 | $0.312 |
| **Anthropic Claude 3.5 Haiku** | $1.000 | $5.000 | $0.100 |
| **Anthropic Claude 3.5 Sonnet** | $3.000 | $15.000 | $0.300 |
| **OpenAI GPT-4o-mini** | $0.150 | $0.600 | $0.075 |
| **OpenAI GPT-4o** | $2.500 | $10.000 | $1.250 |
| **Whisper Audio API** | $0.006 / minute | — | — |

---

### 5.3 Monthly Cost Forecast by Business Tier

We compare two architectural deployment strategies:
- **Hybrid Cost-Optimized Stack**: Multi-tier model routing using *Gemini 1.5 Flash / Flash-Lite* for high-frequency extraction, classification, and standard sales dialogues, with *Claude 3.5 Haiku / Sonnet* for complex negotiations.
- **Premium Stack**: Utilizing *Claude 3.5 Sonnet* and *GPT-4o* across all conversational steps.

#### Tier 1: Small Business / Single Clinic (500 Leads / Month)
* Monthly Volume: 23.5 Million Input Tokens | 2.27 Million Output Tokens | 1,000 Audio Minutes

| Metric | Hybrid Cost-Optimized Stack | Premium Stack |
|---|---|---|
| **AI Sales SDR Agent Cost** | $2.02 (Gemini 1.5 Flash) | $56.25 (Claude 3.5 Sonnet) |
| **Memory Extraction Cost** | $0.16 (Gemini 1.5 Flash-Lite) | $4.95 (GPT-4o-mini) |
| **Opportunity Scoring Cost** | $0.13 (Gemini 1.5 Flash) | $2.47 (Claude 3.5 Haiku) |
| **Cadence & Coaching Cost** | $1.20 (Claude 3.5 Haiku) | $12.00 (Claude 3.5 Sonnet) |
| **Audio Transcription (Whisper)** | $6.00 | $6.00 |
| **TOTAL ESTIMATED MONTHLY COST** | **~$9.51 / month** | **~$81.67 / month** |

#### Tier 2: Mid-Market Organization (2,500 Leads / Month)
* Monthly Volume: 117.5 Million Input Tokens | 11.37 Million Output Tokens | 5,000 Audio Minutes

| Metric | Hybrid Cost-Optimized Stack | Premium Stack |
|---|---|---|
| **AI Sales SDR Agent Cost** | $10.10 (Gemini 1.5 Flash) | $281.25 (Claude 3.5 Sonnet) |
| **Memory Extraction Cost** | $0.80 (Gemini 1.5 Flash-Lite) | $24.75 (GPT-4o-mini) |
| **Opportunity Scoring Cost** | $0.65 (Gemini 1.5 Flash) | $12.35 (Claude 3.5 Haiku) |
| **Cadence & Coaching Cost** | $6.00 (Claude 3.5 Haiku) | $60.00 (Claude 3.5 Sonnet) |
| **Audio Transcription (Whisper)** | $30.00 | $30.00 |
| **TOTAL ESTIMATED MONTHLY COST** | **~$47.55 / month** | **~$408.35 / month** |

#### Tier 3: Enterprise / Large Agency (10,000 Leads / Month)
* Monthly Volume: 470 Million Input Tokens | 45.5 Million Output Tokens | 20,000 Audio Minutes

| Metric | Hybrid Cost-Optimized Stack | Premium Stack |
|---|---|---|
| **AI Sales SDR Agent Cost** | $40.40 (Gemini 1.5 Flash) | $1,125.00 (Claude 3.5 Sonnet) |
| **Memory Extraction Cost** | $3.20 (Gemini 1.5 Flash-Lite) | $99.00 (GPT-4o-mini) |
| **Opportunity Scoring Cost** | $2.60 (Gemini 1.5 Flash) | $49.40 (Claude 3.5 Haiku) |
| **Cadence & Coaching Cost** | $24.00 (Claude 3.5 Haiku) | $240.00 (Claude 3.5 Sonnet) |
| **Audio Transcription (Whisper)** | $120.00 | $120.00 |
| **TOTAL ESTIMATED MONTHLY COST** | **~$190.20 / month** | **~$1,633.40 / month** |

---

### 5.4 Token Optimization Strategies (FinOps Best Practices)

1. **Prompt Caching**: Enable Anthropic / Gemini prompt caching for static system prompts and product documentation. *Reduces input costs by up to 75-90% on repetitive turns.*
2. **Asynchronous Batch Extraction**: Do not run memory extraction on every single turn. Process in batches of 3-4 turns in background worker tasks using low-cost models (*Gemini 1.5 Flash-Lite*).
3. **Dynamic Context Compression**: Truncate chat history using sliding windows and rely on high-density extracted long-term memories instead of sending full raw transcripts.
4. **Model Tier Escalation (Smart Router)**: Route standard questions to lightweight models ($0.075/1M) and escalate to premium models ($3.00/1M) only when objection severity or lead temperature is high.

---

## 6. Technical Invariants & Governance

All developers and automated agents contributing code MUST adhere strictly to the following invariants established in `v0.2.0` and architectural decisions:

1. **App Factory Pattern**: No module singletons. Global state resides strictly on `app.state`.
2. **Strict Layering**: FastAPI route -> Domain `service.py` -> SQLModel tables. Database queries NEVER live in API routes.
3. **Multi-Tenant Defense-in-Depth**: Every database query MUST filter by `organization_id`. Cross-tenant record access attempts return generic `404 Not Found`. `organization_id` is extracted strictly from request `ContextVar` context, NEVER from user payload.
4. **Unified Error Envelopes**: Errors raise `AppError` subclasses resulting in standard JSON envelopes `{"error": {"code": ..., "message": ..., "details": ...}}`.
5. **Database Migration Standard**: Table models strictly reflect database state. All schema modifications require Alembic migration scripts (`alembic revision --autogenerate`).
6. **On-Premise Self-Containment**: Zero reliance on external CDNs or external static dependencies. Assets are vendored locally.
7. **Real-Time via SSE**: Use Server-Sent Events for unidirection server-to-client updates (no complex WebSockets).

---

## 7. Sign-off & Execution Next Steps

- **Immediate Action**: Proceed with **Sprint 02 — Lead Brain + Memory Brain** implementation in `~/AGENCIA/SDR/`.
- **Architectural Validation**: Verify cross-tenant isolation and Alembic migration scripts prior to pull request merge.
- **FinOps Monitoring**: Implement API token counter in FastAPI middleware to track exact real-world token spend per organization.
