---
name: vector-search-rag-pgvector
description: |
  Carregue esta skill sempre que for implementar busca vetorial (sqlite-vec ou pgvector),
  chunking de documentos de conhecimento, geração de embeddings ou busca híbrida
  (RRF / Reciprocal Rank Fusion) para RAG.
version: 1.0.0
author: Hermes (arquiteto)
license: Proprietary
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
metadata:
  hermes:
    tags: [rag, vector-search, sqlite-vec, pgvector, embeddings, rrf, hybrid-search]
---

# Skill: Busca Vetorial, Hybrid Search & RAG (sqlite-vec + pgvector)

## 1. Princípio Fundamental

O **Revenue SDR OS** opera com uma **Arquitetura de RAG Híbrida em Duas Camadas**:
1. **Hot RAG (VPS Local)**: Utiliza `sqlite-vec` / `libsql-vector` na VPS dedicada para buscas ultrarrápidas ($< 15\text{ ms}$) em playbooks e memórias ativas.
2. **Cold RAG (Data Warehouse)**: Utiliza `pgvector` com índice HNSW no PostgreSQL central para buscas semânticas profundas.
3. **Busca Híbrida (RRF)**: Combina Full-Text Search (BM25 / FTS5) com busca por similaridade de cosseno via Reciprocal Rank Fusion.

---

## 2. Padrão de Injeção de Vetores e Pré-Filtragem Multi-Tenant

**REGRA INEGOCIÁVEL**: Toda busca por vetores DEVE filtrar por `organization_id` ANTES de calcular a similaridade vetorial (Pre-Filtering).

```python
from sqlmodel import select, col
from sqlalchemy import text

async def search_relevant_playbook_chunks(
    organization_id: str,
    query_vector: list[float],
    top_k: int = 4,
    db_session: AsyncSession = None
) -> list[KnowledgeChunk]:
    # Formatar vetor para query sqlite-vec ou pgvector
    vector_json = str(query_vector)
    
    # Pre-filtering por organization_id + Cosine Similarity
    statement = (
        select(KnowledgeChunk)
        .where(KnowledgeChunk.organization_id == organization_id)
        .where(KnowledgeChunk.status == "ativo")
        # Exemplo para sqlite-vec / pgvector
        .order_by(text(f"vec_distance_cosine(embedding_data, '{vector_json}') ASC"))
        .limit(top_k)
    )
    
    results = await db_session.exec(statement)
    return results.all()
```

---

## 3. Reciprocal Rank Fusion (RRF) — Algoritmo de Fusão Híbrida

```python
def reciprocal_rank_fusion(
    fts_results: list[dict],
    vector_results: list[dict],
    k: int = 60
) -> list[dict]:
    scores = {}
    
    # Processar Ranks do FTS
    for rank, doc in enumerate(fts_results):
        doc_id = doc["id"]
        if doc_id not in scores:
            scores[doc_id] = {"doc": doc, "score": 0.0}
        scores[doc_id]["score"] += 1.0 / (k + rank + 1)
        
    # Processar Ranks do Vetor
    for rank, doc in enumerate(vector_results):
        doc_id = doc["id"]
        if doc_id not in scores:
            scores[doc_id] = {"doc": doc, "score": 0.0}
        scores[doc_id]["score"] += 1.0 / (k + rank + 1)
        
    # Ordenar por score RRF decrescente
    sorted_docs = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
    return [item["doc"] for item in sorted_docs]
```

---

## 4. Anti-Patterns (NUNCA faça)

```
[X] Fazer busca vetorial sem filtrar organization_id primeiro -> Vazamento cross-tenant fatal!
[X] Enviar N chunks brutos no prompt excedendo a janela        -> Limite rígido: top_k <= 4
[X] Recalcular embedding de texto inalterado                  -> Use hash MD5 para deduplicação
[X] Usar tamanho de chunk > 1000 tokens                       -> Chunk ideal: 250 a 500 tokens
```

---

## 5. Checklist de Validação

- [ ] A consulta vetorial inclui o filtro `organization_id == current_organization.id`
- [ ] O limite de chunks retornados (`top_k`) é $\le 4$
- [ ] O hash MD5 do conteúdo é verificado antes de chamar a API de embeddings
- [ ] Os vetores são normalizados ($L_2$) antes de persistir
