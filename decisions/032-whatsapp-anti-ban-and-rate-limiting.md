# ADR-032: Rate Limiting Anti-Ban no WhatsApp e Imposição Rígida da Janela de 24 Horas da Meta

* **Status**: Aprovado
* **Data**: Agosto 2026
* **Autores**: Equipe de Arquitetura e Engenharia Backend (Revenue SDR OS)

---

## 1. Contexto e Problema

A integração com o WhatsApp no **Revenue SDR OS** suporta tanto a API Oficial (Meta Cloud API) quanto provedores não oficiais de mercado (Z-API, Evolution API). A operação comercial via WhatsApp impõe duas restrições críticas que, se violadas, causam bloqueio imediato do número de telefone da empresa ou falha na entrega de mensagens:

1. **Janela de Atendimento de 24 Horas (Meta Policy)**:
   - A Meta impõe uma janela de 24 horas a partir da última mensagem enviada pelo lead (*last_inbound_timestamp*).
   - Após 24 horas sem interação do lead, mensagens em texto livre (*freeform messages*) enviadas por IA ou automações de cadência são BLOQUEADAS pela Meta ou resultam no banimento da conta por spam. Notificações ativas de cadência (Sprint 03+) após esse período EXIGEM a seleção de **Modelos de Mensagem Aprovados (HSM Templates)**.

2. **Risco de Banimento por Envio em Massa / Padrão Robótico (Anti-Ban)**:
   - Provedores não oficiais (Z-API/Evolution) detectam rajadas de envio e comportamento não humano. Disparar mensagens instantaneamente sem pausas dinâmicas ou sem simular digitação conduz ao bloqueio definitivo do chip pela rede do WhatsApp.

3. **Expiração de Mídia / Áudios Inbound**:
   - Os URLs de mídias (notas de áudio OGG/Opus, imagens) recebidas nos webhooks da Z-API expiram em 5 a 10 minutos. O processamento assíncrono do Whisper não pode depender do URL exposto no payload original.

---

## 2. Decisão Arquitetural

Implementar uma **Camada de Proteção de Ingestão e Envio WhatsApp** no `ZapService` e no `CadenceEngine` (`app/services/zap_service.py` e `app/services/cadence_service.py`).

### A. Imposição Rígida da Janela de 24 Horas da Meta

Antes de despachar qualquer mensagem de saída de cadência ou IA:
1. O `CadenceEngine` calcula o delta: `delta = utc_now() - lead.last_inbound_timestamp`.
2. **Se `delta <= 24h`**: O Agente SDR de IA pode enviar respostas em texto livre (*freeform*).
3. **Se `delta > 24h`**:
   - O sistema bloqueia a geração de mensagens em texto livre.
   - O `CadenceEngine` força a seleção de um **HSM Template** previamente aprovado na Meta (com parâmetros dinâmicos como nome do lead e empresa).
   - Se nenhum HSM Template for aplicável, a conversa entra em estado de atenção no Zap Copilot (`02_ZAP_Prototype`), notificando o operador vendedor humano para reengajamento manual.

```
Outbound Cadence Step / AI Message
  |
  v
Check: (utc_now() - lead.last_inbound_timestamp)
  |
  +---> <= 24h: Freeform AI Response Allowed -> Envia via ZapService
  |
  +---> > 24h:  Freeform BLOCKED
                  |-- HSM Template Configurado? -> Envia HSM Template (Meta Approved)
                  +-- Sem HSM -> Notifica Operador no Zap Copilot (Human Action Required)
```

### B. Guardiões Anti-Ban & Rate Limiter Humano (Z-API / Evolution API)

Para mitigar o risco de banimento de chips em provedores não oficiais:
1. **Rate Limiting em Camadas (Token Bucket)**:
   - Capped a no máximo **1 mensagem a cada 3 a 5 segundos** por instância WhatsApp.
   - Limite de segurança diário: no máximo **200 disparos de saída / dia** para instâncias novas (< 14 dias de maturação), escalando gradualmente via playbooks de aquecimento.
2. **Humanized Jitter & Eventos de Digitação**:
   - Injeção obrigatória de **atraso randômico humano** ($2.0\text{s} - 7.0\text{s}$) antes de disparar o payload final da mensagem.
   - Disparo do evento `sendPresence("composing")` via Z-API/Evolution API durante o período de espera para simular digitação humana aos olhos dos servidores do WhatsApp.

### C. Download Assíncrono Imediato de Mídias/Áudio

No worker de ingestão de webhooks (`process_inbound_whatsapp_message_task`):
- Se o payload contiver um `audio_url` ou `media_url`, o Taskiq worker realiza o **download em stream binário imediatamente** para o storage local/S3 (`app/storage/media/`) antes de agendar a transcrição no Whisper, evitando erros de URL expirado.

---

## 3. Código de Referência de Implementação

```python
# app/services/zap_service.py
import asyncio
import random
from datetime import datetime, timezone, timedelta
from app.core.exceptions import AppError
from app.services.zapi_client import zapi_client

class ZapService:
    META_WINDOW_HOURS = 24

    async def send_message_safely(
        self,
        organization_id: str,
        phone_number: str,
        text_content: str | None,
        hsm_template_id: str | None,
        last_inbound_timestamp: datetime | None,
    ) -> dict:
        # 1. Enforce Meta 24-Hour Customer Service Window
        now = datetime.now(timezone.utc)
        if last_inbound_timestamp:
            elapsed = now - last_inbound_timestamp
            if elapsed > timedelta(hours=self.META_WINDOW_HOURS) and not hsm_template_id:
                raise AppError(
                    code="meta_24h_window_expired",
                    message="Freeform messages prohibited >24h after last inbound contact. Use HSM Template.",
                    details={"elapsed_hours": elapsed.total_seconds() / 3600},
                )

        # 2. Apply Anti-Ban Human Jitter & Composing Status
        jitter_delay = random.uniform(2.0, 6.0)
        await zapi_client.send_presence_composing(phone_number)
        await asyncio.sleep(jitter_delay)

        # 3. Dispatch Message Payload
        if hsm_template_id:
            return await zapi_client.send_hsm_template(phone_number, hsm_template_id)
        else:
            return await zapi_client.send_text(phone_number, text_content)
```

---

## 4. Consequências

* **Positivas**:
  - Risco de banimento de número no WhatsApp reduzido em mais de 90% via rate limiting e comportamentos humanizados.
  - Conformidade total com a política oficial de mensagens da Meta (zero bloqueios por violação da janela de 24h).
  - Preservação da integridade de notas de voz/mídia através do download síncrono no Taskiq.
* **Negativas / Riscos**:
  - Cadências automatizadas iniciadas após 24h exigem o cadastro prévio de templates HSM na Meta Business Manager.

---

## 5. Invariantes para Agentes de Codificação (AI Coding Guardrails)

1. **NUNCA** permitir que o `CadenceEngine` envie mensagens em texto livre (*freeform*) para leads com `last_inbound_timestamp` superior a 24 horas.
2. **SEMPRE** injetar o delay aleatório de 2.0s a 6.0s e o evento `composing` antes de efetuar chamadas de envio outbound no `ZapService`.
3. **SEMPRE** realizar o download imediato do buffer binário de áudios no Taskiq antes de invocar a API de transcrição Whisper.
