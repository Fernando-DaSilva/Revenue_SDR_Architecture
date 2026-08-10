# MASTER PLAN — Revenue SDR OS & Arquitetura Conversacional de IA

> **Plano Mestre Técnico de Engenharia para Desenvolvimento da Solução End-to-End**  
> **Elaborado por**: Equipe Multidisciplinar de Engenharia (Arquiteto de Enterprise, Líder de Sistemas de IA, Engenheiro Principal Backend/DevOps, Arquiteto de Segurança Zero-Trust e Diretor de QA)  
> **Versão**: 4.0.0 (Hyper-Accelerated Master Blueprint — Execução de Micro-Sprints Horárias & Topologia de 5 Streams em 2 Meses)  
> **Data**: Agosto de 2026  

---

## 1. Visão Geral e Estratégia Técnico-Operacional da Solução

O **Revenue SDR OS** é um **Sistema Operacional de Vendas Conversacional Autônomo** projetado sob uma mudança fundamental de paradigma: **a entidade raiz da automação comercial não é o cadastro estático do Lead nem um disparo de mensagens em massa, mas sim o Relacionamento (Conversa)** em evolução contínua através dos canais.

### Promessa e Valor Central
> *"Nunca mais perca um lead por falta de acompanhamento. O cliente compra agenda cheia."*

### Pilares Arquiteturais Principais
1. **Memória Persistente do Relacionamento**: Atributos extraídos no longo prazo (orçamento, tomadores de decisão, objeções, cronograma) armazenados por lead e fornecidos dinamicamente aos Agentes de IA.
2. **Ecossistema Multi-Agente de IA**: Agentes autônomos especializados atuando como SDRs seniores, extratores de memória em background, qualificadores de oportunidade, agendadores de cadência e coaches de vendas pós-conversa.
3. **Engine Omnichannel**: Continuidade fluida de conversa entre WhatsApp (Z-API), Instagram DM, E-mail e Voz.
4. **Arquitetura On-Premise-as-a-Service**: VPSs dedicadas single-tenant por organização, gerenciadas centralmente pelo **MyraOS Platform Console**, garantindo conformidade LGPD, zero compartilhamento de dados entre empresas e resiliência de execução local.
5. **Stack Auto-Contida**: Backend FastAPI (`app/main.py`) + SQLModel sobre banco embarcado Turso (libSQL) + Frontend hypermedia Jinja2/HTMX/Alpine.js (vendored) + streaming em tempo real SSE + Fila de Jobs Taskiq com `TenantTaskiqMiddleware` + Orquestração Instructor/Pydantic v2.
6. **Armazenamento de RAG em Duas Camadas & Re-hidratação**: Armazenamento local Turso (libSQL) + `sqlite-vec` ($< 15\text{ ms}$) com protocolo automático de Re-hidratação de Cold Storage (PostgreSQL `pgvector` DW) para leads recorrentes inativos (> 30d) (ADR-015, ADR-031).
7. **Integração WhatsApp & Conformidade Meta**: Enforcement rigoroso da Janela de Atendimento de 24 Horas do Meta via Templates HSM aprovados, com rate limiters por Token-Bucket (jitter de 3–5s) contra banimentos (ADR-032).
8. **Desenvolvimento Orientado a Agentes de IA & Micro-Sprints Horárias**: Repositório projetado com contratos estritos OpenAPI 3.1, schemas Pydantic v2, harness de verificação sub-minuto e execução autônoma em **Micro-Sprints Horárias (1h a 4h)** em tempo recorde de **2 Meses (60 Dias)** (ADR-026, ADR-033, ADR-034, ADR-035).

---

## 2. Estrutura da Equipe de Engenharia e Processo de Desenvolvimento

A execução desta solução exige uma equipe de engenharia multidisciplinar operando sob um processo de desenvolvimento padronizado e rigoroso.

### 2.1 Papéis e Responsabilidades Técnicas

| Papel | Responsabilidades Principais |
|---|---|
| **Arquiteto Principal de Enterprise & Software** | Topologia do sistema em 5 streams paralelas (ADR-035), invariantes de multi-tenancy Zero-Trust, evolução de schema Alembic Batch, orquestração de VPS. |
| **Engenheiro Líder de Sistemas de IA** | Arquitetura do sistema multi-agente LangGraph, engenharia de prompt, RAG híbrido (`sqlite-vec` + `pgvector`), Instructor/Pydantic schemas, fallback LLM Router com orçamento estrito de 900ms. |
| **Engenheiro Sênior de Backend e Dados** | Serviços de domínio FastAPI, integração Turso/libSQL local + Cold DW PostgreSQL, jobs assíncronos Taskiq com `TenantTaskiqMiddleware`, broker SSE. |
| **Engenheiro Sênior de Frontend e UX** | Implementação hypermedia Jinja2 + HTMX + Alpine.js (desconstruindo o HTML monolítico de 1.1MB do protótipo em templates Jinja2), sistema de presets de cores white-label, correção de memory leaks do Chart.js no Zap Copilot. |
| **Arquiteto de Segurança Zero-Trust & DevSecOps** | Automação de SAST/DAST, Secret Scanning, Zero-Trust multi-tenancy enforcement, conformidade OWASP Top 10 API Security, rotação de tokens Argon2id & PyJWT. |
| **Diretor de QA e Harness de IA** | Suíte de testes isolados cross-tenant com Pytest (>90% de cobertura), linting ruff, validação de migrations Alembic batch round-trip em $< 60\text{s}$ no CI/CD. |

