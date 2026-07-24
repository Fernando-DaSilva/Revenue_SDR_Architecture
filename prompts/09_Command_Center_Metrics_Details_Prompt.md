# Prompt para Agente de IA: Detalhamento de Totais e Fórmulas de Cálculo do Command Center (Tempo Médio, Custo por Agendamento, Autonomia da IA)

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI encarregado de implementar as **telas de detalhamento dos totais e construtores de fórmulas de cálculo** para os 3 cards estratégicos do **Command Center** no protótipo do **Revenue SDR OS** (`01_SDR_Prototype/index.html`):
1. ⏱️ **Tempo Médio no Funil** (ex: `3.2 Dias`)
2. 💰 **Custo por Agendamento** (ex: `R$ 14,80`)
3. 🤖 **Autonomia da IA** (ex: `84.2% Sem Humano`)

Ao clicar em qualquer um destes 3 cards (ou nos botões de detalhe/drill-down), o sistema deve abrir modais e sub-telas analíticas dedicadas para visualização detalhada dos componentes que formam esses totais, decomposição por etapas/origens, histórico de dados e construtores de fórmulas matematicamente interativos para recalcular as métricas em tempo real.

---

### 1. REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 / ADR-013)
1. **Frontend Server-Driven & Estático**: Escreva HTML5 semântico com Tailwind CSS + DaisyUI + Alpine.js. Não introduza frameworks SPA complexos (React, Vue).
2. **Estilização White-Label**: Todas as telas e modais criados devem respeitar dinamicamente as variáveis CSS e temas de cores selecionados no Header (`Sakura Bloom`, `Emerald Garden`, `Ocean Breeze`, `Obsidian Night`, `Amber Warmth`).
3. **Zero Backend**: Mantenha o estado reativo simulado no Alpine.js (`dashboardApp()`) com dados mockados ricos, consistentes e dinamicamente recalculáveis.

---

### 2. ESTRUTURA E REQUISITOS DAS TELAS DE DETALHES E FÓRMULAS (TODOS 1 A 3)

---

#### ⏱️ TODO 1: Tempo Médio no Funil — Decomposição por Estágios, Identificação de Gargalos e Construtor de Fórmulas de SLA

Ao clicar no card **"Tempo Médio no Funil"** (`3.2 Dias`), a interface deve abrir o modal **"Detalhamento e Cálculo do Tempo Médio no Funil"** (`showFunnelTimeModal = true`) composto por 2 abas principais:

1. **Aba 1: Detalhamento por Estágio e Decomposição (`funnelTimeModalTab = 'breakdown'`)**:
   - **Visualização de Funil com Lead Time por Etapa**:
     - Card visual em fluxo mostrando o tempo médio de permanência em cada transição:
       - *Entrada → 1ª Abordagem IA*: `0.1 Dias` (~2h) [🟢 Dentro do SLA]
       - *1ª Abordagem → Resposta/Engajamento*: `0.8 Dias` [🟢 Dentro do SLA]
       - *Engajamento → Qualificação BANT*: `1.1 Dias` [🟡 Alerta SLA]
       - *Qualificação BANT → Agendamento SQL*: `1.2 Dias` [🟢 Dentro do SLA]
     - Destaque automático da **Etapa Gargalo (Bottleneck Stage)** com indicador visual em contraste.
   - **Filtro de Cohort e Segmentação**:
     - Filtros por **Canal** (*Todos*, *WhatsApp*, *E-mail*, *LinkedIn*, *Voz*), **Porte do Lead** (*Enterprise*, *Mid-Market*, *SMB*) e **SDR Responsável / Agente IA**.
   - **Tabela de Leads no Funil e Tempos de Ciclo**:
     - Colunas: *Lead / Empresa*, *Canal de Origem*, *Data de Entrada*, *Estágio Atual*, *Dias no Estágio*, *Tempo Total Decorrido (Dias)* e *Status do SLA*.
     - Ação rápida: `👁️ Ver Jornada` para visualizar o timeline de mensagens e eventos do lead.

