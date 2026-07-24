# Prompt para Agente de IA: Detalhamento e Operação das Ações Rápidas de Decisão

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI, CRM de Vendas e SDR Automation encarregado de implementar as **Telas e Modais de Detalhamento e Operação dos Botões do Card "🚀 Ações Rápidas de Decisão"** no protótipo do **Revenue SDR OS** (`01_SDR_Prototype/index.html`).

O objetivo é transformar os 4 botões de decisão rápida em **fluxos operacionais completos e interativos**, baseados nas **melhores práticas de mercado (HubSpot, Salesforce, Outreach, Salesloft e Close)** para operação de SDRs e transbordo (handoff) de Inteligência Artificial para atendimento humano.

---

### 1. REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 / ADR-013)
1. **Frontend Server-Driven & Estático**: Escreva HTML5 semântico com Tailwind CSS + DaisyUI + Alpine.js. Não introduza frameworks SPA complexos (React, Vue).
2. **Estilização White-Label**: Todas as telas, gavetas e modais devem respeitar dinamicamente as variáveis CSS (`--p`, `--s`, `--b1`, `--bc`, etc.) e os 5 temas de cores configurados no Header (`Sakura Bloom`, `Emerald Garden`, `Ocean Breeze`, `Obsidian Night`, `Amber Warmth`).
3. **Zero Backend**: Mantenha o estado reativo simulado no Alpine.js (`dashboardApp()`) com dados mockados ricos, transições suaves, logs de auditoria e toasts de notificação feedback.

---

### 2. ESPECIFICAÇÃO DETALHADA DAS 4 AÇÕES RÁPIDAS DE DECISÃO

---

#### 📅 AÇÃO 1: `Agendar Reunião Agora` (Modal de Agendamento Comercial)

##### 🎯 Práticas de Mercado & Objetivo
Permitir a marcação instantânea de uma demonstração ou reunião de qualificação (Discovery / Demo), integrando agenda do SDR/AE, envio de convite multicanal e transição automática no funil.

##### 🏗️ Estrutura da Tela / Modal (`showScheduleMeetingModal = true`)
- **Header do Modal**: Título *"📅 Agendar Reunião Comercial com [Nome do Lead]"* + Badge de ICP/Fit Score (ex: `96/100`).
- **Resumo Executivo Contextual (AI Briefing)**:
  - Mini card com resumo das preferências do lead (ex: *"Lead solicitou reunião no período da tarde via Google Meet"*).
- **Formulário Operacional de Agendamento**:
  - **Tipo de Reunião**: Radio/Badges (*Demonstração de Produto (30m)*, *Discovery Call (15m)*, *Alinhamento Técnico (45m)*, *Fechamento (60m)*).
  - **Host / Responsável**: Selector com SDR logado ou Executivo de Contas (AE Enterprise).
  - **Seleção de Data e Horário**:
    - Sugestão Inteligente da IA (ex: *"Slots mais recomendados: Hoje 16:30 | Amanhã 10:00"*).
    - Picker de Data/Hora e integração visual com Google Calendar / Outlook.
  - **Link da Sala Virtual**: Autogeração de link Google Meet / Zoom (`https://meet.google.com/rsd-demo-x89`).
  - **Disparos Automáticos & Lembretes**:
    - `[x]` Enviar convite por E-mail com arquivo `.ics`
    - `[x]` Agendar mensagem de confirmação ativa no WhatsApp 2h antes da reunião
    - `[x]` Pausar cadência ativa do lead
- **Ação Principal**: Botão **"📅 Confirmar Agendamento e Notificar Lead"**.
- **Efeito Pós-Execução**:
  - Atualiza o estágio do lead para `"Reunião Agendada"`.
  - Registra o evento no Timeline do Lead.
  - Exibe Toast: *"✅ Reunião agendada com sucesso para [Data/Hora]!"*.

---

#### 💬 AÇÃO 2: `Assumir Conversa no WhatsApp` (Gaveta / Modal de Transbordo Handoff)

##### 🎯 Práticas de Mercado & Objetivo
Gerenciar a transição sem atrito do atendimento da IA para o SDR Humano (*Handoff Protocol*), pausando a autonomia da IA e abrindo o ambiente de bate-papo ao vivo com contexto imediato.

##### 🏗️ Estrutura da Tela / Gaveta (`showWhatsAppTakeoverModal = true`)
- **Header da Operação**: Título *"💬 Transbordo e Assumir Atendimento no WhatsApp"* + Status da IA (`🤖 IA Ativa -> 👤 Humano`).
- **Resumo para Transbordo Rápidas (AI Handover Briefing)**:
  - **Motivo do Transbordo**: Dropdown (*Objeção de Preço/Orçamento*, *Solicitação de Atendimento Humano*, *Dúvida Técnica Avançada*, *Interesse Alto em Fechamento*).
  - **Pausa da IA Autônoma**: Toggle (*Pausar IA por 24h*, *Pausar Definitivemente para este Lead*, *Manter IA em modo Co-piloto / Sugestão*).
  - **Síntese de Contexto IA**: 3 tópicos com o que o SDR precisa saber antes de mandar a primeira mensagem.
