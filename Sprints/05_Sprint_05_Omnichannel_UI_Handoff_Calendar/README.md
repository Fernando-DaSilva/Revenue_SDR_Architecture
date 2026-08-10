# Sprint 05 — Monitoramento + handoff IA<->Humano + Google Calendar

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 05 — MONITORAMENTO + HANDOFF + GOOGLE CALENDAR             |
|   Status:  DOCUMENTADA                                              |
|   Owner:   Agente de codificacao                                     |
|   Quando:  Apos conclusao da Sprint 04                               |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-05-handoff-calendar                        |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visão Geral

Foco em instrumentar o sistema para operação em produção e empoderar as ferramentas da IA e do vendedor:
1. **Handoff Avançado**: Permitir que a IA solicite proativamente um vendedor humano quando detectar sentimentos negativos ou quando a complexidade da negociação exceder sua política de ação.
2. **Integração Google Calendar**: Autenticação OAuth2 do tenant para que a IA possa agendar, reagendar ou cancelar reuniões de vendas usando Tools.
3. **Observabilidade e Logs (Conforme ADR-014)**: Implementação de logging estruturado (JSON), métricas (Prometheus) para monitoramento de latência da IA e taxas de entrega de mensagens, além do tracing com `request_id` cross-layer.

---

## Schema Previsto (Alembic)

### Tabela: calendar_integrations
```sql
CREATE TABLE calendar_integrations (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    provider VARCHAR(50) NOT NULL DEFAULT 'google',
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

### Tabela: meetings
```sql
CREATE TABLE meetings (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,
    title VARCHAR(200) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL, -- scheduled, completed, canceled, no_show
    external_event_id VARCHAR,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);
```

---

## Endpoints e Serviços

- **Calendar OAuth**: `GET /api/v1/integrations/google/authorize` e `GET /api/v1/integrations/google/callback`.
- **Handoff API**: `POST /api/v1/conversations/{id}/handoff` (usado pela UI ou pela IA via Tool).
- **Métricas**: `GET /metrics` (para scraping do Prometheus). Configurado via Middleware ou dependência no nível do App.
- **Client Logs Ingestion**: `POST /api/v1/logs/client` (conforme especificado no ADR-014 para captação de métricas de frontend e erros client-side).

---

---

## Alinhamento com Prototipos (`01_SDR_Prototype` e `02_ZAP_Prototype`)

- **01_SDR_Prototype**:
  - Handoff Alerts (`sdrAgent: 'Alerta Handoff'`, `status: '🟡 Aguardando Operador'`): notificação visual de transbordo no Inbox.
  - Handoff Tab no Command Center (`commandCenterTab: 'handoffs'`): painel de controle e atribuição de leads para operadores humanos.
- **02_ZAP_Prototype**:
  - Handoff Status Badge (`👤 Human Mode` + congelamento temporário do bot durante atendimento humano).

---

## SLAs de Performance (P95) e Requisitos de Qualidade & Segurança

- **Performance SLAs (ADR-019)**:
  - Execução de Handoff IA<->Humano: **$< 50\text{ ms}$**
  - Agendamento de reunião via Tool Google Calendar: **$< 500\text{ ms}$**
  - Endpoint de ingestão de logs do client (`POST /api/v1/logs/client`): **$< 30\text{ ms}$**
- **Segurança Zero-Trust (ADR-018)**:
  - Criptografia dos `access_token` e `refresh_token` do Google Calendar em repouso.
  - Rate-limiting estrito em `/api/v1/logs/client` para prevenir ataques de negação de serviço.
- **Garantia de Qualidade (ADR-020)**:
  - Cobertura de testes unitários do serviço de Handoff e Calendar **> 85%**.
  - **100% de cobertura nos testes de isolamento multi-tenant** (`tests/test_calendar_isolation.py`).
  - Validation round-trip de migration Alembic.

---

## Criterios de Aceitacao (Definition of Done)

```
[ ] Handoff IA -> Humano solicitado por sentiment analysis ou botão UI atualiza ai_mode=false com resumo de contexto
[ ] Integração Google Calendar permite autorização OAuth2 por tenant e agendamento de reuniões via AI Tool
[ ] Endpoint /metrics exporta métricas Prometheus (latência, chamadas LLM, status de handoff)
[ ] Endpoint /api/v1/logs/client ingere erros client-side com rate-limiting
[ ] Cross-tenant isolation 100% aprovado em pytest
```
