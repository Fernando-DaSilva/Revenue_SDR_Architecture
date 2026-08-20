# Sprint 05 — Monitoramento + Handoff IA<->Humano + Sistema Interno Integrado de Calendário & Agendamentos

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 05 — MONITORAMENTO + HANDOFF + NATIVE CALENDAR OPERATIONS   |
|   Status:  PRONTA PARA EXECUCAO (Hyper-Accelerated Hourly Micro-Sprints)|
|   Cadencia:Semana 4 (8 Micro-Sprints Horarias de 1h a 4h)             |
|   Owner:   Agente de codificacao                                     |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-05-handoff-calendar                        |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visão Geral

Foco em instrumentar o sistema para operação em produção e empoderar as ferramentas da IA e do vendedor:
1. **Handoff Avançado**: Permitir que a IA solicite proativamente um vendedor humano quando detectar sentimentos negativos ou quando a complexidade da negociação exceder sua política de ação.
2. **Sistema Interno Integrado de Calendário & Agendamentos (ADR-040)**: Ferramenta nativa completa de agendamento de reuniões com Dashboard visual de Eventos, janelas de disponibilidade por vendedor (`host_availabilities`), tipos de reunião (`meeting_types`), controle de ciclo de vida (`scheduled`, `confirmed`, `completed`, `no_show`, `canceled`) e adaptadores de sincronização bidirecional/exportação para Google Calendar (OAuth2), Cal.com (API/Webhooks) e feeds iCalendar (`.ics`).
3. **Observabilidade e Logs (Conforme ADR-014)**: Implementação de logging estruturado (JSON), métricas (Prometheus) para monitoramento de latência da IA e taxas de entrega de mensagens, além do tracing com `request_id` cross-layer.

---

## Schema Previsto (Alembic / Supabase PostgreSQL ADR-037)

### Tabela: meeting_types
```sql
CREATE TABLE meeting_types (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    name VARCHAR(100) NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 30,
    buffer_minutes INTEGER NOT NULL DEFAULT 15,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

### Tabela: host_availabilities
```sql
CREATE TABLE host_availabilities (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    day_of_week INTEGER NOT NULL, -- 0=Domingo, 1=Segunda, ..., 6=Sábado
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Tabela: calendar_events (Substitui e expande a tabela meetings)
```sql
CREATE TABLE calendar_events (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,
    host_user_id VARCHAR NOT NULL,
    meeting_type_id VARCHAR,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'scheduled', -- scheduled, confirmed, completed, rescheduled, no_show, canceled
    location_url VARCHAR(500),
    ics_uid VARCHAR(255) UNIQUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id),
    FOREIGN KEY (host_user_id) REFERENCES users(id),
    FOREIGN KEY (meeting_type_id) REFERENCES meeting_types(id)
);
```

### Tabela: external_calendar_syncs (Google Cal, Cal.com, .ics)
```sql
CREATE TABLE external_calendar_syncs (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    provider VARCHAR(50) NOT NULL, -- google_calendar, cal_com, ics_feed
    external_calendar_id VARCHAR(255),
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    expires_at DATETIME,
    sync_token TEXT,
    last_synced_at DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Endpoints e Serviços

- **Internal Calendar API**: `GET /api/v1/calendar/events`, `POST /api/v1/calendar/events`, `POST /api/v1/calendar/events/{id}/reschedule`, `GET /api/v1/calendar/slots`
- **iCalendar Feed Export**: `GET /api/v1/calendar/export/{token}/feed.ics` (RFC 5545 compatível).
- **External Sync OAuth & Webhooks**: `GET /api/v1/integrations/google/authorize`, `GET /api/v1/integrations/google/callback`, e `POST /api/v1/integrations/calcom/webhook`.
- **Handoff API**: `POST /api/v1/conversations/{id}/handoff` (usado pela UI ou pela IA via Tool).
- **Métricas**: `GET /metrics` (para scraping do Prometheus). Configurado via Middleware ou dependência no nível do App.
- **Client Logs Ingestion**: `POST /api/v1/logs/client` (conforme especificado no ADR-014 para captação de métricas de frontend e erros client-side).

---

## Alinhamento com Prototipos (`01_SDR_Prototype` e `02_ZAP_Prototype`)

- **01_SDR_Prototype**:
  - Dashboard de Eventos e Agendamentos (`commandCenterTab: 'calendar'`): visão multi-agenda (Dia, Semana, Mês, Agenda), filtro de vendedores e controle de status de reunião.
  - Handoff Alerts (`sdrAgent: 'Alerta Handoff'`, `status: '🟡 Aguardando Operador'`): notificação visual de transbordo no Inbox.
  - Handoff Tab no Command Center (`commandCenterTab: 'handoffs'`): painel de controle e atribuição de leads para operadores humanos.
- **02_ZAP_Prototype**:
  - Handoff Status Badge (`👤 Human Mode` + congelamento temporário do bot durante atendimento humano).

---

## SLAs de Performance (P95) e Requisitos de Qualidade & Segurança

- **Performance SLAs (ADR-019)**:
  - Execução de Handoff IA<->Humano: **$< 50\text{ ms}$**
  - Busca de horários livres (`slots`) no Calendar Core Engine: **$< 35\text{ ms}$**
  - Agendamento de reunião via Tool da IA ou Dashboard: **$< 150\text{ ms}$**
  - Endpoint de ingestão de logs do client (`POST /api/v1/logs/client`): **$< 30\text{ ms}$**
- **Segurança Zero-Trust (ADR-018)**:
  - Criptografia dos `access_token` e `refresh_token` do Google Calendar e Cal.com em repouso.
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
