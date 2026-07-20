---
name: whatsapp-zapi-integration
description: |
  Padroes de integracao WhatsApp via Z-API para o Revenue SDR OS. Carregue
  esta skill quando for implementar webhook, envio de mensagens, ou
  qualquer feature de WhatsApp.
version: 1.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# WhatsApp via Z-API — Padroes do Revenue SDR OS

## Principio basico

```
Z-API e' unofficial (wrapper de WhatsApp Web). Funciona no MVP.
Migracao para Twilio/Meta Cloud API e' MECANICA via abstracao WhatsAppProvider.
Multi-tenant: cada Organization tem seu proprio instance_id da Z-API.
```

---

## Abstracao WhatsAppProvider

### Interface (app/integrations/whatsapp/base.py)

```python
"""
Interface WhatsAppProvider — abstracao sobre qualquer provider.

Sprint 4: Z-API (MVP unofficial)
Sprint 5+: Twilio / Meta Cloud API (oficial)
"""
from typing import Protocol, Any
from dataclasses import dataclass


@dataclass
class Message:
    """Mensagem normalizada (independente de provider)."""
    to: str  # telefone destino (E.164: +5511999999999)
    content: str
    media_url: Optional[str] = None  # para audio, imagem, video
    media_type: Optional[str] = None  # "image", "audio", "video", "document"
    reply_to: Optional[str] = None  # message_id pra responder


@dataclass
class IncomingMessage:
    """Mensagem recebida (webhook)."""
    from_: str  # telefone origem
    to: str  # seu numero (WhatsApp Business)
    content: str
    message_id: str  # ID unico da mensagem no WhatsApp
    timestamp: int  # unix timestamp
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    is_from_me: bool = False  # se foi enviada por nos
    instance_id: str  # ID da instancia Z-API (multi-tenant)


@dataclass
class SendResult:
    """Resultado de envio."""
    success: bool
    message_id: Optional[str] = None  # ID da mensagem enviada
    error: Optional[str] = None


class WhatsAppProvider(Protocol):
    """Interface que todos os providers devem implementar."""

    async def send_message(self, instance_id: str, message: Message) -> SendResult:
        """Envia mensagem."""
        ...

    async def get_instance_status(self, instance_id: str) -> dict:
        """Status da instancia (connected, qr_code, etc)."""
        ...

    async def parse_webhook(self, payload: dict) -> IncomingMessage:
        """Parseia payload do webhook para IncomingMessage normalizado."""
        ...
```

---

## Implementacao Z-API (app/integrations/whatsapp/zapi.py)

```python
"""
Z-API provider — wrapper de WhatsApp Web (nao oficial).

Docs: https://developer.z-api.io
Risco: Meta pode bloquear (mitigacao: provider abstraido)
"""
import httpx
from typing import Optional
from app.integrations.whatsapp.base import (
    WhatsAppProvider, Message, IncomingMessage, SendResult,
)


class ZAPIProvider(WhatsAppProvider):
    """Implementacao Z-API do WhatsAppProvider."""

    BASE_URL = "https://api.z-api.io"

    def __init__(self, default_token: str):
        """
        Args:
            default_token: Token default (instance_id-specific vem do banco)
        """
        self.default_token = default_token

    async def send_message(
        self,
        instance_id: str,
        message: Message,
        instance_token: Optional[str] = None,
    ) -> SendResult:
        """Envia mensagem via Z-API.

        Endpoint: POST /instances/{instance_id}/token/{token}/send-text
        Docs: https://developer.z-api.io/post/send-text
        """
        token = instance_token or self.default_token
        url = f"{self.BASE_URL}/instances/{instance_id}/token/{token}/send-text"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "phone": message.to,  # E.164
                    "message": message.content,
                },
                timeout=10.0,
            )

        if response.status_code == 200:
            data = response.json()
            return SendResult(success=True, message_id=data.get("messageId"))
        else:
            return SendResult(
                success=False,
                error=f"Z-API error {response.status_code}: {response.text}",
            )

    async def get_instance_status(self, instance_id: str, instance_token: str) -> dict:
        """Status da instancia Z-API."""
        url = f"{self.BASE_URL}/instances/{instance_id}/token/{instance_token}/status"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
        return response.json() if response.status_code == 200 else {"connected": False}

    async def parse_webhook(self, payload: dict) -> IncomingMessage:
        """Parseia webhook Z-API.

        Payload tipico:
        {
          "instanceId": "ABC123",
          "messageId": "ABCDEF",
          "phone": "5511999999999",
          "fromMe": false,
          "moments": "1",
          "type": "ReceivedCallback",
          "text": {"message": "Oi, quero saber..."},
          "image": {"imageUrl": "...", "mimeType": "image/jpeg"},  # opcional
          "audio": {"audioUrl": "...", "mimeType": "audio/ogg"},  # opcional
          "timestamp": 1690123456
        }
        """
        text = payload.get("text", {}).get("message", "")

        media_url = None
        media_type = None
        for mt in ("image", "audio", "video", "document"):
            if mt in payload and payload[mt]:
                media_url = payload[mt].get(f"{mt}Url")
                media_type = mt
                break

        return IncomingMessage(
            from_=payload.get("phone", "").replace("+", ""),  # Z-API vem sem +
            to="",
            content=text,
            message_id=payload.get("messageId", ""),
            timestamp=payload.get("timestamp", 0),
            media_url=media_url,
            media_type=media_type,
            is_from_me=payload.get("fromMe", False),
            instance_id=payload.get("instanceId", ""),
        )
```

