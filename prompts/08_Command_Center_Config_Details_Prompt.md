# Prompt para Agente de IA: Telas de Configuração de Opções e Detalhes do Command Center (01_SDR_Prototype)

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI encarregado de implementar as **telas de configuração de opções e detalhamento dos cards do Command Center** no protótipo do **Revenue SDR OS** (`01_SDR_Prototype/index.html`).

O objetivo desta tarefa é expandir a experiência interativa dos 4 cards principais de KPI do **Command Center** (*Leads Contatados*, *Taxa de Qualificação BANT*, *Reuniões Agendadas SQL* e *Pipeline de MRR Gerado*). Ao clicar em qualquer um destes cards (ou em seu botão de engrenagem/detalhes), o sistema deve abrir modais e sub-telas dedicadas para navegação profunda nos dados, ajuste de parâmetros, metas, construtor de fórmulas de cálculo, gestão de agenda/slots de vendedores e sincronização de calendários externos.

---

### 1. REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 / ADR-013)
1. **Frontend Server-Driven & Estático**: Escreva HTML5 semântico com Tailwind CSS + DaisyUI + Alpine.js. Não introduza frameworks SPA complexos (React, Vue).
2. **Estilização White-Label**: Todas as telas e modais criados devem respeitar dinamicamente as variáveis CSS e temas de cores selecionados no Header (`Sakura Bloom`, `Emerald Garden`, `Ocean Breeze`, `Obsidian Night`, `Amber Warmth`).
3. **Zero Backend**: Mantenha o estado reativo simulado no Alpine.js (`dashboardApp()`) com dados mockados ricos e consistentes.

---

### 2. ESTRUTURA E REQUISITOS DAS TELAS DE DETALHES E CONFIGURAÇÃO (TODOS 1 A 4)

---

#### 📈 TODO 1: Leads Contatados — Visão Detalhada, Seletor de Período Customizado e Integração com Pipeline de Leads

Ao clicar no card **"Leads Contatados"** (ou no seu atalho de drill-down), a interface deve abrir a sub-tela/modal **"Detalhamento de Leads Contatados"** (`showLeadsDetailModal = true`):

1. **Barra Superior de Filtro Temporal e Seletor de Período**:
   - Selector com os botões de atalho: `Hoje`, `Semana`, `Mês` e `Personalizado`.
   - **Calendário Interativo de Escolha de Período (Date Range Picker)**:
     - Quando a opção `Personalizado` estiver ativa, exibir um date picker estilizado com campos para **Data Inicial** (`customStartDate`) e **Data Final** (`customEndDate`).
     - Incluir botão **"Aplicar Período"** que filtra dinamicamente a contagem e a lista de leads contatados na janela temporal escolhida.
2. **Correlação Direta com o Pipeline de Leads**:
   - Os dados exibidos nesta tela devem derivar da mesma base de dados usada no menu **"Pipeline de Leads"**, mantendo total consistência de status (*Novo Lead*, *Em Abordagem*, *Qualificado BANT*, *Reunião Agendada*, *Desqualificado*).
   - Exibir badges do estágio atual do lead no funil, canal de contato de origem (*Zap*, *E-mail*, *LinkedIn*, *Voz*) e data/hora do último contato.
3. **Tabela Interativa de Leads Contatados**:
   - Colunas: *Lead / Empresa*, *Canal de Abordagem*, *Estágio no Pipeline*, *Data do Último Contato*, *SDR Responsável (IA ou Humano)*, *Score BANT* e *Ações*.
   - Filtros rápidos por canal de prospecção e status de resposta.
   - **Ações Rápidas em cada linha**:
     - Botão `👁️ Ver Conversa`: abre o modal de Raio-X com o histórico do chat.
     - Botão `🔗 Abrir no Pipeline`: redireciona a visualização para a tab do *Pipeline de Leads* já pré-filtrada com o lead selecionado.

---

#### 🎯 TODO 2: Taxa de Qualificação (BANT) — Detalhamento dos Scores e Construtor de Fórmulas de Cálculo

