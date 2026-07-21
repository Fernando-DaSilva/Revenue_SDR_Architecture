# Sprint 03 — Conversations + Opportunity + Cadence

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 03 — CONVERSATIONS + OPPORTUNITY + CADENCE                 |
|   Status:  DOCUMENTADA                                              |
|   Owner:   Agente de codificacao                                     |
|   Quando:  Apos conclusao da Sprint 02                               |
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
    channel VARCHAR(50) NOT NULL, -- whatsapp, instagram, email
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

---

## Endpoints e Serviços

- **Conversations API**: `GET /api/v1/conversations`, `POST /api/v1/conversations/{id}/messages`
- **Cadence Service**: Lógica de enfileiramento de `jobs` assíncronos. Verificação periódica de `next_execution_at` para avançar `cadence_steps` e disparar eventos.
- **Scoring Engine**: Função que avalia `lead_timeline_events` e atualiza o campo `score` (e possivelmente a fase do funil) do lead na tabela `leads`.

---

## Decisões Pendentes
- Qual fila leve adotaremos? (ARQ vs APScheduler vs BackgroundTasks nativo no MVP). *Sugestão inicial: Iniciar com ARQ por sua robustez usando Redis, caso Redis já seja aceito na arquitetura; ou APScheduler se mantivermos apenas in-memory/SQLite WAL restrito.*
