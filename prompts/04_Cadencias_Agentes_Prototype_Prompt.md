# Prompt para Agente de IA: Atualização das Telas de Cadências & Agentes no Protótipo (01_SDR_Prototype)

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI encarregado de atualizar e implementar a seção **"Cadências & Agentes"** no protótipo do **Revenue SDR OS** no repositório `01_SDR_Prototype`.

O objetivo desta tarefa é construir a experiência completa da aba **"Cadências & Agentes"** (`activeTab === 'cadences'`), permitindo ao usuário visualizar, gerenciar e editar as réguas automáticas de prospecção, configurar as personas dos Agentes SDR de IA (tom de voz, autonomia, instruções) e visualizar o desempenho analítico da orquestração de vendas.

---

### 1. REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 / ADR-013)
1. **Frontend Server-Driven & Estático**: Utilize HTML5 semântico com Tailwind CSS + DaisyUI + Alpine.js. Não introduza frameworks SPA pesados (como React ou Vue).
2. **Estilização White-Label**: Mantenha integração total com os 5 presets de temas White-Label no Header:
   - 🌸 `Sakura Bloom` (Rosa/Roxo vibrante)
   - 🌲 `Emerald Garden` (Verde esmeralda)
   - 🌊 `Ocean Breeze` (Azul vibrante)
   - 🖤 `Obsidian Night` (Dark mode puro com alto contraste)
   - 🌅 `Amber Warmth` (Laranja/Amarelo quente)
3. **Zero Backend**: Mantenha o estado e dados mockados diretamente no componente Alpine.js (`dashboardApp()`).

---

### 2. ESTRUTURA DAS TELAS DE CADÊNCIAS & AGENTES (SUB-VISÕES)

Garantir que, ao clicar em **"Cadências & Agentes"** na Sidebar principal (`activeTab = 'cadences'`), a interface apresente uma barra de sub-navegação no topo com as seguintes 4 sub-visões operacionais:

#### ⚡ Sub-Visão 1: Réguas & Cadências Ativas (`cadenceTab = 'cadences'`)
- **Header & Filtros**:
  - Filtro por Canal (*Todos*, *Zap*, *LinkedIn*, *E-mail*, *Omnichannel*) e por Status (*Todas*, *Ativas*, *Pausadas*, *Rascunhos*).
  - Botão de destaque: `+ Nova Cadência`.
- **Grid / Lista de Cadências**:
  - Cards detalhados de cadências (ex: *Inbound Qualificação Express*, *Outbound LinkedIn Enterprise*, *Resgate de No-Show*, *Re-engajamento Lead Frio*).
  - **Indicadores no Card**:
    - Status (Badge visual: *Em Execução*, *Pausada*).
    - Agente SDR Responsável (com avatar e nome do Agente IA).
    - Métricas-chave: *Leads Ativos*, *Taxa de Resposta (%)*, *Reuniões Agendadas (SQL)* e *Conversão Final (%)*.
    - Sequência visual dos canais (Ícones: Zap ➔ E-mail ➔ Ligação IA ➔ LinkedIn).
  - **Ações Rápidas em cada Card**:
    - Toggle de Ativar/Pausar cadência com toast de notificação imediata.
    - Botão `Editar Passo-a-Passo` (direciona para o Construtor/Builder).
    - Botão `Duplicar` e `Testar no Sandbox`.

#### 🤖 Sub-Visão 2: Agentes SDR & Personas IA (`cadenceTab = 'agents'`)
- **Header de Gestão de IA**:
  - Resumo de capacidade da equipe digital: *Total de Agentes Ativos*, *Autonomia Média (ex: 88.4%)*, *Horas Trabalhadas/Mês (ex: 420h)*.
  - Botão `+ Criar Novo Agente IA`.
- **Grid de Personas de Agentes SDRs**:
  - Cards visuais dos Agentes (ex: *Sofia - Especialista Inbound*, *Lucas - Hunter Outbound B2B*, *Mariana - Follow-up & Re-engajamento*).
  - **Informações em destaque**:
    - Avatar, Nome e Cargo (*SDR IA Senior*).
    - Status de Operação (*Online / Processando 14 conversas*).
    - **Nível de Autonomia**: Badge visual com indicador (ex: *100% Autônomo com Guardrails*, *Semi-Autônomo (Human-in-the-Loop)*, *Somente Transbordo*).
    - **Tom de Voz & Estilo**: Badge (ex: *Consultivo & Empático*, *Direto & Comercial*, *Educativo & Técnico*).
    - **Canais Habilitados**: Badges dos canais ativados.
    - Limites Operacionais: Máximo de abordagens simultâneas e tempo médio de resposta (ex: 3.8s).
  - **Ações do Agente**:
    - Botão `Configurar Prompt & Regras` (Abre modal de edição da Persona).
    - Botão `Ver Transcrições & Memória`.

