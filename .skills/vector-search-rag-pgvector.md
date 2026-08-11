---
name: vector-search-rag-pgvector
description: |
  Carregue esta skill sempre que for implementar busca vetorial no Supabase (pgvector),
  chunking de documentos de conhecimento, geração de embeddings ou busca híbrida
  (RRF / Reciprocal Rank Fusion) para RAG.
version: 2.0.0
author: Antigravity (arquiteto)
license: Proprietary
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
metadata:
  hermes:
    tags: [rag, vector-search, pgvector, supabase, embeddings, rrf, hybrid-search, hnsw]
---

# Skill: Busca Vetorial, Hybrid Search & RAG (Supabase pgvector)

## 1. Princípio Fundamental

O **Revenue SDR OS** utiliza **Supabase Managed PostgreSQL 16+** com a extensão **`pgvector`** como a engine unificada para busca vetorial RAG (ADR-036, ADR-037).

1. **Embedding Standard**: Dimensão 1536 (`vector(1536)`), alinhada aos modelos `text-embedding-3-small` (OpenAI/Google).
2. **Índice HNSW**: Utiliza o índice Hierarchical Navigable Small World (`vector_cosine_ops`) para pesquisas vetoriais de ultra-baixa latência ($\le 15\text{ ms}$).
3. **Busca Híbrida (RRF)**: Combina Full-Text Search PostgreSQL (`tsvector`/BM25) com similaridade vetorial por cosseno via Reciprocal Rank Fusion (RRF).
4. **Isolamento Zero-Trust Multi-Tenant**: Pre-filtering obrigatório de `organization_id` em todas as consultas SQL e políticas RLS.

---

## 2. Padrão de Injeção de Vetores e Pré-Filtragem Multi-Tenant (Supabase)

**REGRA INEGOCIÁVEL**: Toda busca por vetores DEVE filtrar por `organization_id` ANTES ou durante a navegação no índice vetorial (Pre-Filtering).

```python
from sqlmodel import select, col
from sqlalchemy import text
from pgvector.sqlalchemy import Vector
from app.tenancy.context import current_organization

async def search_relevant_playbook_chunks(
    query_vector: list[float],
    top_k: int = 4,
    db_session: AsyncSession = None
) -> list[KnowledgeChunk]:
    org_id = current_organization.get().id
    
    # Supabase pgvector cosine distance: embedding <=> query_vector
    statement = (
        select(KnowledgeChunk)
        .where(KnowledgeChunk.organization_id == org_id)
        .where(KnowledgeChunk.status == "ativo")
        .order_by(KnowledgeChunk.embedding.cosine_distance(query_vector))
        .limit(top_k)
    )
    
    results = await db_session.exec(statement)
    return results.all()
```

---

## 3. Reciprocal Rank Fusion (RRF) — Algoritmo de Fusão Híbrida

O RRF combina o ranking da busca textual por palavra-chave (`tsvector`/BM25) com a busca por similaridade vetorial Cosseno (`pgvector`):

$$\text{RRF\_Score}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

onde $k = 60$ é uma constante de suavização, $M = \{\text{FTS}, \text{Vector}\}$ e $r_m(d)$ é a posição do documento $d$ no ranking do modelo $m$.

```python
def compute_rrf(
    fts_results: list[tuple[str, int]],   # [(doc_id, rank_fts)]
    vector_results: list[tuple[str, int]],# [(doc_id, rank_vector)]
    k: int = 60
) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}

    for doc_id, rank in fts_results:
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank))

    for doc_id, rank in vector_results:
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank))

    # Ordenar por score decrescente
    sorted_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_docs
```

---

## 4. Tabela de Schema no Alembic / SQLModel

```python
from sqlmodel import SQLModel, Field, Column
from pgvector.sqlalchemy import Vector
import uuid

class KnowledgeChunk(SQLModel, table=True):
    __tablename__ = "knowledge_chunks"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)
    title: str
    content: str
    embedding: list[float] = Field(sa_column=Column(Vector(1536)))
    status: str = Field(default="ativo")
```
