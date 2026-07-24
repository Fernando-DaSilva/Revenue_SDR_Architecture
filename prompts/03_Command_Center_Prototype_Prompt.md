# Prompt para Agente de IA: Atualização do Command Center no Prototipo (01_SDR_Prototype)

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI encarregado de atualizar e aprimorar o protótipo do **Revenue SDR OS** no repositório `01_SDR_Prototype`.

O objetivo desta tarefa é aperfeiçoar a experiência do **Command Center** (Manager Dashboard), garantindo que ao clicar na opção **"Command Center"** na sidebar principal (ou ao navegar pelas suas sub-visões), a interface apresente de forma fluida, interativa e esteticamente impecável todas as telas e visões operacionais da central de comando do SDR OS.

---

### 1. REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 / ADR-013)
1. **Frontend Server-Driven & Estático**: Escreva HTML5 semântico com Tailwind CSS + DaisyUI + Alpine.js. Não introduza frameworks SPA complexos (como React ou Vue).
2. **Estilização White-Label**: Mantenha o suporte completo aos 5 presets de temas White-Label dinâmicos no Header:
   - 🌸 `Sakura Bloom` (Rosa/Roxo vibrante)
   - 🌲 `Emerald Garden` (Verde esmeralda)
   - 🌊 `Ocean Breeze` (Azul vibrante)
   - 🖤 `Obsidian Night` (Dark mode puro com alto contraste)
   - 🌅 `Amber Warmth` (Laranja/Amarelo quente)
3. **Zero Backend**: Mantenha dados mockados ricos no estado reativo do Alpine.js (`dashboardApp()`).

---

### 2. ESTRUTURA DAS TELAS DO COMMAND CENTER (O QUE DESENVOLVER/GARANTIR)

Garantir que, quando o usuário clicar em **"Command Center"** na Sidebar (`activeTab = 'dashboard'`), as 4 sub-visões a seguir estejam 100% integradas e operacionais na sub-navegação do Header:

#### 📊 Sub-Visão 1: Visão Geral & KPIs (`commandCenterTab = 'overview'`)
- **Grid de Cards de KPIs Executivos**:
  - *Leads Contatados*: indicador de volume e variação percentual.
  - *Taxa de Qualificação BANT*: indicador percentual e score médio.
  - *Reuniões Agendadas (SQL)*: progresso em relação à meta (ex: 94.6% de 150).
  - *Pipeline de MRR Gerado*: valor em R$ e estimativa de MRR.
- **Funil de Conversão Comercial Dinâmico**:
  - Estágios visuais do funil: Prospecção → Engajamento IA → Qualificação BANT → Reunião Agendada → Proposta Enviada.
  - Progresso relativo, contagem de leads, taxa de conversão e valor acumulado.
  - Filtro funcional de executor (*Todos*, *Apenas Agente IA*, *SDRs Humanos*).
  - Resumo de métricas no rodapé do funil: Tempo médio no funil (3.2 dias), Custo por agendamento (R$ 14,80) e Autonomia da IA (84.2%).
- **Widgets Laterais**:
  - Card de preview de recomendações proativas do SDR Copilot.
  - Alerta com acionamento direto para a Fila de Handoff Crítico.

#### 🔴 Sub-Visão 2: Live Monitor / Operations Feed (`commandCenterTab = 'live_feed'`)
- **Stream em Tempo Real de Interações**:
  - Tabela com feed ao vivo das abordagens do Agente IA e SDRs humanos (WhatsApp, E-mail, Ligação, LinkedIn).
  - Badge de status de conexão WebSocket ("LIVE FEED" / "latência 14ms").
  - Campo de busca em tempo real por nome do lead ou empresa.
  - Visualização de Score BANT com barra de progresso visual.
  - Ações rápidas em cada linha: Botão `Raio-X` (abre modal de detalhes) e `Assumir` (takeover imediato por SDR humano com toast de notificação).

#### 🤖 Sub-Visão 3: AI Copilot & Insights (`commandCenterTab = 'copilot'`)
- **Métricas de Eficiência da IA**:
  - *Horas Economizadas* (ex: 148h / +2 SDRs).
  - *Acurácia BANT* (ex: 96.4%).
  - *Economia em Headcount* (ex: R$ 18.500/mês).
  - *Tempo Médio de Resposta* (ex: 4.2s vs 45min humano).
- **Central de Ações Recomendadas**:
  - Grid de cards de sugestões proativas (Re-engajamento, Otimização de script para objeções de preço, Leads VIP detectados, Disparo inteligente Meta Ads).
  - Botão de execução individual de ação (`⚡ Executar`) e re-otimização global de cadências (`⚡ Otimizar Todas as Cadências`).

#### 🚨 Sub-Visão 4: Handoffs & Alertas de Escalação (`commandCenterTab = 'handoffs'`)
- **Fila de Prioridade — Escalação Humana Imediata**:
  - Lista detalhada de leads com atendimento retido que exigem intervenção humana (motivos: objeção não mapeada como HIPAA/LGPD, pedido de consultor humano, lead VIP enterprise).
  - Tags de urgência (*CRÍTICA*, *ALTA*), tempo de espera na fila e score BANT.
  - Trecho em destaque do motivo da escalação e última mensagem do lead.
  - Botões de ação direta: `Assumir no WhatsApp`, `Iniciar Chamada` e `Ver Raio-X`.

---

### 3. MODAIS INTERATIVOS E COMPONENTES SUPORTE

1. **Modal Raio-X do Lead (`selectedLead`)**:
   - Cabeçalho com dados e canal do lead.
   - Grid com breakdown do BANT (Budget, Authority, Need, Score).
   - Caixas de diálogo com transcrição completa da conversa do WhatsApp com a IA (`SDR-01 IA`).
   - Botão para assumir atendimento.
2. **Modal Novo Lead (`showNewLeadModal`)**:
   - Formulário completo para simular injeção manual de lead na esteira da IA.
   - Atualização dinâmica da tabela e exibição de Toast de confirmação.
3. **Controle de Janela Temporal**:
   - Alternância entre `Hoje`, `Semana` e `Mês`, atualizando dinamicamente os valores de KPIs na tela.

---

### 4. CHECKLIST DE VALIDAÇÃO
- [ ] O menu **Command Center** na sidebar ativa perfeitamente a visualização principal do dashboard.
- [ ] As 4 sub-visões no header (*Visão Geral & KPIs*, *Live Monitor*, *AI Copilot*, *Handoffs & Alertas*) alternam dinamicamente sem recarregar a página.
- [ ] O modal de *Raio-X do Lead* abre corretamente com dados do lead selecionado.
- [ ] A injeção de *Novo Lead* funciona e adiciona o lead no topo da lista.
- [ ] O seletor de temas White-Label no header altera as cores de todo o dashboard em tempo real.

***

**FIM DO PROMPT.**