#### 🛠️ Sub-Visão 3: Construtor Visual de Cadências (`cadenceTab = 'builder'`)
- **Header da Cadência em Edição**:
  - Título e seletor da cadência atual (ex: *Editando: Inbound Qualificação Express*).
  - Botões de ação: `Salvar Alterações`, `Simular Abordagem`, `Cancelar`.
- **Fluxo Passo-a-Passo (Visual Step Builder)**:
  - Timeline vertical com os passos da régua:
    - **Gatilho Inicial (Trigger)**: Ex: *Lead inserido via Meta Ads / Webhook*.
    - **Passo 1 (Ação)**: *Abordagem inicial Zap via SDR Sofia (IA)* - Texto + Áudio Personalizado.
    - **Passo 2 (Espera/Delay)**: *Aguardar 2 horas se não houver resposta*.
    - **Passo 3 (Condição/Branching BANT)**: *Se Lead respondeu ➔ Qualificar BANT | Se não respondeu ➔ Enviar E-mail de Follow-up*.
    - **Passo 4 (Ação Final / Transbordo)**: *Agendar Reunião via Google Calendar + Handoff para SDR Humano*.
  - Botão entre cada passo: `+ Adicionar Passo` (Abre modal para escolher tipo: *Mensagem IA*, *Delay/Espera*, *Condição*, *Lembrete Humano*, *E-mail*, *Ligação*).

#### 📊 Sub-Visão 4: Analytics de Cadências & Testes A/B (`cadenceTab = 'analytics'`)
- **Painel de Performance Comparativa**:
  - Gráfico/Tabela comparativa entre cadências: *Qual régua gera mais reuniões (SQLs)?*
  - **Funil de Retenção por Passo**: Percentual de desengajamento/dropout em cada etapa da régua.
  - **Análise de Testes A/B de Mensagens**:
    - Variação A (Abordagem Direta com Vídeo) vs Variação B (Pergunta Consultiva com Pergunta Aberta).
    - Métricas de Taxa de Abertura, Taxa de Resposta e Conversão em Agendamento.
  - **Heatmap de Melhores Horários**: Gráfico visual dos melhores dias/horários para disparo inteligente da IA.

---

### 3. MODAIS INTERATIVOS E ESTADO ALPINE.JS

1. **Modal Configurar Agente IA (`showAgentModal`)**:
   - Edição de Nome, Tom de Voz, Prompt do Sistema / Instruções da Persona, Modelo de LLM (Gemini 1.5 Pro, GPT-4o), Nível de Autonomia (Slider/Radio 0-100%) e Guardrails de Segurança (LGPD, limites de desconto, gatilhos de escalação humana).
2. **Modal Adicionar Passo na Cadência (`showStepModal`)**:
   - Form com escolha do canal, mensagem de template/prompt dinâmico, tempo de atraso (horas/dias) e condições de desvio.
3. **Drawer / Modal Sandbox de Simulação (`showSandboxModal`)**:
   - Permite simular o envio de mensagens de um lead fictício para testar a reação do Agente IA dentro da cadência em tempo real.

---

### 4. CHECKLIST DE VALIDAÇÃO
- [ ] Clicar em **"Cadências & Agentes"** na sidebar ativa a nova aba principal (`activeTab === 'cadences'`).
- [ ] As 4 sub-visões no topo (*Réguas & Cadências Ativas*, *Agentes SDR & Personas IA*, *Construtor Visual*, *Analytics & A/B*) alternam dinamicamente sem recarregar a página.
- [ ] O toggle de ativar/pausar cadência exibe toast de confirmação e atualiza o badge do card.
- [ ] O modal de edição do Agente IA permite alterar parâmetros e salva no estado Alpine.js.
- [ ] O Construtor Visual exibe a timeline de passos interativa de forma limpa e responsiva.
- [ ] A alteração do preset de tema White-Label no header reflete perfeitamente nas novas telas.

***

**FIM DO PROMPT.**
