---
name: sse-realtime-pattern
description: |
  Padroes de Server-Sent Events (SSE) para real-time no Revenue SDR OS.
  Carregue esta skill quando for implementar notificacoes live, transcricao,
  grafico DHS, ou qualquer atualizacao server→client em tempo real.
version: 1.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# Server-Sent Events (SSE) — Padroes do Revenue SDR OS

## Principio basico

```
Real-time server→client = SSE (NAO WebSocket).
Sprint 6: notificacoes + transcricao + grafico DHS atualizam ao vivo.
Lead ↔ IA: SSE empurra mensagens do servidor pro frontend do vendedor.
```

---

## Por que SSE e nao WebSocket

```
SSE                                WebSocket
+ Unidirecional (server→client)    + Bidirecional
+ Simples (HTTP + EventSource)     + Complexo (protocolo proprio)
+ FastAPI tem suporte nativo        + Precisa lib extra
+ Bateria-friendly                  + Mais drain
+ Auto-reconnect built-in           + Manual reconnect
+ Funciona com proxy/auth padrao    + Upgrade dance tricky

USAR SSE QUANDO: so servidor empurra dados pro cliente.
USAR WebSocket QUANDO: cliente precisa mandar dados em tempo real
                       (ex: vendedor digitando mensagem na plataforma).
```

---

## SSE endpoint FastAPI (app/realtime/sse.py)

```python
"""
Server-Sent Events endpoints.

Sprint 6+: notifications, transcription, deal health updates.
"""
import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/sse", tags=["sse"])


# === Pub/Sub simples (in-memory, OK para MVP) ===

class _Broker:
    """Broker de eventos in-memory. Por conversation_id e organization_id."""

    def __init__(self):
        # conversation_id → set de queues
        self.conversations: dict[str, set[asyncio.Queue]] = {}
        # organization_id → set de queues (notificacoes globais)
        self.organizations: dict[str, set[asyncio.Queue]] = {}

    def subscribe_conversation(self, conversation_id: str) -> asyncio.Queue:
        """Cria queue para receber eventos de uma conversa."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = set()
        queue = asyncio.Queue()
        self.conversations[conversation_id].add(queue)
        return queue

    def unsubscribe_conversation(self, conversation_id: str, queue: asyncio.Queue):
        """Remove queue."""
        if conversation_id in self.conversations:
            self.conversations[conversation_id].discard(queue)
            if not self.conversations[conversation_id]:
                del self.conversations[conversation_id]

    async def publish_conversation(self, conversation_id: str, event: dict):
        """Publica evento para todos os subscribers da conversa."""
        if conversation_id not in self.conversations:
            return
        for queue in self.conversations[conversation_id]:
            await queue.put(event)

    def subscribe_organization(self, organization_id: str) -> asyncio.Queue:
        """Cria queue para notificacoes globais da org."""
        if organization_id not in self.organizations:
            self.organizations[organization_id] = set()
        queue = asyncio.Queue()
        self.organizations[organization_id].add(queue)
        return queue

    def unsubscribe_organization(self, organization_id: str, queue: asyncio.Queue):
        if organization_id in self.organizations:
            self.organizations[organization_id].discard(queue)
            if not self.organizations[organization_id]:
                del self.organizations[organization_id]

    async def publish_organization(self, organization_id: str, event: dict):
        if organization_id not in self.organizations:
            return
        for queue in self.organizations[organization_id]:
            await queue.put(event)


# Singleton
broker = _Broker()


# === Endpoints ===

@router.get("/conversations/{conversation_id}")
async def stream_conversation(
    conversation_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Stream SSE de eventos de uma conversa."""

    async def event_generator() -> AsyncGenerator[dict, None]:
        queue = broker.subscribe_conversation(conversation_id)
        try:
            # Envia "ready" event ao conectar
            yield {
                "event": "connected",
                "data": json.dumps({
                    "conversation_id": conversation_id,
                    "timestamp": "now",
                }),
            }

            while True:
                # Aguarda evento ou detecta disconnect
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {
                        "event": event.get("type", "message"),
                        "data": json.dumps(event.get("data", {})),
                    }
                except asyncio.TimeoutError:
                    # Keep-alive (evita conexao cair por timeout)
                    yield {"event": "ping", "data": ""}

        finally:
            broker.unsubscribe_conversation(conversation_id, queue)

    return EventSourceResponse(event_generator())


@router.get("/organization/notifications")
async def stream_organization_notifications(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Stream SSE de notificacoes globais da Organization."""

    async def event_generator():
        queue = broker.subscribe_organization(current_user.organization_id)
        try:
            yield {
                "event": "connected",
                "data": json.dumps({"organization_id": current_user.organization_id}),
            }

            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {
                        "event": event.get("type", "notification"),
                        "data": json.dumps(event.get("data", {})),
                    }
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": ""}

        finally:
            broker.unsubscribe_organization(current_user.organization_id, queue)

    return EventSourceResponse(event_generator())
```

