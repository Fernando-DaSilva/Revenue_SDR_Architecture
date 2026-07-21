# Sprint 07 — Relatório Pós-conversa + Manager/Revenue Brain

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 07 — RELATORIO POS-CONVERSA + MANAGER BRAIN                |
|   Status:  DOCUMENTADA                                              |
|   Owner:   Agente de codificacao                                     |
|   Quando:  Apos conclusao da Sprint 06                               |
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

## Decisões Críticas

- As queries do Dashboard não podem travar a instância (especialmente usando SQLite no MVP). Avaliar se criamos jobs periódicos (CRON via Fila) que calculam e agregam os dados nas tabelas `daily_metrics` de madrugada, mantendo o App principal muito leve de leitura.