2. **Aba 2: Construtor de Fórmulas e Regras de Tempo (`funnelTimeModalTab = 'formula'`)**:
   - **Seleção do Modelo de Cálculo de Tempo**:
     - Radio selector / Buttons para escolher o algoritmo de apuração:
       - **Média Aritmética Simples**: Média direta de dias do total de conversões.
       - **Mediana (P50 - Recomendado)**: Elimina distorções de leads estagnados por meses.
       - **Percentil 90 (P90 / Pior Caso)**: Medição de tempo máximo para 90% dos casos.
   - **Filtro Truncador de Outliers (Leads Parados)**:
     - Input/Slider: *Ignorar leads parados a mais de X dias* (ex: `30 dias`).
   - **Exibição Matemática Interativa da Fórmula**:
     $$\text{Tempo Médio} = \frac{\sum_{i=1}^{N} (\text{Data Agendamento}_i - \text{Data Entrada}_i)}{N_{\text{válidos}}}$$
   - Botão **"💾 Salvar e Recalcular Tempo do Funil"**: atualiza instantaneamente o valor exibido no card do Command Center (ex: de `3.2 Dias` para `2.9 Dias`).

---

#### 💰 TODO 2: Custo por Agendamento — Decomposição Estrutural de Custos (Mídia + IA + Operacional) e Fórmulas de CPAg

Ao clicar no card **"Custo por Agendamento"** (`R$ 14,80`), a interface deve abrir o modal **"Detalhamento Estrutural e Fórmulas de Custo por Agendamento"** (`showCostPerBookingModal = true`) composto por 2 abas principais:

1. **Aba 1: Detalhamento da Composição de Custos (`costModalTab = 'breakdown'`)**:
   - **Cards de Decomposição do Total (Custo Blended de R$ 14,80 por Reunião)**:
     - 📢 **Investimento em Mídia / Ads**: `R$ 8,50 / agendamento` (57.4% do total)
     - 🤖 **Infraestrutura IA & APIs** (LLMs + WhatsApp API + Twilio): `R$ 3,80 / agendamento` (25.7% do total)
     - 👤 **Operação Humana / Gestão**: `R$ 2,50 / agendamento` (16.9% do total)
   - **Gráfico de Rosca / Donut Chart ou Barras de Distribuição**:
     - Visualização rápida da proporção entre Mídia, APIs de IA e Custo Operacional.
   - **Tabela de Custos por Origem / Campanha**:
     - Colunas: *Origem / Campanha*, *Investimento Total (R$)*, *Agendamentos Gerados*, *Custo por Agendamento (R$)* e *Eficiência vs Meta*.
     - Destaque para origens com melhor ROI e menor custo unitário.

2. **Aba 2: Construtor de Fórmulas e Parâmetros de Custo (`costModalTab = 'formula'`)**:
   - **Modo de Apuração de Custo do Card**:
     - Switch/Select para escolher o que compõe o card no Command Center:
       - **Custo Blended Total** (Mídia + Infra IA + Operação).
       - **Custo Computacional Direto de IA** (Somente Tokens LLM + APIs por agendamento).
       - **Custo de Aquisição Direto (Ad Spend / Agendamento)**.
   - **Painel de Parâmetros e Custos Fixos/Variáveis**:
     - Input: *Custo Médio por 1k Tokens LLM* (ex: `R$ 0,02`).
     - Input: *Custo Fixo Mensal de Software / Servidores* (ex: `R$ 1.500,00`).
     - Input: *Verba Total de Mídia no Período* (ex: `R$ 12.750,00`).
   - **Exibição da Fórmula do Custo por Agendamento**:
     $$\text{CPAg} = \frac{\text{Custo Mídia} + \text{Custo APIs IA} + \text{Custo Operacional}}{\text{Total de Reuniões Agendadas (SQL)}}$$
   - **Definição da Meta de Custo Máximo (SLA FinOps)**:
     - Input para definir o teto de custo (ex: `R$ 20,00`). Caso ultrapasse, exibir badge de alerta no Command Center.
   - Botão **"💾 Recalcular e Aplicar Custo por Agendamento"**: salva as alterações e atualiza o card no Command Center.

---

#### 🤖 TODO 3: Autonomia da IA — Análise de Interações (Zero Touch vs Handoff), Motivos de Transbordo e Fórmulas

Ao clicar no card **"Autonomia da IA"** (`84.2% Sem Humano`), a interface deve abrir o modal **"Detalhamento de Autonomia da IA e Regras de Transbordo"** (`showAiAutonomyModal = true`) composto por 2 abas principais:

