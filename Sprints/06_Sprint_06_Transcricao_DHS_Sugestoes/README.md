# Sprint 06 — Real-time (Transcrição, DHS e Sugestões SSE)

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 06 — TRANSCRIÇÃO + GRAFICO DHS + SUGESTOES (SSE)            |
|   Status:  DOCUMENTADA                                              |
|   Owner:   Agente de codificacao                                     |
|   Quando:  Apos conclusao da Sprint 05                               |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-06-realtime-sse                            |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visão Geral

Implementação do protocolo de comunicação em tempo real unidirecional do servidor para o cliente (Server-Sent Events - SSE), evitando a complexidade de WebSockets.
1. **SSE Broker**: Serviço para enfileirar e despachar notificações de servidor para clientes escutando.
2. **Notificações Live**: Avisos na interface do SDR sobre novas mensagens, alertas de Handoff solicitados pela IA.
3. **Transcrição de Áudio (Live)**: O áudio enviado pelo Lead via WhatsApp passa por Whisper e a transcrição é cuspida em real-time na UI do atendente.
4. **Gráfico DHS (Dynamic Health Score)**: UI responsiva para alteração do humor/interesse da negociação na linha do tempo.
5. **Sugestões de Objeção**: IA sugere a melhor resposta para o SDR baseado na última mensagem recebida.

---

## Schema Previsto (Alembic)

*Esta sprint foca majoritariamente em comunicação, portanto não há grandes mudanças no modelo de dados, exceto talvez um registro persistente de notificações.*

### Tabela: user_notifications
```sql
CREATE TABLE user_notifications (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    type VARCHAR(50) NOT NULL, -- handoff_request, new_lead, SLA_breach
    payload JSON NOT NULL,
    read_at DATETIME,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Endpoints e Serviços

- **SSE Stream**: `GET /api/v1/stream/events`
  - Endpoint assíncrono mantido aberto devolvendo dados no formato `text/event-stream`.
- **Audio Service**: Worker em background (dependência de Speech-to-Text) que escuta os webhooks com anexos de áudio da Z-API, transcreve, salva na tabela de mensagens e emite o evento via Broker SSE.
- **Coach Assistant Service**: Escuta ativamente cada nova mensagem e proativamente emite dicas via SSE.

---

## Lógica Crítica de Negócio

- **Autenticação no SSE**: Como o SSE é invocado nativamente pelos navegadores através da interface `EventSource`, a autenticação preferencial deve ser feita pelo Cookie `rsdros_session`.
- **Desconexão/Reconexão**: SSE já trata reconexão nativamente, mas o client deve passar um `Last-Event-ID` caso precise reaver mensagens perdidas, ou a arquitetura pode tratar a tela do usuário como descartável (state em banco é fonte de verdade para history).
