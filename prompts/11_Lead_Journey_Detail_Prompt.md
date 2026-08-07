# Prompt para Agente de IA: Tela de Apresentação da Jornada do Lead (Ver Jornada) no Command Center

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI e SDR Analytics encarregado de implementar a **Tela / Modal de Apresentação da Jornada Completa do Lead ("Ver Jornada")** no protótipo do **Revenue SDR OS** (`01_SDR_Prototype/index.html`).

Esta tela é disparada a partir do botão **`👁️ Ver Jornada`** presente na tabela de leads do modal **"Detalhamento e Cálculo do Tempo Médio no Funil"** no Command Center. O objetivo é fornecer uma visão 360º hiper-detalhada da jornada de contato efetuado com o lead, permitindo análises profundas sobre como o lead foi atendido pela IA e/ou pelo SDR humano, com base em dados concretos e inteligência preditiva para suporte a tomadas de decisões futuras.

---

### 1. REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 / ADR-013)
1. **Frontend Server-Driven & Estático**: Escreva HTML5 semântico com Tailwind CSS + DaisyUI + Alpine.js. Não introduza frameworks SPA complexos (React, Vue).
2. **Estilização White-Label**: A tela/modal deve respeitar dinamicamente todas as variáveis CSS (`--p`, `--s`, `--b1`, etc.) e os 5 temas de cores do Header (`Sakura Bloom`, `Emerald Garden`, `Ocean Breeze`, `Obsidian Night`, `Amber Warmth`).
3. **Zero Backend**: Mantenha o estado reativo simulado no Alpine.js (`dashboardApp()`) com dados mockados ricos, realistas e interativos.

---

### 2. ESTRUTURA E SEÇÕES DA TELA DE JORNADA DO LEAD (`showLeadJourneyModal = true`)

Ao clicar em `👁️ Ver Jornada` para qualquer lead na tabela (ex: *Dr. Roberto Alves*, *Mariana Costa*, *Carlos Eduardo Rocha*), o sistema deve abrir o modal full-screen / gaveta analítica **"Jornada 360º de Atendimento do Lead"** composto pelos seguintes módulos:

#### 📊 2.1. Header Executivo do Lead & SLA Summary
- **Identificação**: Nome do Lead, Empresa, Cargo, Foto/Avatar, Badge do Canal Principal (Zap, E-mail, LinkedIn, Voz).
- **Indicadores Rápidos (KPI Cards)**:
  - 🎯 **Fit Score & Lead Score**: Ex: `94/100 (ICP Ideal)`
  - ⏱️ **Tempo Total de Ciclo**: Ex: `3.2 Dias`
  - 🚦 **Status do SLA**: Badge colorido (`🟢 Dentro do SLA`, `🟡 Alerta SLA`, `🔴 Crítico`)
  - 🤖 **Modo de Atendimento**: `100% IA Autônoma`, `Híbrido (Handoff Realizado)` ou `SDR Humano`
  - 💰 **Custo Operacional Acumulado**: Ex: `R$ 12,40` (Mídia + Tokens LLM + Zap API)
  - 👤 **Responsável Atual**: Agente IA (ex: *SDR Bot Dra. Sofia*) + SDR Humano (ex: *Lucas Silveira*)

#### 🧭 2.2. Navegação por Abas Analíticas (`leadJourneyModalTab`)

O modal deve ser estruturado em **4 Abas Principais**:

---

##### 📍 Aba 1: Linha do Tempo e Interações Multicanal (`leadJourneyModalTab = 'timeline'`)
- **Feed Cronológico de Touchpoints**:
  - Exibição em linha do tempo (Timeline com conectores visuais) de cada interação ocorrida desde a entrada do lead.
  - **Identificação Visual por Canal e Emissor**:
    - 💬 **Zap** (Verde), ✉️ **E-mail** (Azul), 🔗 **LinkedIn** (Roxo), 📞 **Chamada de Voz IA** (Laranja).
    - Ícones para diferenciar mensagens da IA (`🤖`), do SDR Humano (`👤`) e do Lead (`👤 Lead`).
  - **Conteúdo das Mensagens & Payloads**:
    - Balões de conversa mostrando o texto exato enviado e recebido.
    - Timestamp exato (ex: `20/07/2026 14:32:05`).
    - Tempo de resposta (Latência da IA vs Tempo de Resposta do Lead).
  - **Análise da Mensagem pela IA (Hover/Expand)**:
    - Sentiment Score da resposta (`🟢 Positivo`, `🟡 Neutro`, `🔴 Objeção / Negativo`).
    - Intenção detectada (ex: *Solicitação de Preço*, *Dúvida Técnica*, *Pediu Reunião*).
  - **Filtros do Timeline**: Botões rápidos para filtrar por *Todos os Canais*, *Somente Zap*, *Somente Chamadas de Voz*, *Somente Mensagens do Lead*.