Ao clicar no card **"Taxa de Qualificação (BANT)"**, a interface deve abrir o modal **"Painel de Qualificação e Configuração BANT"** (`showBantConfigModal = true`) composto por 2 abas principais:

1. **Aba 1: Detalhamento dos Registros & Scores (`bantModalTab = 'records'`)**:
   - Tabela analítica com todos os leads que compõem o percentual de qualificação apresentado no Command Center.
   - Breakdown detalhado das pontuações nos 4 pilares do BANT:
     - 💵 **Budget** (Orçamento disponível): 0 a 100.
     - 👑 **Authority** (Poder de decisão): 0 a 100.
     - 🎯 **Need** (Necessidade/Dor identificada): 0 a 100.
     - ⏳ **Timeline** (Urgência para contratação): 0 a 100.
   - Score Final Médio (ex: `82/100`) e Status de Qualificação (*Qualificado SQL*, *Em Análise*, *Desqualificado*).
2. **Aba 2: Configuração das Fórmulas de Cálculo & Pesos (`bantModalTab = 'formula'`)**:
   - **Sliders/Inputs de Pesos dos Pilares BANT**:
     - Slider para ajustar o peso de cada pilar no cálculo final (ex: Budget = 30%, Authority = 25%, Need = 25%, Timeline = 20%). A soma total deve computar 100% dinamicamente.
   - **Definição de Nota de Corte para Qualificação SQL**:
     - Input numérico para ajustar a pontuação mínima para o lead ser considerado "Qualificado" (ex: `Score >= 70`).
   - **Fórmula de Cálculo da Taxa Global**:
     - Exibição visual da fórmula matemática utilizada:
       $$\text{Taxa de Qualificação (\%)} = \left( \frac{\text{Leads com Score } \ge \text{Corte}}{\text{Total de Leads Analisados}} \right) \times 100$$
   - Botão **"💾 Salvar Nova Formulação"**: atualiza instantaneamente a Taxa de Qualificação BANT no Command Center e recomputa a porcentagem exibida no card.

---

#### 📅 TODO 3: Reuniões Agendadas — Configuração de Metas, Gestão de Agenda/Slots e Sincronização Externa

Ao clicar no card **"Reuniões Agendadas (SQL)"**, a interface deve abrir o modal **"Gestão de Reuniões, Metas e Agendas"** (`showMeetingsConfigModal = true`) composto por 3 abas principais:

1. **Aba 1: Configuração de Metas Comercial (`meetingsModalTab = 'goals'`)**:
   - Definição do número de metas globais por contexto temporal:
     - Meta **Hoje** (ex: `8 reuniões`).
     - Meta **Semana** (ex: `35 reuniões`).
     - Meta **Mês** (ex: `150 reuniões`).
   - Distribuição de metas por SDR / Vendedor individual com barra de progresso visual (% atingido).
2. **Aba 2: Schedule & Slots Disponíveis (CRUD de Horários) (`meetingsModalTab = 'slots'`)**:
   - Seletor de Vendedor / Representante Comercial (ex: *Todos*, *Carlos SDR*, *Ana Account Executive*).
   - Grade semanal/diária de disponibilidade com visualização de slots livres, ocupados e bloqueados.
   - **CRUD Completo de Slots**:
     - Botão `➕ Adicionar Slot`: cria novo horário disponível na agenda do vendedor escolhido.
     - Botão `✏️ Editar / Bloquear Slot`: permite marcar horários como indisponíveis (férias, treinamento, almoço).
     - Botão `❌ Desmarcar / Cancelar Reunião`: libera o slot e envia notificação de cancelamento simulada.
3. **Aba 3: Sincronização com Calendários Externos (`meetingsModalTab = 'sync'`)**:
   - Painel de integração com provedores de calendário externos:
     - **Google Calendar**: Status (*Conectado* - `vendas@empresa.com`), Toggle de ativação, Botão *Sincronizar Agora*.
     - **iCal / Apple Calendar**: URL de Feed ICS dinâmico para cópia e status de sincronização.
     - **Microsoft Outlook 365**: Status (*Desconectado*), Botão *Conectar Conta*.
   - Configurações de Sync: Opção de *Sincronização Bidirecional*, *Duração padrão da reunião (30min / 45min / 60min)* e *Intervalo entre reuniões (Buffer 15min)*.

