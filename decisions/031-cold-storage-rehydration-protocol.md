# ADR-031: Protocolo de Reidratação de Leads Inativos do Cold Storage (Supabase/PostgreSQL) para o Hot Storage (Turso/libSQL)

* **Status**: ⚠️ **SUPERSEDED / DEPRECATED** (Substituído pelo [ADR-036: PostgreSQL Unificado](036-unified-postgresql-architecture.md) e [ADR-037: Supabase Platform Integration](037-supabase-managed-database-platform-integration.md))
* **Data**: Agosto 2026 (Depreciado em 11 de Agosto de 2026)
* **Autores**: Equipe de Arquitetura e Engenharia Backend (Revenue SDR OS)

---

> [!WARNING]
> **ESTE ADR FOI DEPRECIADO.**
> Com a aprovação do **ADR-036 (Option A: Arquitetura PostgreSQL Unificado)**, a plataforma abandonou o modelo de *Storage Tiering* (Turso Hot + PostgreSQL Cold). 
> Como todo o histórico conversacional, atração de leads, memórias e vetores RAG residem no mesmo banco de dados PostgreSQL 16+ unificado, **o Protocolo de Reidratação é totalmente desnecessário**, pois não há fragmentação ou movimentação de dados entre instâncias distintas.

---

## 1. Histórico do Problema (Obsoleto)

Anteriormente, o sistema previa o arquivamento de conversas com mais de 30 dias do Turso local para o PostgreSQL DW, exigindo que o `LeadService` reidratasse dados de volta ao Turso quando um lead inativo retornasse.

## 2. Nova Abordagem Sob o ADR-036

No PostgreSQL Unificado:
1. **Histórico Sempre Acessível**: Consultas SQL com filtro por `organization_id` e `lead_id` acessam diretamente todo o histórico do lead (recente ou histórico) em $< 10\text{ ms}$.
2. **Sem Latência de Re-inserção**: Zero queries adicionais de transporte de dados via rede entre bancos diferentes.
3. **Consistência RAG Única**: Vetores RAG em `pgvector` com HNSW indexam continuamente todas as memórias sem necessidade de sincronizar esquemas SQLite/Turso.
