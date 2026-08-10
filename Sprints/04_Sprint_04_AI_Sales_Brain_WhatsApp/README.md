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

---

## Alinhamento com Prototipos (`01_SDR_Prototype` e `02_ZAP_Prototype`)

- **01_SDR_Prototype**:
  - Live Chat Inbox (`aiMode: 'Ativo (SDR-01)'` vs `'Handoff Solicitado'`): controle do modo autônomo da IA vs intervenção humana.
  - Copilot Execution Confirmation Modal: modal de confirmação de execuções de ferramentas pela IA.
- **02_ZAP_Prototype**:
  - Central Chat Stream: alternador de modo IA Copilot (`🤖 Copilot Active` vs `👤 Human Mode`).
  - Protocolo de Auto-Sync em Background: endpoint `/api/v1/copilot/sync` para ingestão de eventos e payloads do `02_ZAP_Prototype`.

---

## SLAs de Performance (P95) e Requisitos de Qualidade & Segurança

- **Performance SLAs (ADR-019)**:
  - Ingestão do Webhook Z-API (`POST /webhooks/zapi`): **$< 300\text{ ms}$** (Handshake HTTP 200 síncrono imediato)
  - Resposta do Agente AI Sales SDR (LLM): **$< 1,200\text{ ms}$** (Prompt Caching + Roteamento Gemini 1.5 Flash)
  - Ingestão do protocolo Auto-Sync (`POST /copilot/sync`): **$< 50\text{ ms}$**
- **Segurança Zero-Trust (ADR-018)**:
  - Validação estrita de assinatura token nos webhooks da Z-API.
  - Criptografia das credenciais de provedor em `provider_credentials.credentials`.
  - ContextVar `organization_id` obrigatório nas consultas do AI Brain.
- **Garantia de Qualidade (ADR-020)**:
  - Cobertura de testes unitários do AI Sales Brain e Tool Calling **> 85%**.
  - **100% de cobertura nos testes de isolamento multi-tenant** (`tests/test_zapi_isolation.py`).
  - Validação da migration Alembic round-trip.

---

## Criterios de Aceitacao (Definition of Done)

```
[ ] Ingestão de webhook Z-API convertendo para StandardMessageEvent
[ ] Envio outbound via ZapProvider funcionando
[ ] AI Sales Brain responde leads qualificando e executando tool calling (add_memory, schedule_meeting)
[ ] Toggle ai_mode alterna com sucesso entre resposta IA automática e modo Copilot Humano
[ ] Ingestão do protocolo Auto-Sync (/api/v1/copilot/sync) processa payloads offline do 02_ZAP_Prototype
[ ] Cross-tenant isolation 100% aprovado em pytest
```

