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
3. **Transcrição de Áudio (Live)**: O áudio enviado pelo Lead via Zap passa por Whisper e a transcrição é cuspida em real-time na UI do atendente.
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
- **DHS Pipeline Push Endpoint**: `POST /api/v1/copilot/dhs`
  - Ingestão de atualizações do gráfico de saúde da negociação (**DHS Score -100 a +100**) enviadas pelo `02_ZAP_Prototype` (`PIPELINE_SCORE_UPDATE`).
- **RAG Suggestions & Feedback Endpoint**: `POST /api/v1/copilot/suggestions/feedback`
  - Recebe os eventos `AI_SUGGESTION_USED` para registrar o uso e assertividade da resposta no Memory Brain.
- **Audio Service**: Worker em background (Whisper Speech-to-Text) que escuta webhooks de áudio, transcreve, dispara o evento `AUDIO_TRANSCRIPTION_COMPLETED` e notifica via Broker SSE.
- **Coach Assistant Service**: Escuta ativamente cada nova mensagem e proativamente emite dicas via SSE para o painel de sugestões do `02_ZAP_Prototype`.

---

## Lógica Crítica de Negócio

- **Autenticação no SSE**: Como o SSE é invocado nativamente pelos navegadores através da interface `EventSource`, a autenticação preferencial deve ser feita pelo Cookie `rsdros_session`.
- **Sincronia Bidirecional com `02_ZAP_Prototype`**: As pontuações DHS e transcrições de áudio geradas na API central são enviadas via SSE para o `02_ZAP_Prototype`, atualizando reativamente o gráfico Chart.js v4 e o stream de mensagens.
- **Desconexão/Reconexão**: SSE já trata reconexão nativamente, e o protocolo de Auto-Sync descarrega a fila `pendingSyncQueue` ao reconectar.

