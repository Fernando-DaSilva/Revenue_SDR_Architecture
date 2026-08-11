# ADR-036: Adoção do PostgreSQL Unificado como Banco de Dados Único (Option A)

**Status:** Aprovado  
**Data:** 2026-08-11  
**Decisores:** Engenheiro de Software Principal, Arquiteto de Sistemas, Liderança Técnica  
**Tags:** `database`, `postgresql`, `pgvector`, `architecture`, `option-a`, `performance`

---

## Contexto e Problema

Anteriormente, o Revenue SDR OS utilizava uma arquitetura de armazenamento em duas camadas (*storage tiering*):
1. **Hot Storage**: Turso (libSQL/SQLite) para dados operacionais do tenant, chats ativos (<30 dias) e busca vetorial local via `sqlite-vec`.
2. **Cold Storage / DW**: PostgreSQL/Supabase com `pgvector` para histórico de conversas (>30 dias), RAG profundo e análises globais.

Embora a escolha do Turso/SQLite permitisse rápida portabilidade local em micro-instâncias VPS, ela introduziu severos desafios arquiteturais para o ambiente de produção com alto volume de mensagens no WhatsApp:
- **Contenção de Write Locks no SQLite**: Sob rajadas simultâneas de webhooks do WhatsApp (Z-API/Meta API) e execuções de background workers, requisições de escrita causavam erros `database is locked` (**RSK-03**).
- **Complexidade de Reidratação de Dados**: Leads inativos (>30 dias) exigiam o protocolo de reidratação (**ADR-031**) para buscar históricos do Cold DW de volta para o banco Hot local.
- **Fragmentação da Análise de Qualidade**: Análises em tempo real sobre a qualidade do atendimento, objeções, score do lead e aderência do SDR Agent ficavam divididas entre os dois bancos.

## Decisão

Adotar a **Option A: Arquitetura PostgreSQL Unificado** como a engine de banco de dados única para todo o ciclo de vida da aplicação (Hot Transactions, Histórico de Conversas, Filas, Checkpointer de Grafos de Estado e Busca Vetorial RAG).

### Especificações Técnicas:
1. **Engine Principal & Fornecedor de Plataforma**: Supabase Managed PostgreSQL (PostgreSQL 16+) operando com a extensão **`pgvector`** e pooler de conexões Supavisor (**ADR-037**).
2. **Isolamento Multi-Tenant**: Aplicação de defesa em profundidade com filtro obrigatório `organization_id` (injetado via `ContextVar` do FastAPI) em todas as tabelas e Row-Level Security (RLS) nativo do PostgreSQL no Supabase.
3. **Busca Vetorial & RAG Híbrido**: Eliminação da dependência de `sqlite-vec`. A busca vetorial utiliza `pgvector` com índices HNSW para embeddings de 1536 dimensões combinada com busca textual (`tsvector` / BM25) via Reciprocal Rank Fusion (RRF).
4. **LangGraph State Checkpointer**: Substituição do `AsyncSqliteSaver` pelo checkpointer persistente **`AsyncPostgresSaver`** (utilizando `asyncpg` / `psycopg3` no Supabase Postgres).
5. **Broker de Tarefas Taskiq**: O Taskiq utiliza PostgreSQL ou Valkey/Redis (`taskiq-redis` / `taskiq-pg`) com `TenantTaskiqMiddleware` (**ADR-030**), eliminando totalmente o banco local SQLite de fila (`taskiq_queue.db`).
6. **Depreciação do ADR-031**: O protocolo de reidratação torna-se totalmente obsoleto, pois todas as conversas ativas e históricas residem nativamente na mesma instância PostgreSQL.

---

## Consequências

### Positivas:
- **Zero Lock Contention**: Concorrência nativa MVCC do PostgreSQL suporta centenas de webhooks por segundo simultâneos sem travamentos de escrita.
- **Simplificação Operacional**: Única stack de migrações Alembic, único driver de banco, zero sincronização assíncrona entre bancos Hot/Cold.
- **Análise de Qualidade em Tempo Real**: Consultas analíticas (JSONB, Window functions, agregação cross-tenant) executam instantaneamente no mesmo banco de dados sobre todo o histórico.
- **SLA de Performance Garantido**: Latência de escrita/leitura P95 $\le 15\text{ ms}$ com PgBouncer/Supavisor, mantendo a API P95 $< 50\text{ ms}$.

### Negativas / Mitigações:
- **Exigência de Servidor/Instância PostgreSQL**: Requer conectividade com PostgreSQL (local Docker ou serviço gerenciado na nuvem) em vez de apenas um arquivo `.db` local. Mitigado via Supabase / Docker Compose no ambiente de desenvolvimento local.
