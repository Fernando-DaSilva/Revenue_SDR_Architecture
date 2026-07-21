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
3. **Observabilidade e Logs**: Implementação de logging estruturado (JSON), métricas (Prometheus) para monitoramento de latência da IA e taxas de entrega de mensagens.

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

---

## Decisões e Cuidados

- A segurança do Token do Google deve seguir as melhores práticas (criptografia em repouso no banco de dados se necessário, dependendo das políticas de compliance do SaaS).
- O Handoff IA -> Humano deve disparar notificações imediatas (que serão implementadas de forma Real-time na Sprint 06).
