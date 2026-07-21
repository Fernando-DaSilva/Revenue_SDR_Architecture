# Sprint 09 — VPS Dedicada e Orquestração (Update Agent)

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 09 — VPS DEDICADA + UPDATE ORCHESTRATOR                    |
|   Status:  DOCUMENTADA                                              |
|   Owner:   Agente de codificacao / DevOps                            |
|   Quando:  Apos conclusao da Sprint 08                               |
|   Repo:    ~/AGENCIA/SDR/ (App) e MyraOS (Console)                   |
|   Branch:  feature/sprint-09-vps-orchestrator                        |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visão Geral

Conforme o **ADR-004**, a estratégia de infraestrutura SaaS é baseada em uma VPS dedicada por cliente, garantindo White-label profundo, isolamento de recursos e compliance com LGPD. Para escalar isso, precisamos automatizar a gestão.
1. **Platform Console (MyraOS)**: Sistema central onde novos tenants são cadastrados, e VPSs são provisionadas via Cloud Provider (DigitalOcean, Hetzner, AWS).
2. **Update Agent**: Um daemon rodando em cada VPS cliente que pergunta periodicamente à MyraOS: "Qual a versão que eu deveria rodar?".
3. **Rollback Automático**: Se o Update Agent puxar uma versão, falhar no Healthcheck ou no Alembic migrate, ele volta o binário/código para a versão anterior.

---

## Estrutura / Schema (MyraOS / Global)

*Atenção: A MyraOS possivelmente viverá em um repositório ou banco de dados separado do core do App dos clientes, embora compartilhem a definição de tenant (organization).*

### Tabela: tenant_instances (na MyraOS)
```sql
CREATE TABLE tenant_instances (
    id VARCHAR PRIMARY KEY,
    organization_slug VARCHAR NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    current_version VARCHAR(50) NOT NULL,
    target_version VARCHAR(50) NOT NULL,
    last_health_check DATETIME,
    status VARCHAR(20) NOT NULL, -- provisioning, running, updating, degraded
    created_at DATETIME NOT NULL
);
```

---

## Endpoints (MyraOS)

- `GET /api/v1/releases/latest`: Endpoint público (ou autenticado pelo Agent) para ver qual a última versão estável do Revenue SDR OS.
- `POST /api/v1/instances/{id}/status`: Endpoint que o Update Agent chama para avisar "Update bem-sucedido" ou "Rollback efetuado devido ao erro X".

---

## Lógica Crítica de Negócio

1. **Alembic e SQLite**: Como o app usa SQLite local, o Update Agent simplesmente copia o banco antes do `alembic upgrade`. Se der erro na migração ou o healthcheck falhar (ex: `GET /health/` retornar 500), ele deleta o banco corrompido, restaura o backup e reinicia o serviço.
2. **Self-Contained**: Para isso dar certo, o frontend **não pode** depender de CDN dinâmico. Todas as libs Javascript e CSS devem continuar *vendored* dentro do pacote (ADR-011).