- **Interface de Live Chat / Envio Rápido**:
  - Histórico recente das últimas 3 mensagens do WhatsApp.
  - Caixa de texto para o SDR digitar a mensagem de entrada humana.
  - **Respostas Rápidas (Quick Templates)**: Botões de clique único com templates de saudação humana (ex: *"Olá [Nome], sou [SDR] especialista da equipe. Assumi aqui para te ajudar..."*).
- **Ação Principal**: Botão **"🚀 Assumir Conversa e Enviar Mensagem"** (Estilo WhatsApp Green).
- **Efeito Pós-Execução**:
  - Altera o responsável (`assigned_sdr`) para o SDR logado.
  - Zera o cronômetro de SLA de resposta do SDR.
  - Exibe Toast: *"💬 Conversa assumida! IA pausada para este lead."*.

---

#### 🔄 AÇÃO 3: `Reiniciar em Cadência` (Modal de Re-engajamento & Workflow)

##### 🎯 Práticas de Mercado & Objetivo
Permitir a recolocação do lead em um fluxo automatizado de cadência (Outbound, Re-engajamento de Leads Frios ou Nutrição), redefinindo os gatilhos de disparo.

##### 🏗️ Estrutura do Modal (`showRestartCadenceModal = true`)
- **Header do Modal**: Título *"🔄 Reiniciar Lead em Cadência de Vendas"*.
- **Configuração do Re-engajamento**:
  - **Seleção de Cadência**: Dropdown com as cadências do tenant (ex: *Cadência Outbound MedTech Enterprise*, *Re-engajamento Lead Inativo 30 dias*, *Nutrição Pós-Objeção*).
  - **Passo Inicial de Disparo**:
    - Radio Selector: `Reiniciar do Passo 1 (Boas-vindas)` vs `Selecionar Passo Específico` (ex: *Passo 3 - WhatsApp Direto com Oferta*).
  - **Agendamento de Início**:
    - `Iniciar Imediatamente` vs `Agendar para [Data/Hora]` (ex: Próxima segunda-feira às 09:00).
  - **Gestão da Memória da IA**:
    - Checkbox: `[x] Preservar histórico de objeções e dados BANT coletados anteriormente`.
- **Preview da Cadência Selecionada**:
  - Resumo dos touchpoints (ex: *5 Passos em 12 dias: WhatsApp -> E-mail -> Voz IA -> E-mail -> WhatsApp final*).
- **Ação Principal**: Botão **"🔄 Confirmar Reinício de Cadência"**.
- **Efeito Pós-Execução**:
  - Atualiza status do lead para `"Em Cadência Active"`.
  - Reseta contador de passos e agenda a próxima tarefa de IA/SDR.
  - Exibe Toast: *"🔄 Lead inserido na cadência [Nome da Cadência]!"*.

---

#### 🏷️ AÇÃO 4: `Alterar Estágio / Desqualificar` (Modal de Gestão de Funil e MQL/SQL/Perda)

##### 🎯 Práticas de Mercado & Objetivo
Permitir o avanço manual do lead pelas etapas do funil de vendas ou o descarte/desqualificação estruturada com motivo de perda para alimentar o aprendizado da IA.

##### 🏗️ Estrutura do Modal (`showChangeStageModal = true`)
- **Aba Dupla (Tabs)**: `[ 🏷️ Avançar Estágio do Funil ]` | `[ ❌ Desqualificar / Marcar Perda ]`
- **Aba 1: Avançar Estágio**:
  - Pipeline Visual Stepper (Semáforo do Funil):
    - *Lead Novo* -> *Em Qualificação* -> *Reunião Agendada* -> *SAL (Sales Accepted)* -> *SQL (Oportunidade)* -> *Proposta Enviada*.
  - Seletor de Novo Estágio com justificativa rápida opcional.
  - Botão: **"🏷️ Salvar Alteração de Estágio"**.
- **Aba 2: Desqualificar / Marcar Perda (Loss Workflow)**:
  - **Motivo de Desqualificação (Loss Reason - Campo Obrigatório)**:
    - Dropdown (*Sem Orçamento / Budget Insuficiente*, *Fora do Perfil de ICP*, *Optou por Concorrente*, *Sem Contato / Lead Incontactável*, *Projeto Adiado*).
  - **Detalhamento do Motivo (Feedback para a IA)**:
    - Textarea para observações adicionais (alimenta o algoritmo de fit do Lead Brain).
  - **Política de Reciclagem (Re-contact Policy)**:
    - Select (*Não Re-contatar*, *Reciclar em 30 dias*, *Reciclar em 60 dias*, *Reciclar em 90 dias*).
  - Botão: **"❌ Confirmar Desqualificação do Lead"** (Estilo Danger/Warning).