---

## Como publicar eventos (app/realtime/events.py)

```python
"""
Helper para publicar eventos no broker SSE.

Usado pelo webhook de WhatsApp, AI worker, etc.
"""
from app.realtime.sse import broker


async def publish_message_received(conversation_id: str, message_data: dict):
    """Publica que nova mensagem chegou."""
    await broker.publish_conversation(
        conversation_id,
        {
            "type": "message_received",
            "data": message_data,
        },
    )


async def publish_transcript_update(conversation_id: str, transcript_data: dict):
    """Publica atualizacao de transcricao (audio do lead)."""
    await broker.publish_conversation(
        conversation_id,
        {
            "type": "transcript_update",
            "data": transcript_data,
        },
    )


async def publish_score_changed(conversation_id: str, score_data: dict):
    """Publica mudanca de score (Opportunity Brain)."""
    await broker.publish_conversation(
        conversation_id,
        {
            "type": "score_changed",
            "data": score_data,
        },
    )


async def publish_emotion_detected(conversation_id: str, emotion_data: dict):
    """Publica deteccao de emocao."""
    await broker.publish_conversation(
        conversation_id,
        {
            "type": "emotion_detected",
            "data": emotion_data,
        },
    )


async def publish_new_lead_notification(organization_id: str, lead_data: dict):
    """Notificacao global: novo lead criado."""
    await broker.publish_organization(
        organization_id,
        {
            "type": "new_lead",
            "data": lead_data,
        },
    )
```

---

## Cliente JavaScript (static/js/sse-client.js)

```javascript
// static/js/sse-client.js
// Cliente SSE para o frontend

class SSEClient {
    constructor(url, options = {}) {
        this.url = url;
        this.eventSource = null;
        this.handlers = options.handlers || {};
        this.autoReconnect = options.autoReconnect !== false;
        this.reconnectDelay = options.reconnectDelay || 3000;
    }

    connect() {
        this.eventSource = new EventSource(this.url);

        // Event: connected (servidor confirma conexao)
        this.eventSource.addEventListener("connected", (e) => {
            console.log("[SSE] Connected:", JSON.parse(e.data));
            this._callHandler("connected", JSON.parse(e.data));
        });

        // Event: message_received
        this.eventSource.addEventListener("message_received", (e) => {
            const data = JSON.parse(e.data);
            console.log("[SSE] New message:", data);
            this._callHandler("message_received", data);
            // Atualizar UI:
            // - Adicionar mensagem na lista
            // - Scroll pra baixo
            // - Tocar som (opcional)
        });

        // Event: transcript_update
        this.eventSource.addEventListener("transcript_update", (e) => {
            const data = JSON.parse(e.data);
            this._callHandler("transcript_update", data);
            // Atualizar transcricao na UI
        });

        // Event: score_changed
        this.eventSource.addEventListener("score_changed", (e) => {
            const data = JSON.parse(e.data);
            this._callHandler("score_changed", data);
            // Atualizar grafico DHS
        });

        // Event: ping (keep-alive)
        this.eventSource.addEventListener("ping", () => {
            // Apenas log
        });

        // Erro
        this.eventSource.onerror = (e) => {
            console.error("[SSE] Error:", e);
            this._callHandler("error", e);
            if (this.autoReconnect) {
                this.eventSource.close();
                setTimeout(() => this.connect(), this.reconnectDelay);
            }
        };
    }

    _callHandler(name, data) {
        if (this.handlers[name]) {
            this.handlers[name](data);
        }
    }

    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
        }
    }
}

// Uso:
// const sse = new SSEClient("/sse/conversations/123", {
//     handlers: {
//         message_received: (data) => { /* atualizar UI */ },
//         score_changed: (data) => { /* atualizar grafico */ },
//     }
// });
// sse.connect();
```

