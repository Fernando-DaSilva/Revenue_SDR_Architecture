# Prompt para Agente de IA: Subtela Pop-up de Confirmação e Autorização de Ordem ("To execute") no Copilot

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI encarregado de implementar a subtela em formato de pop-up para confirmação e autorização de execução de ordens do **SDR Copilot** no protótipo do **Revenue SDR OS** (`01_SDR_Prototype/index.html`).

Ao clicar no botão **"⚡ Executar"** (ou **"⚡ To execute"**) em qualquer card de recomendação proativa do **Copilot** (seja no widget da visão geral ou na aba dedicada *AI Copilot & Insights*), a interface deve abrir um modal interativo em pop-up com a confirmação detalhada do que será executado, parâmetros de ajuste, trava de segurança com autorização explícita e feedback visual do progresso da ordem.

---

### 1. REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 / ADR-013)
1. **Frontend Server-Driven & Estático**: Escreva HTML5 semântico com Tailwind CSS + DaisyUI + Alpine.js. Não introduza frameworks SPA complexos (React, Vue).
2. **Estilização White-Label**: O modal deve respeitar dinamicamente as variáveis e temas de cores escolhidos no Header (Sakura, Emerald, Ocean, Obsidian, Amber).
3. **Zero Backend**: Mantenha o estado reativo simulado no Alpine.js (`dashboardApp()`).

---

### 2. ESTRUTURA E REQUISITOS DA SUBTELA POP-UP (MODAL DE CONFIRMAÇÃO)

O modal deve ser um `<dialog class="modal">` do DaisyUI controlado pela flag de estado `showExecuteModal` no Alpine.js, contendo as seguintes seções:

#### 🟢 A. Cabeçalho do Modal
- Iconografia marcante (`🤖⚡`) e título claro: **"Confirmação de Ordem de Execução — SDR Copilot"**.
- Badges dinâmicos com a **Categoria** da ação (ex: *RE-ENGAJAMENTO VIA IA*, *OTIMIZAÇÃO DE SCRIPT*), o **Tempo** de geração e o **Impacto Estimado** (ex: *+8 Reuniões est.*, *Conversão +14%*).
- Botão de fechar `✕`.

#### 📋 B. Painel de Detalhes da Execução (Escopo & Impacto)
- **Título & Descrição detalhada da Ordem**: Apresentar exatamente o que a IA identificou e o plano de ação sugerido.
- **Grid de Metadados da Operação**:
  - **Público / Volume Afetado**: Ex: *34 Leads parados há 24h na Qualificação*.
  - **Nível de Risco**: Badge visual (*Médio Risco*, *Baixo Risco* ou *Alto Risco*).
  - **Canais Envolvidos**: Badges com os canais (WhatsApp, E-mail, Ligação).
  - **Agentes Executores**: Ex: *SDR-01 IA (Lead Inbound)*.
- **Detalhamento do Script / Prompt**: Caixa destacada mostrando o resumo das alterações de script ou cadência que serão aplicadas.

#### ⚙️ C. Configurações de Envio / Ajuste Fino
- **Modo de Agendamento**: Seletor rádio ou tabs (*Executar Imediatamente* vs *Agendar para Horário Comercial*).
- **Opções de Notificação**: Checkbox para notificar a equipe comercial via Slack/WhatsApp ao concluir a ordem.

#### 🔐 D. Trava de Autorização e Segurança
- **Caixa de Consentimento Explícito**: Checkbox de confirmação com texto claro:
  - `[ ] Declaro que revisei os detalhes e autorizo a execução desta ordem pelo SDR Copilot.`
- O botão principal de ação **"⚡ Confirmar e Autorizar Execução"** DEVE permanecer **desabilitado (`:disabled="!executeAuthorized"`)** enquanto o usuário não marcar a caixa de autorização.

#### ⏳ E. Fluxo de Processamento & Feedback em Tempo Real
- Ao clicar em confirmar, o modal transita para o estado de processamento (`executeProcessing = true`):
  - Barra de progresso animada (`progress progress-primary w-full`).
  - Feed de logs passo a passo simulados em tempo real com delay:
    - `[1/3] Validando critérios de eligibilidade e opt-in dos leads...`
    - `[2/3] Atualizando parâmetros dos Agentes SDR IA...`
    - `[3/3] Disparando cadência e registrando auditoria...`
- Ao concluir (`executeSuccess = true`):
  - Card verde de sucesso com mensagem de confirmação e **ID de Auditoria da Ordem** (ex: `#ORD-2026-0891`).
  - Toast de notificação na aplicação.
  - Atualização do status da recomendação na lista (ex exibindo badge *"✅ Executado"* ou ocultando da fila de pendentes).

---

### 3. MODIFICAÇÕES NO ESTADO ALPINE.JS (`dashboardApp()`)

Adicionar/Atualizar as seguintes propriedades e métodos no objeto retornado por `dashboardApp()`:

```js
// Propriedades do Modal de Confirmação de Ordem Copilot
showExecuteModal: false,
selectedExecuteAction: null,
executeAuthorized: false,
executeProcessing: false,
executeSuccess: false,
executeStep: 1,
executeLogs: [],
executeForm: {
  mode: 'immediate',
  notifyTeam: true
},

// Métodos
openExecuteModal(item) {
  this.selectedExecuteAction = item;
  this.executeAuthorized = false;
  this.executeProcessing = false;
  this.executeSuccess = false;
  this.executeStep = 1;
  this.executeLogs = [];
  this.showExecuteModal = true;
},

closeExecuteModal() {
  this.showExecuteModal = false;
  this.selectedExecuteAction = null;
},

confirmAndExecuteAction() {
  if (!this.executeAuthorized) return;
  
  this.executeProcessing = true;
  this.executeLogs = ['[1/3] Validando critérios de eligibilidade dos leads...'];
  
  setTimeout(() => {
    this.executeLogs.push('[2/3] Atualizando diretivas do Agente SDR-01 IA...');
  }, 600);
  
  setTimeout(() => {
    this.executeLogs.push('[3/3] Ordem executada com sucesso e auditada.');
    this.executeProcessing = false;
    this.executeSuccess = true;
    
    // Marca item como executado
    if (this.selectedExecuteAction) {
      this.selectedExecuteAction.executed = true;
    }
    
    this.showNotification(`⚡ Ordem "${this.selectedExecuteAction?.title}" autorizada e executada!`, 'success');
  }, 1400);
}
```

---

### 4. CHECKLIST DE VALIDAÇÃO
- [ ] Ao clicar em **"⚡ Executar"** em qualquer sugestão do Copilot, o modal pop-up abre perfeitamente.
- [ ] O modal exibe todos os detalhes da ação (impacto, risco, canais, volume de leads).
- [ ] O botão **"⚡ Confirmar e Autorizar Execução"** fica desabilitado até a caixa de autorização ser marcada.
- [ ] O fluxo de confirmação exibe progresso animado e logs passo a passo.
- [ ] Ao finalizar, a tela exibe comprovante de sucesso com ID de auditoria e notificação toast.
- [ ] O modal adapta-se perfeitamente a todos os 5 temas de cores do Header (White-Label).

***

**FIM DO PROMPT.**
