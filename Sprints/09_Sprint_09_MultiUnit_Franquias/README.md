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

---

## Alinhamento com Prototipos (`01_SDR_Prototype` e `02_ZAP_Prototype`)

- **01_SDR_Prototype**:
  - Theme Studio & Multi-Unit Configuration (`brandConfig`, `themeActiveTab: 'identidade_visual'`): sincronização de temas e branding por VPS cliente.
  - Painel de Gestão de Dados (`dataTab: 'backup_restore'`): status de backups locais e réplicas de sincronia.

---

## SLAs de Performance (P95) e Requisitos de Qualidade & Segurança

- **Performance SLAs (ADR-019)**:
  - Healthcheck de liveness da VPS (`GET /api/v1/health/`): **$< 10\text{ ms}$**
  - Checagem de updates pelo Update Agent: **$< 200\text{ ms}$**
- **Segurança Zero-Trust (ADR-018)**:
  - Autenticação mTLS ou API Key assinada entre o Update Agent (`systemd`) e o MyraOS Platform Console.
  - Verificação de integridade do pacote de release via Hash SHA-256 antes da execução.
- **Garantia de Qualidade (ADR-020)**:
  - Testes automatizados da rotina de Rollback e Migração Alembic em ambiente isolado.

---

## Criterios de Aceitacao (Definition of Done)

```
[ ] MyraOS Console lista e monitora saúde das VPSs clientes em tempo real
[ ] Update Agent via systemd consulta releases a cada 6h e executa pull de novas versões
[ ] Rollback automático funciona em 100% dos testes de falha simulada (banco corrompido ou app crash)
[ ] Healthcheck (/api/v1/health/) responde 200 OK pós-update autorizando o encerramento do deploy
```