1. **Aba 1: Decomposição de Interações e Motivos de Transbordo (`autonomyModalTab = 'breakdown'`)**:
   - **Distribuição de Atendimento em 3 Categorias**:
     - ⚡ **100% Autônomo (Zero Touch)**: `84.2%` (842 agendamentos sem nenhuma intervenção humana).
     - 🤝 **Híbrido / Handoff Assistido**: `11.0%` (110 conversas onde a IA iniciou e o humano assumiu).
     - 👨‍💻 **100% Humano (Manual Overrule)**: `4.8%` (48 conversas tratadas diretamente por SDRs).
   - **Análise Top Motivos de Transbordo (Handoff Reasons)**:
     - Gráfico ou lista categorizada dos motivos que levaram a IA a transferir para humanos:
       1. *Solicitação Explícita do Lead*: `42%` dos transbordos.
       2. *Objeção Técnica Não Mapeada*: `28%` dos transbordos.
       3. *Dúvida Fiscais/Jurídicas*: `18%` dos transbordos.
       4. *Gatilho de Sentimento Negativo*: `12%` dos transbordos.
   - **Tabela de Atendimentos Analisados**:
     - Colunas: *Lead / Conversa*, *Agente IA*, *Total Mensagens*, *Mensagens IA*, *Mensagens Humano*, *Status de Autonomia* e *Gatilho de Handoff*.
     - Ação rápida: `💬 Ver Chat Logs` para examinar o momento exato em que ocorreu a intervenção humana.

2. **Aba 2: Fórmulas de Autonomia e Ajuste de Agressividade (`autonomyModalTab = 'formula'`)**:
   - **Métrica Base de Cálculo da Autonomia**:
     - Radio Selector:
       - **Baseado em Conversas Concluídas / Agendadas** (% de reuniões fechadas sem toque humano).
       - **Baseado em Mensagens Totais Enviadas** ($\frac{\text{Mensagens IA}}{\text{Mensagens IA + Humano}}$).
       - **Baseado em Qualificação BANT Finalizada**.
   - **Seletor de Nível de Autonomia do Agente (Autonomy Level)**:
     - Range slider com 3 modos:
       - *Conservador (Transborda em caso de dúvida)*.
       - *Balanceado (Padrão - Handoff com alta confiança)*.
       - *Autônomo Extremo (Tenta resolver todas as objeções antes de transferir)*.
   - **Exibição da Fórmula Visual**:
     $$\text{Taxa de Autonomia (\%)} = \left( \frac{\text{Agendamentos 100\% Autônomos (Zero Touch)}}{\text{Total de Agendamentos Gerados}} \right) \times 100$$
   - Botão **"💾 Salvar Parâmetros de Autonomia"**: recalcula o percentual e atualiza o card no Command Center (ex: `84.2% Sem Humano`).

---

### 3. ESTRUTURA DE ESTADO ALPINE.JS (`dashboardApp()`)

Adicionar e estender no objeto retornado por `dashboardApp()` as seguintes variáveis e funções de controle:

