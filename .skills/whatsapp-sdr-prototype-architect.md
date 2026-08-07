# Skill: WhatsApp SDR Standalone Prototype Architect (`whatsapp-sdr-prototype-architect.md`)

> **Instruções para Agentes de Codificação**: Esta skill define o manual completo de engenharia de frontend, arquitetura de Standalone Micro-App (`02_ZAP_Prototype`), estado global Alpine.js (`$store.sdrApp`), controle dinâmico de painéis 3 colunas, motor de gráficos Chart.js v4, integração de sugestões RAG do Memory Brain, player de áudio Whisper e o protocolo de **Sincronização Automática em Background com o Core Revenue SDR OS (`00_SDR_architecture`)**.

---

## 1. Princípios Globais de Execução Standalone & Auto-Sync (`02_ZAP_Prototype`)

1. **Modo Isolado (Standalone Micro-App)**: A interface opera de forma autônoma e ultra-leve, sem dependência de navegação para menus administrativos do sistema central. Vendedores, SDRs e leads interagem diretamente no layout nativo inspirado no Zap Web.
2. **Sincronização Automática em Background (`dispatchAutoSyncEvent`)**: 100% das mensagens enviadas/recebidas, alternâncias de modo Copilot/Humano, sugestões RAG utilizadas, atualizações do gráfico de saúde da negociação (DHS) e eventos de áudio Whisper DEVEM ser agrupados em payloads JSON e despachados em segundo plano para a API central.
3. **Resiliência e Fila Local Offline**: Em casos de instabilidade de rede ou simulação offline (`isOfflineSimulated`), os eventos são enfileirados em `pendingSyncQueue` e persistidos em `localStorage`. Ao reconectar, a fila é descarregada automaticamente (`flush`).
4. **Inspector de Transmissão (`Auto-Sync Ledger`)**: Gaveta sanfonada no rodapé exibindo em tempo real o log de transmissões JSON enviados para a API (`coreSyncLogs`).
5. **Suporte White-Label Nativo (5 Presets CSS)**: Alternância fluida entre 5 temas CSS: `Obsidian Night` (dark mode default), `Emerald Garden`, `Ocean Breeze`, `Sakura Bloom` e `Amber Warmth`.

---

## 2. Layout Grid de 3 Colunas & Sistema de Painéis Independentes

A aplicação utiliza um Grid de 3 Colunas com gerenciamento dinâmico de layout:

- **Coluna 1 (Sidebar - Lista de Leads)**:
  - Header com avatar do operador, busca de conversas em tempo real (`searchQuery`) e badges de status/DHS de cada lead.
  - Alternador de visão mobile (`mobileActiveView`: `'chat' | 'leads' | 'ai'`).

- **Coluna 2 (Central Chat Stream)**:
  - Header da Conversa Ativa: Avatar, nome, empresa, badge de modo (`🤖+👤 IA Copiloto` vs `👤 SDR Humano`).
  - Stream de mensagens com balões Zap Web, micro-badges de sincronia e suporte a mensagens de áudio com player interativo e transcrição Whisper expandida.
  - Input de mensagem flexível com foco automático.

- **Coluna 3 (Painéis Extras de Inteligência IA)**:
  - **Painel Superior (DHS Score Chart)**: Gráfico em tempo real via **Chart.js v4** monitorando o humor/interesse da negociação em escala de -100 a +100.
  - **Painel Inferior (Sugestões RAG Memory Brain)**: Abas divididas entre `qa` (Perguntas & Respostas / Scripts) e `docs` (Manuais / Documentação API), com score de confiança, origem do RAG e botão **"Usar esta resposta"**.

- **Controle Dinâmico de Painéis (Alpine Methods)**:
  - `movePanel(panelId, direction)`: Altera a ordem dos painéis (`['leads', 'chat', 'ai']`).
  - `toggleMinimize(panelId)`: Minimiza/restaura um painel específico.
  - `toggleMaximize(panelId)`: Maximiza o painel selecionado ocupando a tela.
  - `resetPanels()`: Restaura o layout padrão de 3 colunas.

---

## 3. Estado Global Alpine.js (`Alpine.store('sdrApp')`)