- **Efeito Pós-Execução**:
  - Atualiza estágio para o novo valor ou para `"Desqualificado"`.
  - Registra motivo de perda e nota de auditoria no timeline.
  - Exibe Toast: *"🏷️ Estágio do lead atualizado para [Estágio/Desqualificado]!"*.

---

### 3. ESTRUTURA DE ESTADO ALPINE.JS (`dashboardApp()`)

Adicione/Estenda no objeto retornado por `dashboardApp()` o controle de estado e métodos para suportar os 4 modais:

```js
// --- ESTADO DOS MODAIS DAS AÇÕES RÁPIDAS DE DECISÃO ---
showScheduleMeetingModal: false,
showWhatsAppTakeoverModal: false,
showRestartCadenceModal: false,
showChangeStageModal: false,
changeStageTab: 'stage', // 'stage' | 'disqualify'

// Formulários Reativos das Ações
scheduleForm: {
  meetingType: 'demo_30',
  host: 'sdr_current',
  date: '',
  time: '14:30',
  sendEmailInvite: true,
  sendWhatsappReminder: true,
  pauseCadence: true,
  meetLink: 'https://meet.google.com/rsd-demo-x89'
},

whatsappTakeoverForm: {
  reason: 'Objeção de Preço',
  pauseAiMode: '24h',
  initialMessage: ''
},

restartCadenceForm: {
  cadenceId: 'cad-01',
  startStep: 1,
  scheduleMode: 'immediate',
  preserveMemory: true
},

changeStageForm: {
  targetStage: 'Reunião Agendada',
  disqualifyReason: 'Budget Insuficiente',
  notes: '',
  recycleDays: '60'
},

// --- MÉTODOS DE ABERTURA E EXECUÇÃO ---
openQuickAction(actionType, lead) {
  if (lead) {
    this.selectedLeadJourney = Object.assign({}, this.selectedLeadJourney, lead);
  }
  
  if (actionType === 'schedule') {
    this.showScheduleMeetingModal = true;
  } else if (actionType === 'whatsapp') {
    this.showWhatsAppTakeoverModal = true;
  } else if (actionType === 'cadence') {
    this.showRestartCadenceModal = true;
  } else if (actionType === 'stage') {
    this.changeStageTab = 'stage';
    this.showChangeStageModal = true;
  } else if (actionType === 'disqualify') {
    this.changeStageTab = 'disqualify';
    this.showChangeStageModal = true;
  }
},

executeScheduleMeeting() {
  this.showScheduleMeetingModal = false;
  if (this.selectedLeadJourney) {
    this.selectedLeadJourney.currentStage = 'Reunião Agendada';
  }
  this.showNotification(`📅 Reunião agendada com sucesso com ${this.selectedLeadJourney?.name || 'o Lead'}!`, 'success');
},

executeWhatsAppTakeover() {
  this.showWhatsAppTakeoverModal = false;
  if (this.selectedLeadJourney) {
    this.selectedLeadJourney.aiAutonomy = 'Híbrido (Assumido por SDR)';
  }
  this.showNotification(`💬 Atendimento no WhatsApp assumido por ${this.currentUser?.name || 'SDR'}!`, 'success');
},

executeRestartCadence() {
  this.showRestartCadenceModal = false;
  this.showNotification(`🔄 Lead reiniciado na Cadência com sucesso!`, 'success');
},

executeChangeStage() {
  this.showChangeStageModal = false;
  const newStage = this.changeStageTab === 'stage' ? this.changeStageForm.targetStage : 'Desqualificado';
  if (this.selectedLeadJourney) {
    this.selectedLeadJourney.currentStage = newStage;
  }
  this.showNotification(`🏷️ Status atualizado para: ${newStage}`, 'info');
}
```

---

### 4. CHECKLIST DE VALIDAÇÃO DA IMPLEMENTAÇÃO

- [ ] **Integração com o Card**: Ao clicar nos botões do card *"🚀 AÇÕES RÁPIDAS DE DECISÃO"*, o modal correspondente abre de forma limpa.
- [ ] **Modal 1 (Agendar Reunião)**: Exibe sugestões inteligentes de horário, seleção de tipo de reunião, link do Google Meet e opções de convite/lembrete.
- [ ] **Modal 2 (Assumir WhatsApp)**: Exibe briefing de transbordo, motivo da assunção, opção de pausar IA e input com respostas rápidas.
- [ ] **Modal 3 (Reiniciar Cadência)**: Exibe seletor de cadências, passo de início, agendamento e preservação de memória BANT.
- [ ] **Modal 4 (Alterar Estágio / Desqualificar)**: Suporta troca visual de estágio e fluxo completo de desqualificação com motivo obrigatório e data de reciclagem.
- [ ] **Conformidade White-Label**: Todos os componentes adaptam-se perfeitamente às variáveis CSS do tema ativo no Header.
- [ ] **Feedback ao Usuário**: Todas as ações disparam notificações toast responsivas e atualizam os dados do lead em tempo real na interface.

---

**FIM DO PROMPT.**