---

##### ⚡ Aba 2: Regras da Cadência, Triggers e Handoff (`leadJourneyModalTab = 'cadence'`)
- **Visão da Cadência Vinculada**:
  - Nome da Cadência (ex: *Cadência Outbound MedTech Enterprise v3.2*).
  - Estado atual do lead no fluxo: *Passo 4 de 7 (Aguardando Reunião Agendada)*.
- **Passo a Passo da Cadência Executada**:
  - *Passo 1*: [Zap - IA] Boas-vindas + Apresentação da solução (`Concluído - Há 3 dias`).
  - *Passo 2*: [E-mail - IA] Envio de Case de Sucesso (`Concluído - Há 2 dias`).
  - *Passo 3*: [Zap - IA] Pergunta de Qualificação BANT (`Concluído - Há 1 dia`).
  - *Passo 4*: [Handoff Trigger - Sistema] Transbordo para SDR Humano por objeção de preço (`Executado há 12h`).
- **Análise do Transbordo (Handoff Audit Log)**:
  - Card em destaque listando a causa exata da transferência IA -> Humano.
  - Gatilho disparado: *Gatilho #3 - Objeção de Orçamento / Condição de Pagamento*.
  - Tempo de Assumissão pelo SDR: `14 minutos` (SDR assumiu dentro da meta).

---

##### 🧠 Aba 3: Inteligência BANT, Objeções e Memória da IA (`leadJourneyModalTab = 'memory'`)
- **Matriz de Qualificação BANT**:
  - 💵 **Budget (Orçamento)**: `R$ 15k - 25k/mês` [🟢 Verificado pela IA]
  - 🔑 **Authority (Autoridade)**: `Diretor Clínico / Sócio` [🟢 Confirmado]
  - 🎯 **Need (Necessidade)**: `Redução de no-show em consultas e automação de agendamentos` [🟢 Mapeado]
  - ⏰ **Timing (Prazo de Decisão)**: `Imediato (Próximos 15 dias)` [🟢 Urgência Alta]
- **Resumo Executivo Gerado pela IA (AI Sales Digest)**:
  - Card de síntese automática em linguagem natural:
    > *"Lead demonstrou alto interesse na funcionalidade de confirmação ativa por Zap. Apresentou restrição inicial quanto ao prazo de implantação, contornada pela IA. O lead solicitou demonstração com a equipe técnica."*
- **Objeções Identificadas & Respostas Utilizadas**:
  - Tabela com as objeções levantadas pelo lead e o script/argumento utilizado pela IA ou SDR para superá-las.

---

##### 📞 Aba 4: Chamadas de Voz, Transcrições e Audit Log (`leadJourneyModalTab = 'calls'`)
- **Player de Áudio / Transcrição de Chamadas (Voice Bot)**:
  - Player simulado de áudio com wave-form e controle de velocidade.
  - Transcrição sincronizada com diarização de falantes (*IA Agente* vs *Lead*).
  - Resumo de tópicos e marcadores na linha do tempo da chamada (ex: `01:15 - Lead mencionou concorrente X`).
- **Audit Log Técnico de Integrações**:
  - Eventos de Webhooks, entregabilidade de e-mail (Open Rate, Click Rate), confirmação de leitura do Zap.

---

#### 💡 2.3. Painel Lateral de Tomada de Decisão & Ações Rápidas (Decisões Futuras)
Fixado na lateral do modal (ou rodapé estruturado), apresentando recomendações acionáveis para o SDR/Gestor com base no histórico do lead:
- 💡 **Recomendação do AI Copilot**: *"Lead pronto para agendamento! Sugestão: Enviar link da agenda do SDR de Contas Enterprise."*
- 🚀 **Ações Rápidas**:
  - `📅 Agendar Reunião Agora`
  - `💬 Assumir Conversa no Zap`
  - `🔄 Reiniciar na Cadência de Re-engajamento`
  - `🏷️ Alterar Estágio / Marcar Perda (Disqualify)`

---

### 3. ESTRUTURA DE ESTADO ALPINE.JS (`dashboardApp()`)

Adicionar e estender no objeto retornado por `dashboardApp()` as variáveis e funções abaixo:

