# Skill: WhatsApp SDR Prototype Architect (`whatsapp-sdr-prototype-architect.md`)

> **Instruções para Agentes de Codificação**: Esta skill define as regras de engenharia de frontend, execução isolada (Standalone Micro-App), manipulação de estado Alpine.js, integração com Chart.js e compartilhamento automático em background com o **Revenue SDR OS** (`00_SDR_architecture`).

---

## 1. Princípios Globais de Execução Standalone & Auto-Sync

1. **Modo Isolado (Standalone Micro-App)**: A aplicação deve funcionar de forma independente de qualquer painel administrativo. Vendedores e Leads utilizam apenas esta interface simplificada estilo WhatsApp Web.
2. **Sincronização Automática em Background**: Todos os dados coletados durante o uso (histórico de conversas, métricas de sentimento DHS, objeções e ações do vendedor) DEVEM ser automaticamente agrupados e despachados em background para os endpoints do projeto principal.
3. **Fila Local Offline (Resiliência)**: Se a conexão com o servidor central falhar, os eventos devem ser armazenados temporariamente no `localStorage` via Alpine.js e sincronizados assim que a conexão for reestabelecida.
4. **Suporte White-Label Nativo**: A interface DEVE reagir dinamicamente às 5 paletas CSS (`Sakura Bloom`, `Emerald Garden`, `Ocean Breeze`, `Obsidian Night`, `Amber Warmth`).

---

## 2. Padrão do Estado Global Alpine.js (`Alpine.store('sdrApp')`)

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.store('sdrApp', {
        // Configuração de Execução Standalone
        isStandalone: true,
        tenantApiKey: 'sk_live_clinica_bela_99412',
        coreApiEndpoint: 'https://api.revenuesdros.com/v1',
        
        // Status de Auto-Sync
        autoSyncStatus: 'synced', // 'synced' | 'syncing' | 'offline'
        pendingSyncQueue: [],
        
        // Tema White-Label ativo
        currentTheme: 'theme-obsidian',
        
        // Conversa Ativa
        activeLeadId: 1,
        activeLeadName: 'Amanda Sinclair',
        activeLeadAvatar: 'https://i.pravatar.cc/150?u=amanda',
        
        // Score de Saúde da Negociação (DHS)
        currentDhsScore: 78,
        dhsTrend: 'up',
        dhsHistory: [
            { time: '11:00', score: 50 },
            { time: '11:05', score: 62 },
            { time: '11:10', score: 58 },
            { time: '11:15', score: 78 }
        ],
        
        // Sugestões de Resposta da IA (Consultadas remotamente no Core OS)
        answerSuggestions: [],
        
        // Log de Transmissão de Dados Standalone -> Core OS
        coreSyncLogs: [],
        
        // Métodos de Auto-Sync em Background
        async dispatchAutoSyncEvent(eventType, payload) {
            this.autoSyncStatus = 'syncing';
            const syncItem = {
                id: 'sync_' + Date.now(),
                event: eventType,
                tenant: this.tenantApiKey,
                timestamp: new Date().toISOString(),
                payload: payload
            };
            
            this.coreSyncLogs.unshift(syncItem);
            
            // Simulação de despacho em background
            setTimeout(() => {
                this.autoSyncStatus = 'synced';
            }, 600);
        }
    });
});
```

---

## 3. Diretrizes de Usabilidade Standalone

- **Interface Focada**: Remova qualquer menu de navegação para dashboards administrativos externos. A interface é focada unicamente na negociação ativa e nos 2 painéis de suporte (DHS + Sugestões).
- **Indicador de Conexão no Header**: `<div class="badge badge-success gap-2">🟢 Auto-Sync Ativo: Revenue SDR OS</div>`.
- **Inspector de Transmissão**: Permitir que o operador abra a gaveta `Auto-Sync Ledger` no rodapé para visualizar a transmissão automática de dados para o sistema central.