---

## Webhook handler (app/webhooks/zapi.py)

```python
"""
Z-API webhook handler.

Endpoint: POST /webhooks/zapi/incoming

Fluxo:
1. Recebe webhook
2. Parseia (ZAPIProvider.parse_webhook)
3. Identifica Organization pelo instance_id
4. Identifica ou cria Lead pelo telefone
5. Identifica ou cria Conversation
6. Salva Message inbound
7. Enfileira job de processamento IA
8. Emite SSE event
9. Retorna 200 (Z-API exige < 5s)
"""
from datetime import UTC, datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.integrations.whatsapp.zapi import ZAPIProvider
from app.integrations.whatsapp.factory import get_whatsapp_provider
from app.database import get_session
from app.models.lead import Lead
from app.models.conversation import Conversation
from app.models.message import Message as MessageModel
from app.models.organization import Organization
from app.services.lead_merge import find_existing_lead
from app.services.message_dispatcher import dispatch_message

router = APIRouter(prefix="/webhooks/zapi", tags=["zapi-webhook"])


@router.post("/incoming")
async def incoming_message(
    payload: dict,
    background_tasks: BackgroundTasks,
):
    """Recebe mensagem inbound do WhatsApp via Z-API."""
    provider = get_whatsapp_provider()
    msg = provider.parse_webhook(payload)

    # 1. Ignora mensagens enviadas por nos
    if msg.is_from_me:
        return {"status": "ignored", "reason": "from_me"}

    # 2. Identifica Organization pelo instance_id
    with next(get_session()) as db:
        org = db.exec(
            select(Organization).where(
                Organization.zapi_instance_id == msg.instance_id,
                Organization.is_active == True,
            )
        ).first()

        if not org:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown instance_id: {msg.instance_id}",
            )

        # 3. Identifica ou cria Lead (Lead Brain)
        phone = "+" + msg.from_  # normalizar pra E.164
        lead = find_existing_lead(
            db,
            organization_id=org.id,
            phone=phone,
        )

        if not lead:
            # Criar lead novo (origem: whatsapp)
            lead = Lead(
                organization_id=org.id,
                name=f"WhatsApp {phone[-4:]}",  # placeholder
                phone=phone,
                source="whatsapp",
                status="novo",
                last_interaction_at=datetime.now(UTC),
            )
            db.add(lead)
            db.commit()
            db.refresh(lead)

        # 4. Identifica ou cria Conversation
        conv = db.exec(
            select(Conversation).where(
                Conversation.lead_id == lead.id,
                Conversation.closed_at.is_(None),
            )
        ).first()

        if not conv:
            conv = Conversation(
                organization_id=org.id,
                lead_id=lead.id,
                channel_first="whatsapp",
                mode="ai",
                current_stage="novo",
                score=0,
                emotional_state="neutro",
                last_interaction_at=datetime.now(UTC),
            )
            db.add(conv)
            db.commit()
            db.refresh(conv)

        # 5. Salva Message inbound
        message = MessageModel(
            organization_id=org.id,
            conversation_id=conv.id,
            direction="inbound",
            channel="whatsapp",
            sender_type="lead",
            content=msg.content,
            media_url=msg.media_url,
            ai_generated=False,
            sent_at=datetime.fromtimestamp(msg.timestamp),
            external_id=msg.message_id,  # ID do Z-API
        )
        db.add(message)
        conv.last_interaction_at = datetime.now(UTC)
        db.add(conv)
        db.commit()
        db.refresh(message)

        # 6. Enfileira processamento IA (async, nao bloqueia webhook)
        background_tasks.add_task(
            dispatch_message,
            conversation_id=conv.id,
            message_id=message.id,
            organization_id=org.id,
        )

    return {"status": "received", "message_id": message.id}
```