```js
// --- ESTADO DO MODAL DE JORNADA DO LEAD ---
showLeadJourneyModal: false,
leadJourneyModalTab: 'timeline', // 'timeline' | 'cadence' | 'memory' | 'calls'

// Lead selecionado para visualização
selectedLeadJourney: {
  id: 'lead-001',
  name: 'Dr. Roberto Alves',
  company: 'Hospital São Lucas',
  role: 'Diretor Clínico',
  avatar: 'https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=150',
  channel: 'Zap',
  channelIcon: '💬',
  fitScore: 96,
  leadScore: 94,
  entryDate: '20/07/2026 09:15',
  currentStage: 'Reunião Agendada',
  daysInStage: '0.3d',
  totalDays: '3.2d',
  slaStatus: 'ok', // 'ok' | 'warning' | 'critical'
  slaLabel: 'Dentro do SLA',
  aiAutonomy: '100% IA Autônoma',
  costTotal: 'R$ 14,20',
  assignedSdr: 'Dra. Sofia (Agente IA)',
  
  // Linha do tempo de mensagens e eventos
  timelineEvents: [
    {
      id: 1,
      type: 'message',
      channel: 'Zap',
      sender: 'ai',
      senderName: 'SDR Bot Dra. Sofia',
      timestamp: '20/07/2026 09:16:02',
      content: 'Olá Dr. Roberto! Vi que o Hospital São Lucas busca otimizar a confirmação de consultas. Como está a taxa de no-show hoje?',
      sentiment: 'positive',
      intent: 'Abertura & Sondagem'
    },
    {
      id: 2,
      type: 'message',
      channel: 'Zap',
      sender: 'lead',
      senderName: 'Dr. Roberto Alves',
      timestamp: '20/07/2026 09:28:40',
      content: 'Nossa taxa de falta está em torno de 22%. Precisamos resolver isso com urgência.',
      sentiment: 'positive',
      intent: 'Dor Mapeada (No-Show Alto)'
    },
    {
      id: 3,
      type: 'call',
      channel: 'Voz IA',
      sender: 'ai',
      senderName: 'Voice Agent Bot',
      timestamp: '21/07/2026 11:00:00',
      content: 'Chamada de voz autônoma de 2m 14s. Lead confirmou interesse em demonstração ao vivo.',
      audioUrl: '#',
      duration: '02:14',
      sentiment: 'positive',
      intent: 'Agendamento Confirmado'
    }
  ],

  // Dados BANT
  bant: {
    budget: 'R$ 15.000 / mês',
    authority: 'Decisor Final (Sócio)',
    need: 'Reduzir no-show de 22% para <5%',
    timing: 'Imediato (15 dias)'
  },

  // Resumo IA
  aiDigest: 'Lead com fit perfeito (ICP MedTech Enterprise). Apresentou dor crítica de no-show elevado. Aceitou demonstração em menos de 48h sem requerer intervenção humana.',

  // Handoff Log
  handoffInfo: {
    occurred: false,
    reason: 'Nenhum (Atendimento 100% Autônomo)',
    timestamp: '-'
  }
},

// --- MÉTODOS DE CONTROLE DA JORNADA ---
openLeadJourney(lead) {
  if (lead) {
    this.selectedLeadJourney = Object.assign({}, this.selectedLeadJourney, lead);
  }
  this.showLeadJourneyModal = true;
},

closeLeadJourney() {
  this.showLeadJourneyModal = false;
}
```

---

### 4. CHECKLIST DE VALIDAÇÃO DA TELA

- [ ] **Gatilho de Abertura**: O clique no botão `👁️ Ver Jornada` na tabela do modal de Tempo Médio no Funil abre a Tela/Modal de Jornada com os dados do lead correspondente.
- [ ] **Header Executivo**: Exibe informações do lead, fit score, status do SLA, responsável e custos operacionais de atendimento.
- [ ] **Linha do Tempo Multicanal**: Timeline exibe histórico ordenado com distinção por Zap, E-mail, Chamada de Voz, remetente (IA vs Lead vs SDR) e indicadores de sentimento/intenção.
- [ ] **Matriz BANT & Resumo IA**: Apresenta de forma visual e clara os 4 pilares do BANT e a síntese executiva gerada pela IA.
- [ ] **Ações de Tomada de Decisão**: Fornece sugestões do Copilot e botões de ação rápida para agendamento, assumir conversa ou alterar estágio.
- [ ] **White-Label & Branding**: Visual 100% adaptável às variáveis CSS e temas selecionados no Header.

---

**FIM DO PROMPT.**
