# MASTER PLAN — Revenue SDR OS & AI Conversational Architecture

> **Executive & Technical Blueprint for End-to-End Solution Development**  
> **Prepared by**: Engineering Taskforce (Software Architects, AI Engineers, Systems Developers & FinOps Engineers)  
> **Version**: 2.2.0 (Post v0.2.0 Baseline — Software Engineering Execution Plan for AI-Agent Development)  
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
5. **Self-Contained Tech Stack**: FastAPI backend + SQLModel over Turso (libSQL) embedded databases + Jinja2/HTMX/Alpine.js hypermedia frontend + SSE real-time streaming + Taskiq job queue + Instructor/Pydantic v2 orchestration.
6. **AI-Agent Driven Development Protocol**: Machine-readable OpenAPI 3.1 contracts, strict Pydantic schemas, and automated test harnesses for autonomous AI coding agents (ADR-026).

---

## 2. Engineering Team Structure & Roles

Executing this solution requires a disciplined, multi-disciplinary engineering taskforce:

| Role | Core Responsibilities |
|---|---|
| **Principal Software Architect** | System topology, Zero-Trust multi-tenancy invariants, Alembic Batch schema evolution, VPS orchestration. |
| **Lead AI Systems Engineer** | Multi-agent framework design, prompt engineering, Hybrid RAG pipelines (sqlite-vec + pgvector), Instructor Pydantic schemas, LLM fallback Router. |
| **Senior Backend & Data Engineer** | FastAPI domain services, Turso/libSQL local DB + PostgreSQL DW, Taskiq background jobs, SSE broker. |
| **Senior Frontend & UX Engineer** | Jinja2 + HTMX + Alpine.js implementation, white-label color preset translation system, ZAP Copilot Prototype integration. |
| **FinOps & Cost Optimization Specialist** | Token consumption forecasting, multi-tier LLM routing, System Prompt Caching, Tenant Rate Limiting. |
| **QA & AI Coding Guardrails Engineer** | Pytest cross-tenant isolation test suite, ruff linting, Alembic migration verification, automated AI agent pre-commit harness (ADR-026). |

---

## 3. Comprehensive Phased Roadmap & Timeframe Estimation

```
Sprint 00 [DONE] Architecture & Governance
Sprint 01 [DONE] Foundation + Auth + White-Label (v0.2.0 Baseline)
Sprint 01.5 [DONE] Standalone ZAP Copilot Prototype (02_ZAP_Prototype)
Sprint 02 [W1-W2] Lead Brain + Memory Brain
Sprint 03 [W3-W4] Conversations + Opportunity Brain + Cadence Engine + Taskiq
Sprint 04 [W5-W7] AI Sales Brain + Instructor + Z-API WhatsApp Integration
Sprint 05 [W8-W9] Human-AI Handoff + Google Calendar Integration + Observability
Sprint 06 [W10-W11] Audio Whisper Transcription + DHS Chart + SSE Real-Time Stream
Sprint 07 [W12-W14] Post-Call Analysis + Data Warehouse ETL/CDC + Cold RAG pgvector
Sprint 08 [W15-W17] Omnichannel Engine (Instagram DM, Email, Voice Agent)
Sprint 09 [W18-W19] Single-Tenant VPS Automation + MyraOS Update Orchestrator
Sprint 10 [W20-W22] Vertical Playbooks + Tribo Agent Marketplace
```

---

## 4. Multi-AI Agent System Architecture (LangChain & LangGraph)

The solution operates as an **orchestrated ecosystem of 6 specialized AI Agents**, built on **LangChain (`langchain-core`)** and **LangGraph (`langgraph`)**, ensuring stateful graph workflows (`StateGraph`), multi-tier model fallbacks (`with_fallbacks`), and full trace visibility in LangSmith (ADR-027, ADR-028, ADR-029):

```
                          +-----------------------------------+
                          |     Inbound Message / Event       |
                          +-----------------+-----------------+
                                            |
                                            v (Taskiq Queue - Immediate HTTP 202)
+-----------------------------------------------------------------------------------+
|                              1. AI Sales SDR Agent                                |
|  - LangGraph StateGraph with MemorySaver Checkpointer & Thread ID per (Org:Lead)  |
|  - Accesses Hot RAG (sqlite-vec), System Prompt Persona, and Lead Memories        |
|  - Invokes @tool functions: schedule_meeting(), update_stage(), add_memory()      |
|  - Pauses via interrupt() for Human-in-the-Loop on sensitive actions              |
|  - Resilient model routing: Gemini 2.5 Flash -> Sonnet 3.5 -> GPT-4o-mini         |
+-------------------+-------------------------------------------+-------------------+
                    |                                           |
                    v (Taskiq Background Task)                  v (Taskiq Background Task)
+---------------------------------------+   +---------------------------------------+
|       2. Memory Extraction Agent      |   | 3. Opportunity Scoring Classifier     |
| - LCEL Chain + Instructor / Pydantic  |   | - LangChain with_structured_output()  |
| - Analyzes dialogue for facts, dates, |   | - Evaluates lead intent & sentiment   |
|   budget, objections, and preferences |   | - Updates DHS score & temperature     |
+---------------------------------------+   +---------------------------------------+
                    |                                           |
                    +-------------------+-----------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                         4. Cadence & Re-Engagement Agent                          |
| - LangGraph state graph triggered by Taskiq scheduler on lead inactivity          |
| - Generates contextual follow-up message using past conversation memories         |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                        5. Voice & Audio Processing Agent                          |
| - Transcribes inbound/outbound audio messages with Groq / OpenAI Whisper API      |
| - Injects transcribed text directly into the LangGraph state message history      |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                      6. Post-Call Sales Coach & Analyst                           |
| - LangGraph analysis graph run on conversation close to evaluate SDR quality     |
| - Feeds analytical insights to Manager Brain & Revenue Brain in Cold DW           |
+-----------------------------------------------------------------------------------+
```

