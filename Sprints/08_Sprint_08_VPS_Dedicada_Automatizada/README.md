# Sprint 08 — Omnichannel Completo (IG, Email, Voice)

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 08 — OMNICHANNEL COMPLETO                                  |
|   Status:  PRONTA PARA EXECUCAO (Hyper-Accelerated Hourly Micro-Sprints)|
|   Cadencia:Semana 7 (8 Micro-Sprints Horarias de 1h a 4h)             |
|   Owner:   Agente de codificacao                                     |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-08-omnichannel                             |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visão Geral

Expansão das fronteiras de aquisição e relacionamento. O que era primariamente Zap, ganha paridade em múltiplos canais.
1. **Instagram DM**: Conexão com Meta Graph API para responder mensagens diretas.
2. **Email**: SMTP para envio, e IMAP ou webhook (ex: SendGrid Inbound Parse) para leitura.
3. **Voice**: Integração com serviços de telefonia IP (ex: Twilio Voice) contendo síntese de voz (TTS) para um AI Voice Agent.
4. **Omnichannel Engine**: Motor lógico que mapeia e une a identidade do Lead se ele conversar por IG de manhã e Zap à tarde, garantindo contexto único.

---

## Schema Previsto (Alembic)

*O trabalho aqui requer atualizações pontuais, visto que `provider_credentials` da Sprint 4 já foi pensado para suportar multiplos provedores, e a tabela `conversations` suporta o campo `channel`.*

### Alterações em `provider_credentials`
Adicionar regras e webhooks específicos por provedor. As colunas já existentes bastam, mas os JSON schemas internos do campo `credentials` aumentam consideravelmente para abranger:
- Configurações IMAP/SMTP.
- Meta App Access Tokens (Instagram).
- SIP Credentials / Twilio Auth.

### Tabela: channel_identities (Identidades externas)
```sql
CREATE TABLE channel_identities (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,
    provider VARCHAR(50) NOT NULL, -- instagram, zap, email
    external_id VARCHAR(255) NOT NULL, -- ID do usuário no provedor (e.g. IG user ID)
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);
-- Indice Unico: (organization_id, provider, external_id)
```

---

## Endpoints e Serviços

- **Webhooks Meta/IG**: `POST /api/v1/webhooks/meta/{organization_id}`
- **Webhooks Email**: `POST /api/v1/webhooks/email/{organization_id}`
- **Voice Routing**: `POST /api/v1/twiml/incoming` (fornecendo XML para gerenciar IVR / chamadas de AI).

---

---

## Alinhamento com Prototipos (`01_SDR_Prototype` e `02_ZAP_Prototype`)

- **01_SDR_Prototype**:
  - Multichannel Live Chat Inbox (`inboxTab: 'multichannel'`): alternância fluida entre Zap, Email e Voice com badges visuais de canal (`badge-success` Zap, `badge-info` E-mail, `badge-secondary` Voice).
  - Identity Merge Drawer: fusão visual de identidades descobertas cross-channel (`channel_identities`).
- **02_ZAP_Prototype**:
  - Sincronização do stream de conversas omnichannel via protocolo Auto-Sync.

---

## SLAs de Performance (P95) e Requisitos de Qualidade & Segurança

- **Performance SLAs (ADR-019)**:
  - Ingestão de Webhooks Meta/Instagram: **$< 300\text{ ms}$**
  - Resposta do Voice Agent (TTS / Twilio IVR): **$< 600\text{ ms}$**
- **Segurança Zero-Trust (ADR-018)**:
  - Validação estrita de Meta Signature (`X-Hub-Signature-256`) em webhooks de Instagram.
  - ContextVar `organization_id` obrigatório nas consultas de `channel_identities`.
- **Garantia de Qualidade (ADR-020)**:
  - Cobertura de testes unitários do Omnichannel Engine **> 85%**.
  - **100% de cobertura nos testes de isolamento multi-tenant** (`tests/test_omnichannel_isolation.py`).
  - Migration Alembic da tabela `channel_identities` testada via round-trip.

---

## Criterios de Aceitacao (Definition of Done)

```
[ ] Recebimento de mensagens Instagram DM via Meta Webhook e envio de respostas outbound
[ ] Envio e recepção de e-mails corporativos vinculados à timeline do lead
[ ] Resposta a chamadas de Voz via AI Voice Agent (Twilio TwiML)
[ ] Resolução de Identidade Cross-Channel une interações de IG, Zap e Email no mesmo Lead
[ ] Cross-tenant isolation 100% aprovado em pytest
```
