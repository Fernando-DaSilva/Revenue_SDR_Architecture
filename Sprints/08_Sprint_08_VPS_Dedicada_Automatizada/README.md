# Sprint 08 — Omnichannel Completo (IG, Email, Voice)

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 08 — OMNICHANNEL COMPLETO                                  |
|   Status:  DOCUMENTADA                                              |
|   Owner:   Agente de codificacao                                     |
|   Quando:  Apos conclusao da Sprint 07                               |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-08-omnichannel                             |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visão Geral

Expansão das fronteiras de aquisição e relacionamento. O que era primariamente WhatsApp, ganha paridade em múltiplos canais.
1. **Instagram DM**: Conexão com Meta Graph API para responder mensagens diretas.
2. **Email**: SMTP para envio, e IMAP ou webhook (ex: SendGrid Inbound Parse) para leitura.
3. **Voice**: Integração com serviços de telefonia IP (ex: Twilio Voice) contendo síntese de voz (TTS) para um AI Voice Agent.
4. **Omnichannel Engine**: Motor lógico que mapeia e une a identidade do Lead se ele conversar por IG de manhã e WhatsApp à tarde, garantindo contexto único.

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
    provider VARCHAR(50) NOT NULL, -- instagram, whatsapp, email
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

## Decisões Críticas

- **Identity Resolution**: Definir estratégia conservadora de "Merge Automático". Se não houver certeza absoluta, cria um lead separado e oferece "Sugestão de Merge" para o operador.
- **Compliance e Limites**: O envio massivo por e-mail ou WhatsApp possui limitações de spam rigorosas. A infraestrutura deve tratar backpressure (Too Many Requests).