---

## 5. Performance SLAs & Latency Budgets (P95 Thresholds)

| Component / Layer | Operation | Latency Budget (P95) | Optimization Strategy |
|---|---|---|---|
| **Turso (libSQL) DB** | Local `.db` Query / Insert | **$< 10\text{ ms}$** | Embedded local file, composite index `(organization_id, id)` |
| **FastAPI Core API** | Route Request Execution | **$< 50\text{ ms}$** | Thin async routes, service layer pattern, Jinja2 pre-compiled |
| **SSE Event Stream** | Live Event Notification | **$< 100\text{ ms}$** | Async memory broker, zero polling overhead |
| **Z-API Ingest Webhook** | Inbound Message Processing | **$< 50\text{ ms}$** | Immediate HTTP 202 return + Taskiq background queue dispatch |
| **Hot RAG Vector Search** | Local Semantic Search | **$< 15\text{ ms}$** | `sqlite-vec` / `libsql-vector` embedded in VPS |
| **Whisper Audio API** | Audio Note Transcription | **$< 1,500\text{ ms}$** | Groq / OpenAI fast audio transcription endpoint |
| **AI Sales SDR Agent** | Conversational Turn Response | **$< 1,200\text{ ms}$** | System Prompt Caching + LangChain + Gemini 2.5 Flash / Sonnet router |

---

## 6. Zero-Trust Security, Quality Assurance & Technical Invariants

1. **App Factory Pattern**: No module singletons. Global state resides strictly on `app.state`.
2. **Strict Layering**: FastAPI route -> Domain `service.py` -> SQLModel tables. Database queries NEVER live in API routes.
3. **Zero-Trust Multi-Tenant Defense**: Every database query MUST filter by `organization_id`. Cross-tenant record access attempts return generic `404 Not Found`. `organization_id` is extracted strictly from request `ContextVar` context, NEVER from user payload.
4. **Auth Hardening**: Password hashing via **Argon2id** (`pwdlib`), session JWTs (PyJWT HS256) with unique `jti` claims, HttpOnly SameSite=Lax cookies.
5. **Data Protection & LGPD**: Soft deletes (`status='deletado'`), Personal Data Anonymization on request, CSP headers (`script-src 'self'`).
6. **Unified Error Envelopes**: Errors raise `AppError` subclasses resulting in standard JSON envelopes `{"error": {"code": ..., "message": ..., "details": ...}}`.
7. **Database Migration Standard**: Table models strictly reflect database state. All schema modifications require Alembic Batch migration scripts (`render_as_batch=True`) with mandatory round-trip validation (`upgrade head -> downgrade -1 -> upgrade head`).
8. **On-Premise Self-Containment**: Zero reliance on external CDNs or external static dependencies. Assets are vendored locally.
9. **Real-Time via SSE**: Use Server-Sent Events for unidirectional server-to-client updates.
10. **Storage & Vector Tiering (Hot/Cold DW)**: Turso local file with `sqlite-vec` maintains active data; Taskiq/ETL pipeline exports consolidated conversations to PostgreSQL/Supabase DW with `pgvector` HNSW.
11. **Agent Orchestration**: Multi-agent workflows use **LangChain (`langchain-core`)** and **LangGraph (`StateGraph`)** with `with_fallbacks()` and DB checkpointers. High-stakes actions trigger `interrupt()` for human approval in Zap Copilot (`02_ZAP_Prototype`) (ADR-027, ADR-028).
12. **Observability & Tracing**: All agent graphs pass `tags` and `metadata` containing `organization_id` and `lead_id` to **LangSmith** (`LANGCHAIN_TRACING_V2=true`) for tracing and FinOps accounting (ADR-029).
13. **QA & AI Coding Harness**: Minimum **> 85% overall backend coverage**, **100% tenant isolation test coverage**, and mandatory pre-commit verification execution by AI coding agents.

---

## 7. Sign-off & Execution Next Steps

- **Immediate Action**: Proceed with **Sprint 02 — Lead Brain + Memory Brain** implementation in `~/AGENCIA/SDR/`.
- **Architectural Validation**: Verify cross-tenant isolation and Alembic Batch migration scripts prior to pull request merge.
- **FinOps Monitoring**: Implement API token counter in FastAPI middleware to track exact real-world token spend per organization.