---

#### 💰 TODO 4: Pipeline de MRR Gerado — Detalhamento do Historico e Construtor de Fórmulas de Valor

Ao clicar no card **"Pipeline de MRR Gerado"**, a interface deve abrir o modal **"Detalhamento & Fórmulas de Pipeline MRR"** (`showMrrConfigModal = true`) composto por 2 abas principais:

1. **Aba 1: Detalhamento & Histórico de Geração de Pipeline (`mrrModalTab = 'history'`)**:
   - Tabela histórica das oportunidades e reuniões convertidas em pipeline de receita recorrente.
   - Colunas: *Data de Geracao*, *Empresa / Lead*, *Estágio no Funil*, *MRR Estimado (R$)*, *Setup Fee / Adicional (R$)*, *Probabilidade de Fechamento (%)* e *Valor Ponderado (R$)*.
   - Gráfico/Barra temporal mostrando a evolução da geração de MRR ao longo dos últimos meses.
2. **Aba 2: Configuração de Fórmulas e Regras de Valor (`mrrModalTab = 'formula'`)**:
   - **Definição dos Métodos de Cálculo do Total Exibido**:
     - Alternância de modelo de cálculo do card:
       - Mode A: *MRR Ponderado por Probabilidade* ($\sum \text{MRR} \times \text{Probabilidade}$).
       - Mode B: *MRR Nominal Total* ($\sum \text{MRR}$ puro sem ponderação).
       - Mode C: *MRR Contracted + Estimated Setup Fee*.
   - **Tabela de Probabilidades por Estágio do Funil**:
     - Configuração dos percentuais de peso para cada fase do pipeline:
       - *Prospecção*: `10%`
       - *Engajado IA*: `25%`
       - *Qualificado BANT*: `50%`
       - *Reunião Realizada*: `75%`
       - *Proposta Aceita*: `90%`
   - **Ajuste de Taxa de Retenção e Multiplicadores LTV**:
     - Inputs para definir se o card exibe o MRR mensal ou o valor total do contrato (ACV - Annual Contract Value).
   - Botão **"💾 Recalcular e Salvar Métricas de Pipeline"**: recalcula dinamicamente os valores de `R$ 485.000` e `68k MRR` exibidos no card do Command Center.

---

### 3. ESTRUTURA DE ESTADO ALPINE.JS (`dashboardApp()`)

Adicionar e estender no objeto retornado por `dashboardApp()` as seguintes variáveis e funções de controle:

