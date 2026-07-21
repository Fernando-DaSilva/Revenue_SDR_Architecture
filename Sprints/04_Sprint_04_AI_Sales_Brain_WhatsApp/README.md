# Sprint 04 — AI Sales Brain + Z-API WhatsApp

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 04 — AI SALES BRAIN + Z-API WHATSAPP                       |
|   Status:  DOCUMENTADA                                              |
|   Owner:   Agente de codificacao                                     |
|   Quando:  Apos conclusao da Sprint 03                               |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-04-ai-whatsapp                             |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visão Geral

Esta sprint dá "vida" ao sistema, conectando-o ao mundo externo (WhatsApp) e ativando a inteligência artificial para conduzir negociações.
1. **WhatsAppProvider (Z-API)**: Implementação concreta da abstração de provedor de mensagens definida na arquitetura.
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
- **AI Brain Service**:
  - `generate_reply(conversation_id)`
  - Acessa o Memory Brain (da Sprint 2) e o histórico de mensagens (da Sprint 3) para montar o *prompt context*.
- **Tool Calling**: A IA deve ser capaz de chamar ferramentas internas como `add_lead_memory` ou `schedule_meeting`.

---

## Lógica Crítica de Negócio

1. **Abstração Obrigatória**: O código não pode depender fortemente de Z-API em suas camadas de negócio. O payload de webhook Z-API deve ser normalizado para um formato de evento interno (`StandardMessageEvent`) no adapter.
2. **Handoff Prevention**: Se `ai_mode` for false, a IA ignora a mensagem recebida. Se o humano envia uma mensagem, o sistema muda o `ai_mode` para false automaticamente.