```js
// --- ESTADO DOS MODAIS DE MÉTRICAS DO COMMAND CENTER ---
showFunnelTimeModal: false,
showCostPerBookingModal: false,
showAiAutonomyModal: false,

// Sub-abas internas dos modais
funnelTimeModalTab: 'breakdown',    // 'breakdown' | 'formula'
costModalTab: 'breakdown',          // 'breakdown' | 'formula'
autonomyModalTab: 'breakdown',      // 'breakdown' | 'formula'

// --- TODO 1: TEMPO MÉDIO NO FUNIL ---
funnelTimeConfig: {
  calculationMode: 'median',        // 'mean' | 'median' | 'p90'
  ignoreOutliersDays: 30,
  selectedChannel: 'all',
  selectedSegment: 'all'
},
funnelTimeValue: '3.2 Dias',
funnelStagesBreakdown: [
  { stage: 'Entrada -> 1ª Abordagem IA', avgDays: 0.1, slaTarget: 0.2, status: 'ok' },
  { stage: '1ª Abordagem -> Engajamento', avgDays: 0.8, slaTarget: 1.0, status: 'ok' },
  { stage: 'Engajamento -> BANT Qualificado', avgDays: 1.1, slaTarget: 0.8, status: 'warning' },
  { stage: 'BANT -> Reunião Agendada', avgDays: 1.2, slaTarget: 1.5, status: 'ok' }
],

// --- TODO 2: CUSTO POR AGENDAMENTO ---
costConfig: {
  calculationMode: 'blended',       // 'blended' | 'ai_direct' | 'ad_spend'
  llmTokenCostPer1k: 0.02,
  fixedSoftwareCost: 1500.00,
  monthlyAdSpend: 12750.00,
  targetCostLimit: 20.00
},
costPerBookingValue: 'R$ 14,80',
costBreakdownComponents: {
  mediaSpend: 8.50,
  aiInfra: 3.80,
  humanOperations: 2.50
},

// --- TODO 3: AUTONOMIA DA IA ---
autonomyConfig: {
  metricBase: 'bookings',          // 'bookings' | 'messages' | 'bant'
  aggressivenessLevel: 'balanced'  // 'conservative' | 'balanced' | 'extreme'
},
aiAutonomyValue: '84.2% Sem Humano',
autonomyBreakdown: {
  zeroTouchPercent: 84.2,
  zeroTouchCount: 842,
  hybridPercent: 11.0,
  hybridCount: 110,
  humanPercent: 4.8,
  humanCount: 48
},
handoffReasons: [
  { reason: 'Solicitação Explícita do Lead', percentage: 42, count: 46 },
  { reason: 'Objeção Técnica Não Mapeada', percentage: 28, count: 31 },
  { reason: 'Dúvida Fiscais/Jurídicas', percentage: 18, count: 20 },
  { reason: 'Gatilho de Sentimento Negativo', percentage: 12, count: 13 }
],

// --- MÉTODOS DE AÇÃO E NAVEGAÇÃO DOS CARDS ---
openMetricDetailModal(metricType) {
  if (metricType === 'funnelTime') this.showFunnelTimeModal = true;
  if (metricType === 'costPerBooking') this.showCostPerBookingModal = true;
  if (metricType === 'aiAutonomy') this.showAiAutonomyModal = true;
},

recalculateFunnelTime() {
  if (this.funnelTimeConfig.calculationMode === 'median') {
    this.funnelTimeValue = '3.2 Dias';
  } else if (this.funnelTimeConfig.calculationMode === 'mean') {
    this.funnelTimeValue = '3.6 Dias';
  } else {
    this.funnelTimeValue = '4.8 Dias';
  }
  this.showNotification('Tempo Médio do Funil recalculado com sucesso!', 'success');
},

recalculateCostPerBooking() {
  if (this.costConfig.calculationMode === 'blended') {
    this.costPerBookingValue = 'R$ 14,80';
  } else if (this.costConfig.calculationMode === 'ai_direct') {
    this.costPerBookingValue = 'R$ 3,80';
  } else {
    this.costPerBookingValue = 'R$ 8,50';
  }
  this.showNotification('Fórmula de Custo por Agendamento atualizada!', 'success');
},

saveAutonomyConfig() {
  this.showNotification('Parâmetros de Autonomia da IA salvos e aplicados!', 'success');
}
```

---

### 4. CHECKLIST DE VALIDAÇÃO

- [ ] **Tempo Médio no Funil**:
  - [ ] O clique no card "Tempo Médio no Funil" abre o modal detalhado (`showFunnelTimeModal = true`).
  - [ ] Exibe a decomposição visual por etapas e indica claramente a etapa de gargalo (*Engajamento -> BANT*).
  - [ ] O construtor de fórmulas permite alternar entre Média, Mediana e P90, recalculando o valor do card.
- [ ] **Custo por Agendamento**:
  - [ ] O clique no card "Custo por Agendamento" abre o modal detalhado (`showCostPerBookingModal = true`).
  - [ ] Exibe os 3 pilares de custo (Mídia R$ 8,50 + IA R$ 3,80 + Operacional R$ 2,50 = R$ 14,80).
  - [ ] O construtor de fórmulas permite alternar os modos de apuração (*Blended*, *Apenas IA*, *Apenas Mídia*) e atualizar o Command Center.
- [ ] **Autonomia da IA**:
  - [ ] O clique no card "Autonomia da IA" abre o modal detalhado (`showAiAutonomyModal = true`).
  - [ ] Apresenta o gráfico/breakdown das 3 categorias (Zero Touch 84.2%, Híbrido 11.0%, Humano 4.8%).
  - [ ] Tabela de razões de handoff detalha exatamente o porquê de intervenção humana nas interações.
- [ ] **White-Label & Design**:
  - [ ] Todos os modais e componentes gráficos se adaptam instantaneamente aos 5 temas de cores do Header.

***

**FIM DO PROMPT.**