```js
// --- ESTADO DOS MODAIS DO COMMAND CENTER CONFIG ---
showLeadsDetailModal: false,
showBantConfigModal: false,
showMeetingsConfigModal: false,
showMrrConfigModal: false,

// Sub-abas internas dos modais
bantModalTab: 'records',       // 'records' | 'formula'
meetingsModalTab: 'goals',     // 'goals' | 'slots' | 'sync'
mrrModalTab: 'history',        // 'history' | 'formula'

// --- TODO 1: LEADS CONTATADOS & FILTRO DE DATA ---
leadsDateFilter: 'semana',     // 'hoje' | 'semana' | 'mes' | 'custom'
customStartDate: '2026-07-01',
customEndDate: '2026-07-23',
leadsDetailSearch: '',
selectedLeadFilterStatus: 'all',

// --- TODO 2: FÓRMULAS E PESOS BANT ---
bantWeights: {
  budget: 30,
  authority: 25,
  need: 25,
  timeline: 20,
  cutoffScore: 70
},
bantCalculatedRate: 38.5,
bantAverageScore: 82,

// --- TODO 3: METAS, SLOTS E CALENDÁRIOS ---
meetingGoals: {
  hoje: 8,
  semana: 35,
  mes: 150
},
selectedSellerSlotFilter: 'all',
sellerSchedules: [
  { id: 1, seller: 'Carlos Silva (SDR)', day: 'Segunda', time: '09:00 - 09:45', status: 'available' },
  { id: 2, seller: 'Carlos Silva (SDR)', day: 'Segunda', time: '10:00 - 10:45', status: 'booked', lead: 'TechCorp' },
  { id: 3, seller: 'Ana Paula (AE)', day: 'Terça', time: '14:00 - 14:45', status: 'blocked', reason: 'Treinamento' }
],
externalCalendars: {
  google: { connected: true, account: 'vendas@clinica-bela.com', syncStatus: 'Ativo (há 5 min)' },
  ical: { connected: true, feedUrl: 'https://api.sdr-os.local/v1/calendar/feed.ics' },
  outlook: { connected: false, account: '' }
},

// --- TODO 4: FÓRMULAS E PIPELINE DE MRR ---
mrrCalculationMode: 'weighted', // 'weighted' | 'nominal' | 'acv'
stageProbabilities: {
  prospeccao: 10,
  engajado: 25,
  bant: 50,
  reuniao: 75,
  proposta: 90
},

// --- MÉTODOS DE AÇÃO E NAVEGAÇÃO ---
openCardDetailModal(cardType) {
  if (cardType === 'leads') this.showLeadsDetailModal = true;
  if (cardType === 'bant') this.showBantConfigModal = true;
  if (cardType === 'meetings') this.showMeetingsConfigModal = true;
  if (cardType === 'mrr') this.showMrrConfigModal = true;
},

saveBantFormula() {
  const totalWeight = parseInt(this.bantWeights.budget) + parseInt(this.bantWeights.authority) + 
                    parseInt(this.bantWeights.authority) + parseInt(this.bantWeights.timeline);
  if (totalWeight !== 100) {
    this.showNotification('A soma dos pesos do BANT deve ser exatamente 100%!', 'warning');
    return;
  }
  this.showNotification('Fórmula e nota de corte do BANT salvas com sucesso!', 'success');
},

saveMeetingGoals() {
  this.showNotification('Metas de reuniões atualizadas para o time comercial!', 'success');
},

toggleCalendarSync(provider) {
  if (this.externalCalendars[provider]) {
    this.externalCalendars[provider].connected = !this.externalCalendars[provider].connected;
    const statusText = this.externalCalendars[provider].connected ? 'conectado' : 'desconectado';
    this.showNotification(`Calendário ${provider.toUpperCase()} ${statusText}!`, 'info');
  }
},

saveMrrFormula() {
  this.showNotification('Fórmulas de cálculo de MRR recalculadas e aplicadas ao Command Center!', 'success');
}
```

---

### 4. CHECKLIST DE VALIDAÇÃO

- [ ] **Leads Contatados**:
  - [ ] O clique no card "Leads Contatados" abre o modal detalhado.
  - [ ] O filtro de período (`Hoje`, `Semana`, `Mês`, `Personalizado`) funciona e abre o Date Range Picker em modo personalizado.
  - [ ] A lista de leads contatados reflete com precisão os dados correlacionados do menu "Pipeline de Leads".
- [ ] **Taxa de Qualificação (BANT)**:
  - [ ] Exibe os registros de leads que formaram o percentual de qualificação.
  - [ ] O painel de fórmulas permite alterar sliders de pesos (Budget, Authority, Need, Timeline) e nota de corte.
  - [ ] A alteração da fórmula recomputa e salva a nova porcentagem no Command Center.
- [ ] **Reuniões Agendadas (SQL)**:
  - [ ] Permite definir e salvar a meta de reuniões para Hoje, Semana e Mês.
  - [ ] Grade de slots dos vendedores permite visualização, bloqueio e adição (CRUD).
  - [ ] Exibe opções funcionais de sincronização com Google Calendar, iCal e Outlook.
- [ ] **Pipeline de MRR Gerado**:
  - [ ] Apresenta a tabela histórica detalhada de geração de receita e oportunidades.
  - [ ] Permite alternar os modos de cálculo (MRR Ponderado vs Nominal vs ACV) e ajustar probabilidades por estágio.
  - [ ] O recálculo atualiza em tempo real os valores exibidos no card do Command Center.
- [ ] **White-Label & Design**:
  - [ ] Todos os novos modais e componentes se adaptam instantaneamente aos 5 temas de cores do Header.

***

**FIM DO PROMPT.**