### 2.2 Workflow Oficial do Agente de Codificação / Desenvolvedor em Micro-Sprints Horárias (ADR-033, ADR-034)

Para garantir consistência e evitar regressões no ciclo acelerado de 60 dias, todo agente de codificação ou desenvolvedor deve seguir o workflow em 6 camadas:

```
+-----------------------------------------------------------------------------------+
| 1. Leitura de Especificações & ADRs (FOUNDATION.md, ARCHITECTURE.md, Micro-Sprint Spec)|
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. Alterações de Banco & Migration (SQLModel -> alembic revision --autogenerate Batch)|
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 3. Implementação da Camada de Domínio (app/*/service.py com filtro organization_id)|
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 4. Schemas & Validação de Entrada (Pydantic / Instructor schemas com validação)    |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 5. Camada de Apresentação & API (FastAPI rotas finas / Jinja2 + HTMX pages)       |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 6. Harness Sub-Minuto (< 60s) (pytest >90% + tenant 100% + ruff + alembic round-trip)|
+-----------------------------------------------------------------------------------+
```

---

## 3. Roadmap Técnico de Execução Hyper-Acelerado (8 Semanas / 60 Dias)

O plano de desenvolvimento é estruturado em **8 Semanas (60 Dias / 2 Meses)** divididas em **5 Streams Paralelas Independentes (ADR-035)** executando **Micro-Sprints Horárias de 1h a 4h (ADR-033)**.

```
MÊS 1 (SEMANAS 1 A 4 / DIAS 1 A 28) — CORE ENGINE & IA MULTI-AGENTE
Semana 1 [Micro-Sprints 02.1 - 02.8] Lead Brain + Memory Brain + Taskiq Tenant (ADR-030)
Semana 2 [Micro-Sprints 03.1 - 03.8] Conversations + Opportunity Brain + Cadence Engine + Meta 24h HSM (ADR-032)
Semana 3 [Micro-Sprints 04.1 - 04.8] AI Sales Brain + Persistent AsyncSqliteSaver + Z-API WhatsApp Anti-Ban
Semana 4 [Micro-Sprints 05.1 - 05.8] Handoff Humano-IA + Desconstrução HTML Monólito + Google Calendar

MÊS 2 (SEMANAS 5 A 8 / DIAS 29 A 60) — REALTIME, OMNICHANNEL & SCALE
Semana 5 [Micro-Sprints 06.1 - 06.8] Transcrição Whisper + Fix Memory Leak Chart.js Zap + Stream SSE Real-Time
Semana 6 [Micro-Sprints 07.1 - 07.8] Análise Pós-Conversa + Data Warehouse ETL/CDC + Reidratação Cold DW (ADR-031)
Semana 7 [Micro-Sprints 08.1 - 08.8] Engine Omnichannel Completo (Instagram DM, E-mail, Agente de Voz)
Semana 8 [Micro-Sprints 09.1 - 10.8] Automação VPS Single-Tenant + MyraOS Console + Playbooks Verticais & Marketplace
```

---

## 4. Arquitetura do Sistema Multi-Agente de IA (LangChain & LangGraph)

O sistema opera como um **ecossistema orquestrado de 6 Agentes de IA especializados**, construído sobre **LangChain (`langchain-core`)** e **LangGraph (`langgraph`)**, garantindo grafos de estado persistentes em banco (`AsyncSqliteSaver`), separação clara de responsabilidades, resiliência via fallbacks (`with_fallbacks`) e rastreabilidade total no LangSmith (ADR-027, ADR-028, ADR-029):

