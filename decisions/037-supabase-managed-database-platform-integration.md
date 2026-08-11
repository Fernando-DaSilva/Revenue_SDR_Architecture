# ADR-037: Integração com a Plataforma Supabase PostgreSQL Gerenciado

**Status:** Aprovado  
**Data:** 2026-08-11  
**Decisores:** Engenheiro de Software Principal, Arquiteto de Sistemas, Liderança Técnica  
**Tags:** `database`, `supabase`, `postgresql`, `pgvector`, `supavisor`, `rls`, `architecture`

---

## Contexto e Problema

Com a aprovação da **Option A (ADR-036)**, o Revenue SDR OS unificou seu modelo de banco de dados em uma única engine **PostgreSQL 16+**, eliminando a antiga arquitetura de duas camadas (*Hot Turso/libSQL + Cold DW*) e o protocolo de reidratação de dados (**ADR-031**).

Para a implantação em produção (em ambientes single-tenant VPS ou multi-tenant SaaS), tornou-se necessário definir o **fornecedor oficial da plataforma gerenciada de banco de dados**. A escolha da plataforma deve suportar:
1. Concorrência extrema em rajadas de webhooks do WhatsApp (Z-API / Meta API) via pooling de conexões otimizado.
2. Defesa em profundidade Zero-Trust nativa na engine de dados via Row-Level Security (RLS).
3. Extensionismo para busca vetorial RAG (`pgvector` com HNSW 1536d) e busca textual por palavra-chave (`tsvector`/BM25).
4. Persistência de grafos de estado de IA com checkpointer `AsyncPostgresSaver` do LangGraph.
5. Suporte a armazenamento de mídias/áudios (WhatsApp/Whisper) e publicação de eventos em tempo real (CDC/WebSockets).

## Decisão

Adotar o **Supabase** como a plataforma oficial e fornecedor gerenciado da camada de banco de dados PostgreSQL para o Revenue SDR OS.

### Especificações Técnicas de Integração com Supabase:

1. **Engine & Provider de Banco de Dados**:
   - **Instância**: Supabase Managed PostgreSQL (PostgreSQL 16+).
   - **Compatibilidade Local**: No ambiente de desenvolvimento local, o ecossistema é replicado usando a Supabase CLI (`supabase start` via Docker Compose).

2. **Gerenciamento de Conexões & Pooler Supavisor**:
   - **Modo Transação (Porta 6543)**: Utilizado por padrão para as conexões da aplicação FastAPI, webhooks e workers assíncronos Taskiq via Supavisor pooler, maximizando a capacidade de conexões simultâneas com `sslmode=require`.
   - **Modo Sessão / Conexão Direta (Porta 5432)**: Reservado exclusivamente para execução de migrações DDL via Alembic (`alembic upgrade head`) e operações administrativas de alteração de esquema.

3. **Isolamento Multi-Tenant & Row-Level Security (RLS)**:
   - Defesa em profundidade combinando a camada de aplicação FastAPI (`ContextVar` `current_organization` + `TenantMixin`) com políticas nativas de **PostgreSQL Row-Level Security (RLS)** no Supabase.
   - Tabelas operacionais configuradas com `ALTER TABLE <tabela> ENABLE ROW LEVEL SECURITY;` utilizando a variável de sessão do tenant (`app.current_organization_id`) ou JWT claims (`auth.jwt()`).

4. **Busca Vetorial & Hybrid RAG (`pgvector` + HNSW)**:
   - Ativação nativa da extensão `pgvector` (`CREATE EXTENSION IF NOT EXISTS vector;`).
   - Tabela de embeddings formatada com `vector(1536)` (modelos `text-embedding-3-small` OpenAI / Google Gemini).
   - Índice HNSW (`vector_cosine_ops`) garantindo buscas vetoriais ultrarrápidas ($\le 15\text{ ms}$) combinadas com `tsvector` e Reciprocal Rank Fusion (RRF). Eliminação total do `sqlite-vec`.

5. **LangGraph State Checkpointer Persistente**:
   - Utilização do checkpointer **`AsyncPostgresSaver`** conectado ao Supabase PostgreSQL, garantindo resiliência de estados de conversas e pontos de pausa `interrupt()` para handoff humano.

6. **Ecossistema Supabase (Storage & Realtime)**:
   - **Supabase Storage**: Buckets S3-compatible gerenciados para armazenar arquivos de áudio do WhatsApp, transcrições do Whisper e mídias de conversas.
   - **Supabase Realtime**: Utilização opcional do CDC / WebSockets do Supabase para broadcast instantâneo de eventos de alteração no estado dos leads no Inbox.

7. **Migrações e Evolução de Schema**:
   - Pipeline de migrações gerenciado via **Alembic** (`alembic/env.py`) com dialeto PostgreSQL nativo e compatível com a Supabase CLI (`supabase migration` / `supabase db push`).
   - Depreciação completa do modo batch (`render_as_batch=True`) do SQLite (**ADR-024**).

---

## Consequências

### Positivas:
- **Infraestrutura Pronta para Escala**: O Supabase resolve pooling de conexões (Supavisor), backups automáticos, replicação e segurança de forma nativa.
- **Desenvolvimento Consistente**: O mesmo banco PostgreSQL roda localmente (`supabase start`) e em produção na nuvem Supabase.
- **RAG & IA em 1 Lugar**: embeddings `pgvector` e checkpointer LangGraph residem no mesmo banco do core do sistema.
- **Concorrência Altíssima**: Responde perfeitamente a rajadas do WhatsApp sem *lock contention*.

### Negativas / Mitigações:
- **Dependência de Driver PostgreSQL (asyncpg/psycopg3)**: O app requer drivers assíncronos de Postgres configurados. Mitigado com inclusão no `pyproject.toml` e `.env.example`.
