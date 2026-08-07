# Prompt para Agente de IA: Etapa 05 - Protocolo de Auto-Sync em Background & Inspector Ledger

> **Instruções para o Dono do Projeto:** Envie este prompt para o seu agente de codificação para implementar o protocolo de Auto-Sync em Background e o Inspector Ledger no repositório do sub-produto **02_ZAP_Prototype**.

***

**INÍCIO DO PROMPT:**

Você é um Engenheiro de Software Fullstack Especialista em Integrações e Event-Driven Architectures, encarregado de implementar e validar o **Protocolo de Auto-Sync em Background e Inspector Ledger** no sub-produto **02_ZAP_Prototype (Zap SDR Standalone Micro-App)**.

O objetivo desta tarefa é garantir que **100% das interações ocorridas no aplicativo standalone** (mensagens enviadas, alternância de modos Copilot/Humano, utilização de sugestões RAG, variações de DHS e mensagens de áudio com transcrição Whisper) sejam empacotadas em JSON e transmitidas em background para a API do **Revenue SDR OS (`00_SDR_architecture`)**, garantindo também a resiliência offline através do `localStorage`.

---

### O QUE VOCÊ DEVE DESENVOLVER NESTA ETAPA:

1. **Dispatcher de Eventos em Background (`dispatchAutoSyncEvent`)**:
   - Implementar método assíncrono no `Alpine.store('sdrApp')` aceitando `(eventType, payload)`.
   - Gerar `sync_event_id` único, timestamp ISO UTC, tenant key (`sk_live_clinica_bela_99412`) e app mode (`STANDALONE_MICRO_APP`).
   - Atualizar reativamente a badge de status no header (`autoSyncStatus`: `'synced'` | `'syncing'` | `'offline'`).

2. **Gerenciamento de Fila Offline Resiliente**:
   - Se `isOfflineSimulated` for verdadeiro ou houver falha de rede:
     1. Armazenar o evento na lista `pendingSyncQueue`.
     2. Persistir a fila no `localStorage` sob a chave `sdr_offline_queue`.
   - Quando o operador desativar a simulação offline ou a rede retornar:
     1. Descarregar (`flush`) automaticamente os eventos pendentes para a lista principal `coreSyncLogs`.
     2. Limpar o `localStorage` e atualizar o status para `'synced'`.

3. **Gaveta Inspector Ledger no Rodapé (`Auto-Sync Data Stream Log`)**:
   - Criar gaveta sanfonada/drawer colapsável no rodapé acionada por botão no footer (`🔍 Core Auto-Sync Data Stream Log`).
   - Exibir os cartões de payload JSON formatados das transmissões recentes em tempo real, destacando:
     - `event_type`: `SDR_MESSAGE_SENT`, `AI_SUGGESTION_USED`, `PIPELINE_SCORE_UPDATE`, `AUDIO_TRANSCRIPTION_COMPLETED`, `THEME_PRESET_CHANGED`, `LEAD_CONVERSATION_LOADED`.
     - `payload`: Estrutura JSON com recuo e destaque de sintaxe.
     - `auto_synced_at`: Timestamp formatado.

4. **Validação de Testes de Payload**:
   - Garantir que todos os 7 cenários de simulação enviem seus respectivos payloads sem bloquear a interface visual do operador de vendas.

Entendido? Construa o motor de auto-sync em background, a fila offline resiliente em `localStorage` e o Inspector Ledger de payloads JSON!

***
**FIM DO PROMPT.**
