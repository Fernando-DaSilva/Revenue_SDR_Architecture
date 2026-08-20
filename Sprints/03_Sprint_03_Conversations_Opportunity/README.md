# Sprint 03 — Conversations + Opportunity + Cadence

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 03 — CONVERSATIONS + OPPORTUNITY + CADENCE                 |
|   Status:  PRONTA PARA EXECUCAO (Hyper-Accelerated Hourly Micro-Sprints)|
|   Cadencia:Semana 2 (8 Micro-Sprints Horarias de 1h a 4h)             |
|   Owner:   Agente de codificacao                                     |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-03-conversations                           |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visão Geral

Esta sprint eleva o sistema para além do simples cadastro de leads, introduzindo o motor central de conversações e oportunidades.
1. **Conversations**: O núcleo onde as interações ocorrem. Um Lead torna-se um participante de uma ou mais conversas.
2. **Messages & Events**: Uma tabela central de eventos (`events`) que generaliza a timeline e armazena o histórico e ações relevantes.
3. **Opportunity Brain**: Sistema de *scoring* dinâmico que avança ou recua leads baseado nos eventos (ex: abriu mensagem, respondeu, demonstrou intenção).
4. **Cadence Engine**: Máquina de estados responsável pelas réguas de relacionamento, usando uma fila leve para jobs assíncronos (arquitetura base para disparos agendados).

---

## Schema Previsto (Alembic)

*Nota: Models devem herdar de `TenantMixin` e `TimestampMixin`.*

### Tabela: conversations
```sql
CREATE TABLE conversations (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- active, archived, won, lost
    channel VARCHAR(50) NOT NULL, -- zap, instagram, email
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);
```

### Tabela: messages
```sql
CREATE TABLE messages (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    conversation_id VARCHAR NOT NULL,
    direction VARCHAR(10) NOT NULL, -- inbound, outbound
    content TEXT,
    content_type VARCHAR(20) NOT NULL, -- text, image, audio
    status VARCHAR(20) NOT NULL, -- sent, delivered, read, failed
    created_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

### Tabela: cadence_steps
```sql
CREATE TABLE cadence_steps (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,
    playbook_id VARCHAR,
    current_step INTEGER NOT NULL DEFAULT 1,
    next_execution_at DATETIME,
    status VARCHAR(20) NOT NULL, -- pending, active, completed, paused
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);
```

### Tabelas: follow_up_rules & follow_up_schedules (ADR-039)
```sql
CREATE TABLE follow_up_rules (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    scenario_type VARCHAR(50) NOT NULL, -- objection_recovery, winback, agenda_reminder, custom
    objection_tag VARCHAR(50),          -- price, timing, competitor, silent
    delay_hours INTEGER NOT NULL DEFAULT 24,
    target_channel VARCHAR(50) NOT NULL DEFAULT 'zap',
    template_id VARCHAR,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE follow_up_schedules (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,
    rule_id VARCHAR NOT NULL,
    scheduled_for DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, executed, canceled, skipped
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id),
    FOREIGN KEY (rule_id) REFERENCES follow_up_rules(id)
);
```

---

## Endpoints e Serviços

- **Conversations API**: `GET /api/v1/conversations`, `POST /api/v1/conversations/{id}/messages`
- **Cadence & Follow-up Service**: Lógica de enfileiramento de `jobs` assíncronos no Taskiq (ADR-030). Processamento dinâmico de recuperação de objeções, cadências por temperatura e disparo de templates HSM respeitando a Janela Meta 24h (ADR-032, ADR-039).
- **Scoring Engine**: Função que avalia `lead_timeline_events` e atualiza o campo `score` (e possivelmente a fase do funil) do lead na tabela `leads`.


---

## Alinhamento com Prototipos (`01_SDR_Prototype` e `02_ZAP_Prototype`)

- **01_SDR_Prototype**:
  - Multichannel Live Chat Inbox (`inboxTab: 'multichannel'`): interface de listagem e filtro de conversas por canal (Zap, Email, Voice).
  - Motor de Cadências (`cadences`): visualização de réguas ativas, passos executados e agendamentos.
- **02_ZAP_Prototype**:
  - Central Chat Stream: renderização de mensagens inbound e outbound com estados (`sent`, `delivered`, `read`).

---

## SLAs de Performance (P95) e Requisitos de Qualidade & Segurança

- **Performance SLAs (ADR-019)**:
  - Query de histórico de conversa no Turso Local: **$< 10\text{ ms}$**
  - Criação de nova mensagem via API Core: **$< 50\text{ ms}$**
  - Processamento de avanço de passo de cadência no ARQ/APScheduler: **$< 100\text{ ms}$**
- **Segurança Zero-Trust (ADR-018)**:
  - Filtro mandatório por `organization_id` em todas as buscas de `conversations` e `messages`.
  - Acesso a conversas de outro tenant via `GET /api/v1/conversations/{id}` retorna **404 Not Found genérico**.
- **Garantia de Qualidade (ADR-020)**:
  - Cobertura de testes unitários/serviço **> 85%**.
  - **100% de cobertura nos testes de isolamento multi-tenant** (`tests/test_conversations_isolation.py`).
  - Migration Alembic testada via `upgrade head && downgrade -1 && upgrade head`.

---

## Criterios de Aceitacao (Definition of Done)

```
[ ] Criar conversa associada a um lead via POST /api/v1/conversations
[ ] Listar conversas ativas filtradas por tenant via GET /api/v1/conversations
[ ] Enviar mensagem inbound/outbound via POST /api/v1/conversations/{id}/messages
[ ] Scoring de Oportunidade atualiza a pontuação do lead automaticamente em cada evento
[ ] Cadence Engine processa steps agendados sem duplicar execuções (idempotência)
[ ] Cross-tenant isolation 100% aprovado em pytest
```
