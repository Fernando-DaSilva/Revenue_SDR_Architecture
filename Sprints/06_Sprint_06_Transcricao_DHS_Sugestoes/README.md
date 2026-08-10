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

---

## Alinhamento com Prototipos (`01_SDR_Prototype` e `02_ZAP_Prototype`)

- **01_SDR_Prototype**:
  - Live Feed no Command Center (`commandCenterTab: 'live_feed'`): feed em tempo real de eventos SSE disparados pelo sistema.
- **02_ZAP_Prototype**:
  - Gráfico de Saúde da Negociação (**DHS Score Chart** via Chart.js v4): renderização reativa das atualizações de humor do lead.
  - Painel de Sugestões RAG: lista de sugestões de resposta com pontuação de confiança e botão "Usar esta resposta".
  - Audio Player com Transcrição Whisper: reprodutor de notas de áudio com exibição de texto transcrito em tempo real.

---

## SLAs de Performance (P95) e Requisitos de Qualidade & Segurança

- **Performance SLAs (ADR-019)**:
  - Notificação via Server-Sent Events (SSE): **$< 100\text{ ms}$**
  - Transcrição de áudio via Whisper API: **$< 1,500\text{ ms}$**
  - Geração de sugestão RAG de resposta: **$< 800\text{ ms}$**
- **Segurança Zero-Trust (ADR-018)**:
  - Autenticação de conexões SSE através de Cookie HttpOnly `rsdros_session`.
  - Isolamento de canais SSE por `organization_id` ContextVar (clientes de um tenant não recebem eventos de outros).
- **Garantia de Qualidade (ADR-020)**:
  - Cobertura de testes unitários do broker SSE e serviço Whisper **> 85%**.
  - **100% de cobertura nos testes de isolamento de SSE multi-tenant** (`tests/test_sse_isolation.py`).
  - Migration Alembic da tabela `user_notifications` validada via round-trip.

---

## Criterios de Aceitacao (Definition of Done)

```
[ ] Connection SSE (GET /api/v1/stream/events) estabelecida e mantida com reconexão automática
[ ] Transcrição de áudio via Whisper gera evento AUDIO_TRANSCRIPTION_COMPLETED e dispara via SSE
[ ] Ingestão de atualizações DHS (POST /api/v1/copilot/dhs) atualiza gráfico Chart.js v4 reativamente
[ ] Sugestões RAG alimentadas via SSE no painel lateral do 02_ZAP_Prototype
[ ] Cross-tenant isolation 100% aprovado (eventos SSE não vazam entre tenants)
```