---

## Factory de provider (app/integrations/whatsapp/factory.py)

```python
"""
Factory para trocar provider de WhatsApp sem mexer no resto do codigo.
"""
from functools import lru_cache
from app.config import get_settings
from app.integrations.whatsapp.zapi import ZAPIProvider

# Quando migrar para Twilio/Cloud API:
# from app.integrations.whatsapp.twilio import TwilioProvider

settings = get_settings()


@lru_cache
def get_whatsapp_provider():
    """Retorna provider ativo baseado em settings."""
    # Por enquanto, sempre Z-API
    # Quando migrar, settings.whatsapp_provider = "twilio"
    if settings.whatsapp_provider == "zapi":
        return ZAPIProvider(default_token=settings.zapi_default_token)
    # elif settings.whatsapp_provider == "twilio":
    #     return TwilioProvider(...)
    else:
        raise ValueError(f"Unknown provider: {settings.whatsapp_provider}")
```

---

## Settings (.env)

```bash
# Z-API
WHATSAPP_PROVIDER="zapi"
ZAPI_DEFAULT_TOKEN="<seu-token-z-api>"
ZAPI_BASE_URL="https://api.z-api.io"

# Webhook security (opcional, recomendado)
ZAPI_WEBHOOK_SECRET="<secret-compartilhado-com-zapi>"

# Para migracao futura (Sprint 5+):
# WHATSAPP_PROVIDER="twilio"
# TWILIO_ACCOUNT_SID="..."
# TWILIO_AUTH_TOKEN="..."
```

---

## Migracao futura Z-API → Twilio

**Quando migrar:**
- Cliente enterprise exige oficial Meta
- Volume justifica custo de Twilio
- SLA contratual

**Como migrar (mecanica via abstracao):**

1. Criar `app/integrations/whatsapp/twilio.py` implementando `WhatsAppProvider`
2. Trocar factory: `if settings.whatsapp_provider == "twilio": return TwilioProvider(...)`
3. Webhook handler NAO muda (usa interface)
4. Migration script: pra cada Organization, recriar conversation history no Twilio
5. Manter Z-API como fallback por 3-6 meses

**Risco de churn**: clientes podem perder historico de conversa. Mitigacao: arquivar conversas em JSON antes de migrar.

---

## Anti-patterns (NUNCA faca)

```python
# ERRADO: chamar Z-API diretamente no codigo
import httpx
response = httpx.post("https://api.z-api.io/instances/.../send-text", ...)


# ERRADO: hardcoded instance_id
@router.post("/incoming")
async def incoming(payload: dict):
    org = db.exec(select(Organization).where(Organization.id == "org_hardcoded")).first()


# ERRADO: bloquear webhook com chamada sincrona lenta
@router.post("/incoming")
async def incoming(payload: dict):
    # processa IA AQUI (demora 30s) — Z-API timeout em 5s!
    response = openai.chat.completions.create(...)
    send_whatsapp_message(...)
# Z-API vai dar timeout e reenviar webhook → duplica mensagem


# ERRADO: nao validar instance_id (multi-tenant leak)
@router.post("/incoming")
async def incoming(payload: dict):
    msg = parse(payload)
    # salva em qualquer org sem verificar instance_id
    org = db.exec(select(Organization)).first()  # PRIMEIRA org = LEAK!
    save_message(org.id, msg)
```

---

## Checklist

```
[ ] Interface WhatsAppProvider definida em app/integrations/whatsapp/base.py
[ ] ZAPIProvider implementa interface
[ ] Factory get_whatsapp_provider() configuravel via settings
[ ] Webhook handler valida instance_id (NAO pega "primeira org")
[ ] Webhook ignora mensagens from_me
[ ] Webhook identifica/cria Lead via Lead Brain
[ ] Webhook identifica/cria Conversation
[ ] Processamento IA roda em background task (NAO sincrono)
[ ] Z-API exige response < 5s (webhook retorna rapido)
[ ] Multi-tenant: Z-API instance_id armazenado por Organization
[ ] Settings tem whatsapp_provider configuravel
[ ] Documentacao de migracao para Twilio/Cloud API
```

---

*"WhatsApp nao e' um canal — e' a pessoa falando."*