---

## Como integrar com HTMX (Sprint 6+)

HTMX tem suporte nativo a SSE via `sse-swap` e `hx-sse`:

```html
<!-- Mensagens aparecem automaticamente -->
<div id="messages"
     hx-sse="connect:/sse/conversations/{{ conversation_id }}"
     sse-swap="message_received"
     hx-swap="beforeend">
    <!-- Mensagens serao inseridas aqui -->
</div>

<!-- Grafico DHS atualiza -->
<div id="dhs-gauge"
     hx-sse="connect:/sse/conversations/{{ conversation_id }}"
     sse-swap="score_changed">
    <!-- Gauge value atualiza -->
</div>
```

---

## Scaling considerations (futuro)

**Sprint atual (MVP)**: broker in-memory funciona pra 1 VPS.

**Quando escalar pra multiplas VPS**:
- Substituir broker in-memory por **Redis Pub/Sub**:
  ```python
  # app/realtime/sse.py (futuro)
  import redis.asyncio as redis

  redis_client = redis.from_url(settings.redis_url)

  async def publish_conversation(conversation_id, event):
      await redis_client.publish(f"conv:{conversation_id}", json.dumps(event))
  ```
- SSE endpoint se inscreve no Redis em vez do broker local
- Funciona entre multiplas VPS / pods

---

## Anti-patterns (NUNCA faca)

```python
# ERRADO: SSE nao fecha queue (memory leak)
@router.get("/sse/conversations/{id}")
async def stream(conversation_id, request):
    queue = broker.subscribe(conversation_id)
    while True:
        event = await queue.get()
        yield event
    # esqueceu broker.unsubscribe! # nunca fecha


# ERRADO: bloquear SSE com chamada lenta
async def event_generator():
    while True:
        event = await slow_db_query()  # 2s por evento!
        yield event
# Cliente percebe lag


# ERRADO: nao enviar keep-alive (proxy timeout)
async def event_generator():
    while True:
        event = await queue.get()  # espera indefinidamente
        yield event
# Apos 60s sem dados, nginx/cloudflare fecha conexao


# ERRADO: SSE sem autenticacao
@router.get("/sse/conversations/{id}")
async def stream(conversation_id):  # sem Depends(get_current_user)
    # qualquer um pode acessar qualquer conversa!
    ...
```

---

## Checklist

```
[ ] SSE endpoint usa EventSourceResponse (sse-starlette)
[ ] Subscribe + unsubscribe em try/finally
[ ] Keep-alive ping a cada 30s
[ ] Detecta disconnect (request.is_disconnected())
[ ] Auth obrigatoria (Depends(get_current_user))
[ ] Tenant isolation (user so ve SSE de sua org)
[ ] Publish helpers em app/realtime/events.py
[ ] Cliente JS com auto-reconnect
[ ] Broker in-memory documentado (migrar para Redis no futuro)
[ ] Testes: publish/subscribe, multi-subscriber, disconnect cleanup
```

---

*"SSE: 30 linhas de codigo, real-time funcionando."*