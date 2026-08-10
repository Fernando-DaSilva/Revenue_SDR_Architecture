# Sprint 07 — Relatório Pós-conversa + Manager/Revenue Brain

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 07 — RELATORIO POS-CONVERSA + MANAGER BRAIN                |
|   Status:  PRONTA PARA EXECUCAO (Hyper-Accelerated Hourly Micro-Sprints)|
|   Cadencia:Semana 6 (8 Micro-Sprints Horarias de 1h a 4h)             |
|   Owner:   Agente de codificacao                                     |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-07-manager-brain                           |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visão Geral

Criação da camada gerencial (para supervisores e gestores) agregando inteligência artificial na análise da equipe.
1. **Coach de Vendedores (Pos-conversa)**: IA analisa o transcript de uma conversa recém-finalizada (ou que deu loss/win) e emite um relatório destacando o que o SDR acertou e onde poderia melhorar.
2. **Manager Brain**: Perfil de IA voltado à supervisão. Identifica gargalos na operação.
3. **Dashboards Gerenciais**: Funil de vendas, CAC (se integrado a custo), ROI, Canais Vencedores, Tempo de primeira resposta (SLA).

---

## Schema Previsto (Alembic)

### Tabela: conversation_reviews
```sql
CREATE TABLE conversation_reviews (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    conversation_id VARCHAR NOT NULL,
    reviewer_type VARCHAR(20) NOT NULL, -- human, ai
    score INTEGER, -- 1 a 100
    strengths JSON NOT NULL,
    weaknesses JSON NOT NULL,
    coaching_notes TEXT,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

### Tabela: daily_metrics (Materialized View ou Tabela Agregada)
```sql
CREATE TABLE daily_metrics (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value FLOAT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
-- Índice único: (organization_id, date, metric_name)
```

---

## Endpoints e Serviços

- **Analytics API**: `GET /api/v1/analytics/funnel`, `GET /api/v1/analytics/performance`. Retornam dados agregados, preferencialmente pré-processados ou cacheados.
- **Review Service**: `POST /api/v1/conversations/{id}/review/ai` (acionado via job async ao fechar uma oportunidade).
- **Manager Insights**: API para expor conselhos da IA para o gerente.

---

---

## Alinhamento com Prototipos (`01_SDR_Prototype` e `02_ZAP_Prototype`)

- **01_SDR_Prototype**:
  - Command Center Overview (`commandCenterTab: 'overview'`): métricas de conversão de funil, ROI, CAC e métricas agregadas por período.
  - Data Management & Storage Tiering (`dataTab: 'tiering_retention'`): rotina de arquivamento para DW, gerenciamento de Cold Storage e expurgo do SQLite local.
- **02_ZAP_Prototype**:
  - Auto-Push de métricas pós-conversa e fechamento de atendimento no Inspector de Transmissão.

---

## SLAs de Performance (P95), Tiering de Dados & Segurança

- **Data Tiering & Arquivamento (ADR-015)**:
  - Turso Local (Hot Storage) retém leads ativos e conversas recentes.
  - Pipeline ETL/CDC diário (D-1) exporta históricos consolidados para PostgreSQL/Supabase (Cold Storage / DW com `pgvector`).
  - Job de Archiving purga registros antigos do Turso local mantendo buscas analíticas transparentes no DW.
- **Performance SLAs (ADR-019)**:
  - Leitura de Dashboards Agregados: **$< 50\text{ ms}$** (lendo do `daily_metrics` ou DW)
  - Execução do Sales Coach AI: **$< 2,500\text{ ms}$** (job assíncrono em background)
- **Segurança Zero-Trust (ADR-018)**:
  - Garantia de isolamento por `organization_id` nos dados agregados exportados para o Data Warehouse.
- **Garantia de Qualidade (ADR-020)**:
  - Cobertura de testes unitários do pipeline de métricas e ETL **> 85%**.
  - **100% de cobertura nos testes de isolamento analítico** (`tests/test_analytics_isolation.py`).
  - Migration Alembic das tabelas `conversation_reviews` e `daily_metrics` testadas via round-trip.

---

## Criterios de Aceitacao (Definition of Done)

```
[ ] Sales Coach AI gera relatório de avaliação da conversa (score, pontos fortes, fracas, dicas)
[ ] Pipeline ETL expurta conversas consolidadas para DW mantendo Turso leve (<10ms)
[ ] Dashboards gerenciais em GET /api/v1/analytics/funnel respondem em <50ms P95
[ ] Expurgo seguro de dados frios executado sem perder histórico no DW
[ ] Cross-tenant isolation 100% aprovado nos dados analíticos
```