```
                          +-----------------------------------+
                          |    Mensagem / Evento de Entrada   |
                          +-----------------+-----------------+
                                            |
                                            v (Taskiq Queue - Immediate HTTP 202)
+-----------------------------------------------------------------------------------+
|                              1. Agente AI Sales SDR                               |
|  - LangGraph StateGraph com AsyncSqliteSaver Checkpointer & Thread ID (Org:Lead)  |
|  - Acessa Hot RAG (sqlite-vec), Persona do System Prompt e Memórias do Lead       |
|  - Invoca Ferramentas @tool: schedule_meeting(), update_stage(), add_memory()     |
|  - Pausa via interrupt() para Human-in-the-Loop; escalonamento em 15 min          |
|  - Modelo resiliente with_fallbacks(): Gemini 2.5 (900ms) -> Sonnet -> GPT-4o-mini |
+-------------------+-------------------------------------------+-------------------+
                    |                                           |
                    v (Taskiq Background Task)                  v (Taskiq Background Task)
+---------------------------------------+   +---------------------------------------+
|      2. Agente Extrator de Memória     |   | 3. Classificador de Scoring e Intenção |
| - LCEL Chain + Instructor / Pydantic  |   | - LangChain with_structured_output()  |
| - Extrai orçamentos, objeções e fatos |   | - Atualiza score DHS (-100 a +100)    |
| - Salva registros de longo prazo      |   | - Dispara alertas de temperatura      |
+---------------------------------------+   +---------------------------------------+
                    |                                           |
                    +-------------------+-----------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                    4. Agente de Cadência e Reengajamento                          |
| - Grafo LangGraph disparado por Taskiq Scheduler em inatividade de leads          |
| - Valida Janela Meta 24h: Força uso de Templates HSM para leads inativos (> 24h)   |
| - Gera mensagem contextual de follow-up usando memórias passadas do Lead          |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                     5. Agente de Processamento de Voz e Áudio                     |
| - Transcreve mensagens de áudio inbound/outbound via Whisper API / Groq           |
| - Formata texto para processamento downstream no Grafo do AI Sales SDR            |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                     6. Coach de Vendas e Analista Pós-Conversa                    |
| - Grafo LangGraph de análise de encerramento para auditoria de performance SDR   |
| - Alimenta insights analíticos para os Brains Manager e Revenue em Cold DW        |
+-----------------------------------------------------------------------------------+
```

---

## 5. Arquitetura de Telemetria, Otimização de Contexto e FinOps Técnico

### 5.1 Instrumentação de Telemetria e Caching
1. **Middleware de Rastreamento de Tokens**: Registra `input_tokens`, `output_tokens` e `cached_tokens` rotulados com a ContextVar `organization_id`.
2. **Rate Limiting por Tenant**: Proteção contra abusos via `TenantRateLimiter` (ADR-025) com backend Valkey/Redis ou DiskCache local.
3. **Multi-Tier Caching**: Cache LRU em memória para temas White-Label e traduções, mitigando consultas desnecessárias ao banco.

---

## 6. SLAs de Performance e Orçamentos de Latência (P95)

| Componente / Camada | Operação | Latência Máxima (P95) | Estratégia de Otimização |
|---|---|---|---|
| **Banco Turso (libSQL)** | Query / Insert no `.db` local | **$< 10\text{ ms}$** | Arquivo local embarcado, índice composto `(organization_id, id)` |
| **API Core FastAPI** | Execução de rota HTTP | **$< 50\text{ ms}$** | Rotas finas assíncronas, camada de serviço, Jinja2 pré-compilado |
| **Stream SSE Real-Time** | Notificação de evento live | **$< 100\text{ ms}$** | Broker assíncrono em memória, zero polling |
| **Ingestão Webhook Z-API** | Recebimento de mensagem | **$< 50\text{ ms}$** | Retorno HTTP 202 imediato + delegação para fila Taskiq |
| **Hot RAG Vector Search** | Busca semântica local | **$< 15\text{ ms}$** | `sqlite-vec` / `libsql-vector` embarcado na VPS |
| **API Transcrição Whisper** | Transcrição de nota de áudio | **$< 1,500\text{ ms}$** | Endpoint otimizado Groq / OpenAI Whisper |
| **Agente AI Sales SDR** | Resposta conversacional | **$< 1,200\text{ ms}$** | System Prompt Caching + Gemini 2.5 Flash / Sonnet (orçamento estrito de 900ms por LLM) |

---

## 7. Invariantes Técnicos, Segurança Zero-Trust e Governança