```javascript
document.addEventListener('alpine:init', () => {
  Alpine.store('sdrApp', {
    // 1. Standalone Core State
    isStandalone: true,
    tenantApiKey: 'sk_live_clinica_bela_99412',
    tenantSlug: 'clinica-bela',
    coreApiEndpoint: 'https://api.revenuesdros.com/v1',
    autoSyncStatus: 'synced', // 'synced' | 'syncing' | 'offline'
    isOfflineSimulated: false,
    pendingSyncQueue: [],
    currentTheme: 'theme-obsidian',

    // 2. Active Lead & Copilot Mode
    activeLeadId: 1,
    activeLeadName: 'Amanda Sinclair',
    activeLeadPhone: '+55 47 99201-8842',
    activeLeadAvatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb',
    activeLeadCompany: 'Bela Saúde & Estética',
    activeLeadModeBadge: '🤖+👤 IA Copiloto',
    isCopilotActive: true,

    // 3. DHS (Deal Health Score) Metrics & Chart.js v4
    currentDhsScore: 78,
    dhsTrend: 'up', // 'up' | 'down' | 'stable'
    dhsVariation: '+15 pts',
    dhsHistory: [
      { time: '11:00', score: 50 },
      { time: '11:05', score: 62 },
      { time: '11:10', score: 58 },
      { time: '11:15', score: 78 }
    ],

    // 4. Panel Layout Control
    panelOrder: ['leads', 'chat', 'ai'],
    minimizedPanels: { leads: false, chat: false, ai: false },
    maximizedPanel: null,

    // 5. RAG Answer Suggestions (Memory Brain)
    searchQuery: '',
    activeTab: 'qa', // 'qa' | 'docs'
    allSuggestions: [],

    // 6. Auto-Sync Ledger & Log Stream
    isDrawerOpen: false,
    coreSyncLogs: [],

    // 7. Core Dispatcher Method
    async dispatchAutoSyncEvent(eventType, payload) {
      if (this.isOfflineSimulated) {
        this.autoSyncStatus = 'offline';
        const offlineItem = {
          sync_event_id: 'evt_off_' + Date.now(),
          app_mode: 'STANDALONE_MICRO_APP',
          tenant_key: this.tenantApiKey,
          event_type: eventType,
          lead_identifier: this.activeLeadPhone,
          collected_data: payload,
          auto_synced_at: new Date().toISOString()
        };
        this.pendingSyncQueue.push(offlineItem);
        localStorage.setItem('sdr_offline_queue', JSON.stringify(this.pendingSyncQueue));
        return;
      }

      this.autoSyncStatus = 'syncing';
      const syncItem = {
        sync_event_id: 'evt_' + Math.floor(Math.random() * 899999 + 100000),
        app_mode: 'STANDALONE_MICRO_APP',
        tenant_key: this.tenantApiKey,
        event_type: eventType,
        lead_identifier: this.activeLeadPhone,
        collected_data: payload,
        auto_synced_at: new Date().toISOString()
      };

      this.coreSyncLogs.unshift(syncItem);
      setTimeout(() => { this.autoSyncStatus = 'synced'; }, 500);
    },

    // Action Methods
    selectLead(leadId) { /* Carrega histórico, ajusta gráfico DHS e dispara LEAD_CONVERSATION_LOADED */ },
    sendMessage() { /* Adiciona balão SDR, impulsiona DHS e dispara SDR_MESSAGE_SENT */ },
    useSuggestion(sug) { /* Injeta texto no input, foca elemento e dispara AI_SUGGESTION_USED */ },
    updateDhsScore(delta, reason) { /* Recalcula score -100 a +100, atualiza gráfico e dispara PIPELINE_SCORE_UPDATE */ },
    setTheme(themeName) { /* Altera classe do body e dispara THEME_PRESET_CHANGED */ },
    toggleOfflineMode() { /* Alterna modo offline e faz flush da fila pendingSyncQueue ao reconectar */ }
  });
});
```

---

## 4. Payloads do Protocolo de Auto-Sync (`AutoSyncEvent`)

### A. Envio de Mensagem (`SDR_MESSAGE_SENT`)
```json
{
  "sync_event_id": "evt_748291",
  "app_mode": "STANDALONE_MICRO_APP",
  "event_type": "SDR_MESSAGE_SENT",
  "collected_data": {
    "leadId": 1,
    "latest_message": "Nosso plano Anual inclui até 5 canais Zap com 20% de desconto.",
    "sender_role": "SDR_COPILOT_ASSISTED",
    "sentiment_dhs_score": 78
  }
}
```

### B. Feedback de Sugestão RAG (`AI_SUGGESTION_USED`)
```json
{
  "sync_event_id": "evt_192834",
  "event_type": "AI_SUGGESTION_USED",
  "collected_data": {
    "suggestionId": "sug_1_1",
    "title": "Proposta Comercial - Plano Anual Clínica",
    "confidence": 96,
    "rag_source": "Memory Brain - Core SDR OS (Doc: Tabela_Precos_2026.pdf)"
  }
}
```

### C. Atualização de Score no CRM Pipeline (`PIPELINE_SCORE_UPDATE`)
```json
{
  "sync_event_id": "evt_583920",
  "event_type": "PIPELINE_SCORE_UPDATE",
  "collected_data": {
    "leadId": 1,
    "leadName": "Amanda Sinclair",
    "currentDhsScore": 78,
    "trend": "up",
    "reason": "Simulação de Negociação: CLOSING"
  }
}
```

### D. Transcrição de Áudio Whisper (`AUDIO_TRANSCRIPTION_COMPLETED`)
```json
{
  "sync_event_id": "evt_883192",
  "event_type": "AUDIO_TRANSCRIPTION_COMPLETED",
  "collected_data": {
    "audio_duration": "0:18",
    "whisper_transcript": "Oi pessoal! Queria saber se vocês ajudam na migração do nosso banco de leads antigo pro SDR OS."
  }
}
```

---

## 5. Diretrizes para Agentes de Codificação

1. **Nunca quebrar a execução Standalone**: O protótipo DEVE rodar abrindo `index.html` diretamente no navegador ou via `npm run dev`.
2. **Reatividade Total**: Qualquer alteração no estado global `$store.sdrApp` deve refletir imediatamente na UI, incluindo o gráfico Chart.js v4 (`refreshChart()`).
3. **Fidelidade de Design**: Manter o visual dark mode Zap Web refinado com suporte aos 5 temas DaisyUI/Tailwind CSS.
