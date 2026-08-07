# Sprint 04 — AI Sales Brain + Z-API Zap

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 04 — AI SALES BRAIN + Z-API ZAP                       |
|   Status:  DOCUMENTADA                                              |
|   Owner:   Agente de codificacao                                     |
|   Quando:  Apos conclusao da Sprint 03                               |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-04-ai-zap                             |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visão Geral

Esta sprint dá "vida" ao sistema, conectando-o ao mundo externo (Zap) e ativando a inteligência artificial para conduzir negociações.
1. **ZapProvider (Z-API)**: Implementação concreta da abstração de provedor de mensagens definida na arquitetura.
2. **Webhooks de Entrada**: Recepção de mensagens, status de leitura/entrega em tempo real.
3. **Envio Outbound**: Serviço para enviar mensagens através da Z-API.
4. **AI Sales Brain**: Agente conversacional construído com LLM (RAG para conhecimento de produto, Tools para ações como marcar reunião, Persona configurável por tenant).
5. **Human vs AI Mode**: Controle de contexto para pausar o robô automaticamente quando o atendente humano assume a conversa.

---

## Schema Previsto (Alembic)

### Tabela: provider_credentials
```sql
CREATE TABLE provider_credentials (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    provider VARCHAR(50) NOT NULL, -- zapi, meta
    credentials JSON NOT NULL, -- tokens, instance_id
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

### Alterações em `conversations`
```sql
ALTER TABLE conversations ADD COLUMN ai_mode BOOLEAN NOT NULL DEFAULT TRUE;
```

---

## Endpoints e Serviços

- **Webhooks**: `POST /api/v1/webhooks/zapi/{organization_id}` - Extremamente performático, validando o origin e despachando para processamento (job ou em background).
- **Copilot Standalone Integration API (`02_ZAP_Prototype`)**:
  - `POST /api/v1/copilot/sync` - Recebe os eventos de auto-sync do micro-app standalone (`SDR_MESSAGE_SENT`, `LEAD_CONVERSATION_LOADED`, `THEME_PRESET_CHANGED`).
  - `POST /api/v1/copilot/mode` - Atualiza o modo da conversa (`isCopilotActive: true/false`, `badge: SDR_COPILOT_ASSISTED` vs `SDR_HUMAN_OPERATOR`).
- **AI Brain Service**:
  - `generate_reply(conversation_id)`
  - Acessa o Memory Brain (da Sprint 2) e o histórico de mensagens (da Sprint 3) para montar o *prompt context*.
- **Tool Calling**: A IA deve ser capaz de chamar ferramentas internas como `add_lead_memory` ou `schedule_meeting`.

---

## Lógica Crítica de Negócio

1. **Abstração Obrigatória**: O código não pode depender fortemente de Z-API em suas camadas de negócio. O payload de webhook Z-API deve ser normalizado para um formato de evento interno (`StandardMessageEvent`) no adapter.
2. **Handoff Prevention & Copilot Sync**: Se `ai_mode` for false (SDR Humano no `02_ZAP_Prototype`), a IA ignora a mensagem recebida e atua apenas como copiloto de sugestões RAG. Se o humano envia uma mensagem, o sistema registra o papel `SDR_HUMAN_OPERATOR` e atualiza o estado para Handoff.
3. **Resiliência Offline Standalone**: A API `/copilot/sync` aceita batched payloads da fila `pendingSyncQueue` provenientes do `localStorage` do `02_ZAP_Prototype` após a reconexão.