1. **Padrão App Factory**: Sem singletons globais de módulo. O estado vive estritamente em `app.state`. App factory oficial Python 3.12+ FastAPI em `revenue_sdr_os` (substituindo mock Node `server.ts` legado).
2. **Camadas Estritas**: Rota FastAPI -> `service.py` de domínio -> Tabelas SQLModel. Queries SQL NUNCA vivem nas rotas da API.
3. **Defensa em Profundidade Multi-Tenant Zero-Trust**: Toda query DEVE filtrar por `organization_id`. Tentativas cross-tenant retornam `404 Not Found` genérico. O `organization_id` vem estritamente da `ContextVar`, NUNCA do payload do usuário.
4. **Propagação de Contexto Assíncrono (ADR-030)**: Workers do Taskiq utilizam o `TenantTaskiqMiddleware` para serializar e hidratar o `organization_id`, operando em banco de dados de fila separado (`taskiq_queue.db`). Execução sem tenant lança `RuntimeError` imediato.
5. **Reidratação de Dados Cold DW (ADR-031)**: O `LeadService` recupera automaticamente o histórico e memórias do Postgres DW para leads inativos que retornam após 30+ dias. Dimensões do modelo de embeddings (`text-embedding-3-small` 1536d) DEVEM ser idênticas entre `sqlite-vec` e `pgvector`.
6. **Proteção WhatsApp & Janela de 24h (ADR-032)**: Limitação de taxa Token-Bucket (jitter de 3–5s) e exigência de Templates HSM para disparos após 24 horas da última mensagem do lead.
7. **Hardening de Autenticação**: Hashes de senha via **Argon2id** (`pwdlib`), JWTs de sessão (PyJWT HS256) com claims `jti` únicos, cookies HttpOnly SameSite=Lax.
8. **Proteção de Dados & LGPD**: Soft deletes (`status='deletado'`), Anonimização de Dados Pessoais mediante solicitação, headers CSP (`script-src 'self'`).
9. **Envelope de Erros Unificado**: Erros lançam subclasses de `AppError` resultando no envelope JSON padrão `{"error": {"code": ..., "message": ..., "details": ...}}`.
10. **Versionamento Rígido com Alembic Batch**: Modelos de tabela refletem o banco. Alterações de schema exigem script de migration com `render_as_batch=True` e validação round-trip obrigatória (`upgrade head -> downgrade -1 -> upgrade head`).
11. **Auto-Contenção On-Premise**: Zero dependência de CDNs ou assets externos. Todos os assets estão embarcados localmente.
12. **Tempo Real via SSE**: Utilizar Server-Sent Events para atualizações unidirecionais do servidor para o cliente.
13. **Data & Vector Tiering (Hot/Cold Storage)**: Turso local com `sqlite-vec` mantém dados ativos; pipeline assíncrono Taskiq/ETL migra históricos para PostgreSQL/Supabase DW com `pgvector` HNSW.
14. **Orquestração de Agentes**: Workflows multi-agente usam **LangChain (`langchain-core`)** e **LangGraph (`StateGraph`)** com `with_fallbacks()` e checkpointers persistentes em banco `AsyncSqliteSaver` (ADR-027, ADR-028). Timeout do LLM primário limitado a **900ms** para preservar o SLA P95 de $< 1.2\text{ s}$. Estados suspensos em `interrupt()` disparam timer de escalonamento de 15 minutos.
15. **Refatoração de Protótipos & Qualidade**: Desconstruir o monólito `01_SDR_Prototype/index.html` (1.1MB) em templates Jinja2 (`app/web/templates/components/`). Corrigir memory leak do Chart.js no `02_ZAP_Prototype` mutando `chartInstance.data` e chamando `.update()`. Padronizar IDs de leads em UUIDv4.
16. **Observabilidade & Tracing**: Todos os grafos de agentes passam `tags` e `metadata` contendo `organization_id` e `lead_id` ao **LangSmith** (`LANGCHAIN_TRACING_V2=true`) para rastreamento e contabilidade FinOps (ADR-029).
17. **Matriz de Qualidade & AI Coding Guardrails**: Cobertura geral backend $> 85\%$, isolamento multi-tenant 100%, e execução mandatória do script de verificação pré-commit pelos agentes de IA (ADR-020, ADR-026).

---

## 8. Matriz de Qualidade, Integração Contínua e Operações de Deploy

### 8.1 Harness de Verificação Pré-Commit (Mandatório para Agentes de IA)

```bash
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=85  # Cobertura >85% + 100% isolamento
ruff check app/ tests/ scripts/ alembic/                              # Lint de código e segurança
ruff format --check app/ tests/ scripts/                              # Formatação estrita
alembic upgrade head && alembic downgrade -1 && alembic upgrade head    # Round-trip de migration
./start &                                                             # Teste de inicialização e saúde
curl http://127.0.0.1:8000/api/v1/health/
```

---

## 9. Próximos Passos de Execução

- **Ação Imediata**: Continuar a implementação técnica da **Sprint 02 — Lead Brain + Memory Brain + Propagação ContextVar Taskiq Tenant** no repositório `~/AGENCIA/SDR/`.
- **Validação Arquitetural**: Garantir a cobertura de testes de isolamento cross-tenant e propagação de contexto do `TenantTaskiqMiddleware`.
- **Instrumentação de Métricas**: Adicionar contadores de telemetria de tokens no middleware do FastAPI para observabilidade de uso desde a Sprint 02.
