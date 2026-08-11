# ADR-022: Arquitetura Híbrida de RAG e Busca Vetorial (sqlite-vec + pgvector)

* **Status**: Atualizado (Unificado no Supabase `pgvector` por [ADR-036](036-unified-postgresql-architecture.md) e [ADR-037](037-supabase-managed-database-platform-integration.md))
* **Data**: Agosto 2026 (Atualizado em 2026-08-11)
* **Autores**: Equipe de Inteligência de IA e Arquitetura de Dados (Revenue SDR OS)

---

## 1. Contexto e Problema

O **Revenue SDR OS** necessita de capacidades de Recuperação Aumentada por Geração (RAG) em dois cenários distintos:
1. **Atendimento em Tempo Real (Hot RAG)**: O Agente SDR precisa buscar trechos de playbooks comerciais, FAQs de produtos, regras de precificação e memórias do lead em menos de **100ms** durante o diálogo no WhatsApp/Zap Copilot.
2. **Análise de Longo Prazo e Base de Conhecimento Central (Cold RAG / DW)**: O Manager Brain e o Revenue Brain precisam realizar buscas semânticas profundas em todo o histórico de conversas consolidadas, objeções recorrentes de mercado e documentos analíticos agregados.

Usar um banco de vetores externo (ex: Pinecone, Qdrant Cloud) quebraria o requisito inegociável de **Custo R$ 0,00**, **Zero Dependência de SaaS Externo** e **Auto-Contenção na VPS do Cliente** (ADR-004 / FOUNDATION.md).

---

## 2. Decisão Arquitetural

Adotar uma **Estratégia Híbrida de Busca Vetorial em Duas Camadas (Tiered RAG)** acoplada à arquitetura Hot/Cold Storage (ADR-015):

```
+-----------------------------------------------------------------------------------+
| CAMADA 1: HOT RAG (VPS Local — Single Tenant)                                     |
|  - Engine: `sqlite-vec` / `libsql-vector` integrado ao Turso / .db local          |
|  - Embeddings: Modelos ultraleves locais/API (text-embedding-3-small / BGE-micro)  |
|  - Foco: Trechos de Playbook Ativo, Objeções Rápidas, Memórias Ativas do Lead     |
|  - Latência: < 15ms | Custo: R$ 0,00 extra                                       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v (Sincronização assíncrona ETL D-1)
+-----------------------------------------------------------------------------------+
| CAMADA 2: COLD RAG & DW ANALÍTICO (PostgreSQL / Supabase Central)                  |
|  - Engine: `pgvector` com índice HNSW (Hierarchical Navigable Small World)        |
|  - Foco: Histórico global de conversas, clustering de objeções, RAG analítico      |
|  - Busca Híbrida: Reciprocal Rank Fusion (RRF) combinando BM25 / FTS + Vector    |
+-----------------------------------------------------------------------------------+
```

---

## 3. Detalhes Técnicos e Busca Híbrida (Hybrid Search)

### A. Busca Híbrida com Reciprocal Rank Fusion (RRF)
Nem toda busca comercial é pura semântica; códigos de produtos, nomes de modelos e valores exigem busca exata por palavra-chave (Full-Text Search).

O sistema combina obrigatoriamente:
- **FTS5 / PostgreSQL TsVector (BM25)**: Para termos numéricos, códigos, nomes próprios e jargões comerciais estritos.
- **Cosine Similarity (Vector Search)**: Para intenções, paráfrases e conceitos semânticos.
- **Fusão de Ranks (RRF)**:
  $$\text{RRF\_Score}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
  Onde $k=60$ e $r_m(d)$ é a posição do documento no ranking do método $m$.

### B. Especificação dos Modelos de Embedding
- **Dimensão Padrão**: 1536 dimensões (`text-embedding-3-small` / OpenAI) ou 1024 dimensões (`bge-m3`).
- **Normalização**: Vetores são obrigatoriamente normalizados para norma unitária ($L_2$) antes de persistir, permitindo uso acelerado do Produto Escalar (Dot Product) equivalente a Cosine Similarity.

---

## 4. Estrutura de Tabelas e Schema (SQLModel)

### Tabela de Chunking de Conhecimento (`playbook_chunks` / `knowledge_chunks`)

```python
class KnowledgeChunk(SQLModel, TenantMixin, TimestampMixin, table=True):
    __tablename__ = "knowledge_chunks"

    id: str = Field(default_factory=lambda: prefixed_id("chk"), primary_key=True)
    category: str = Field(index=True)  # playbook, faq, objection, product_info
    title: str
    content: str  # Texto bruto do chunk
    token_count: int
    
    # Payload de Metadados em JSON para filtragem por tenant/categoria
    metadata_json: dict = Field(default={}, sa_column=Column(JSON))
    
    # Campo vetorial (mapeado como BLOB no SQLite/libSQL via sqlite-vec ou Vector no pgvector)
    embedding_data: bytes | None = Field(default=None)
```

---

## 5. SLAs e Métricas FinOps

| Métrica | Meta | Estratégia de Mitigação |
|---|---|---|
| Latência Busca Hot RAG | $< 25\text{ ms}$ (P95) | sqlite-vec em memória/arquivo local na VPS |
| Top-K Chunks por Turno | $K \le 4$ | Evitar estouro de janela de contexto da LLM |
| Deduplicação de Embeddings | 100% | Hash MD5 do texto do chunk evita chamadas duplicadas de API de embedding |

---

## 6. Invariantes para Agentes de Codificação (AI Coding Guardrails)

1. **SEMPRE** filtrar a busca por vetor pelo `organization_id` da ContextVar ANTES de ranquear os vetores (pre-filtering), garantindo zero risco de vazamento de dados entre empresas.
2. **NUNCA** enviar transcrições inteiras para a busca vetorial sem passar pelo processo de Chunking (tamanho ideal por chunk: 250 a 500 tokens com overlap de 50 tokens).
3. **SEMPRE** armazenar o hash do conteúdo do chunk para evitar recálculo de embeddings desnecessário durante atualizações de cadastros ou playbooks.
