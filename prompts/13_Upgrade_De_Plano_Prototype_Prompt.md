# Prompt para Agente de IA: Tela de Fazer Upgrade de Plano no Protótipo (01_SDR_Prototype)

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI encarregado de implementar a funcionalidade e o fluxo interativo de **"Fazer Upgrade de Plano"** no protótipo do **Revenue SDR OS** no repositório `01_SDR_Prototype`.

O objetivo desta tarefa é construir a experiência completa de visualização, seleção, customização de add-ons e confirmação de upgrade/downgrade de plano (`showUpgradePlanModal` ou sub-visão dedicada em `settingsTab = 'billing_usage'`), permitindo ao usuário selecionar novos planos, adicionar recursos extras (tokens, seats, canais de Zap) e visualizar o cálculo de prorata e renovação em tempo real.

---

### 1. REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 / ADR-013)
1. **Frontend Server-Driven & Estático**: Utilize HTML5 semântico com Tailwind CSS + DaisyUI + Alpine.js. Não introduza frameworks SPA pesados (React, Vue, Next).
2. **Estilização White-Label**: Mantenha integração total com os 5 presets de temas White-Label dinâmicos no Header e aplique atualizações em tempo real ao alterar temas:
   - 🌸 `Sakura Bloom` (Rosa/Roxo vibrante)
   - 🌲 `Emerald Garden` (Verde esmeralda)
   - 🌊 `Ocean Breeze` (Azul vibrante)
   - 🖤 `Obsidian Night` (Dark mode puro com alto contraste)
   - 🌅 `Amber Warmth` (Laranja/Amarelo quente)
3. **Zero Backend**: Mantenha todo o estado e dados mockados diretamente no componente Alpine.js (`dashboardApp()`).

---

### 2. ESTRUTURA E COMPONENTES DA TELA DE UPGRADE DE PLANO

A tela/modal de Upgrade de Plano deve conter os seguintes blocos funcionais com rica interação visual:

---

#### 🔘 2.1 Header & Seletor de Ciclo de Faturamento
- **Título & Subtítulo Claros**: "Evolua a Operação do seu Revenue SDR OS" com explicação sobre aumento de capacidade de prospeção e agentes de IA.
- **Toggle de Faturamento (Mensal vs. Anual)**:
  - Radio button ou toggle visual Alpine.js (`billingCycle = 'monthly' | 'annual'`).
  - Highlight visual no ciclo **Anual**: Badge em destaque (`Ganhe 2 Meses Grátis` ou `20% de Desconto no Anual`).
  - Atualização instantânea nos preços exibidos em todos os cards de planos ao alternar o ciclo.

---

#### 📦 2.2 Tabela Comparativa de Planos (Cards de Preço)
Exibir 4 cards de planos organizados horizontalmente/grid responsivo, destacando o **Plano Atual** do tenant:

1. **Plano Starter (SDR Operacional)**
   - Preço: `R$ 890,00 / mês` (no mensal) ou `R$ 712,00 / mês` (no anual).
   - Indicado para: Pequenas equipes e testes de validação.
   - Recursos inclusos: 1 Usuário SDR, 500 Leads/mês no Pipeline, 500k Tokens de IA/mês, 1 Instância Zap.
   - Botão de Ação: `Migrar para Starter`.

2. **Plano Enterprise Growth (Plano Atual do Tenant - Destaque)**
   - Preço: `R$ 2.490,00 / mês` (no mensal) ou `R$ 1.992,00 / mês` (no anual).
   - Badge visual proeminente: `● Seu Plano Atual`.
   - Indicado para: Operações de vendas em crescimento acelerado.
   - Recursos inclusos: 5 Usuários SDR, 5.000 Leads/mês, 2M Tokens de IA/mês, 3 Instâncias Zap, Suporte a BYOK (Chaves Próprias de IA OpenAI/Anthropic/DeepSeek), Cadências Multicanal.
   - Botão de Ação: Disabled ou `Plano Ativo`.

3. **Plano Enterprise Scale (Alta Performance & IA Avançada)**
   - Preço: `R$ 5.990,00 / mês` (no mensal) ou `R$ 4.792,00 / mês` (no anual).
   - Badge de destaque visual: `🔥 Mais Popular` / `Recomendado`.
   - Indicado para: Grandes operações de SDR com múltiplos times e alto volume de disparos.
   - Recursos inclusos: 15 Usuários SDR, 25.000 Leads/mês, 10M Tokens de IA/mês, 10 Instâncias Zap, SDR Copilot com voz/áudio HD, Guardrails de IA avançados e SLA de Atendimento Prioritário.
   - Botão de Ação: `🚀 Fazer Upgrade para Scale` (Estilo primário vibrante).

4. **Plano Custom / Corporate (Sob Medida)**
   - Preço: `Sob Consulta`.
   - Indicado para: Grandes corporações com volume ilimitado, infraestrutura dedicada (VPS isolada - ADR-004) e integrações customizadas.
   - Recursos inclusos: Leads e Tokens ilimitados, Instâncias Zap ilimitadas, Gerente de Conta Dedicado, Treinamento de Modelos LLM sob medida.
   - Botão de Ação: `💬 Falar com Especialista / Enterprise Sales`.

---

#### 🧩 2.3 Módulos Opcionais / Add-ons Customizáveis
Permitir que o usuário personalize o plano escolhido adicionando capacidade extra diretamente no modal/sub-visão:

- **Pacote Extra de Tokens de IA**:
  - Incremetador (`+1M Tokens` por `R$ 190,00 / mês`).
  - Selector numérico Alpine.js (`extraTokensQty`).
- **Usuários / Seats SDR Adicionais**:
  - Incrementador (`+1 Usuário SDR` por `R$ 150,00 / mês`).
  - Selector numérico Alpine.js (`extraSeatsQty`).
- **Canais / Instâncias Zap Adicionais**:
  - Incrementador (`+1 Instância Zap` por `R$ 250,00 / mês`).
  - Selector numérico Alpine.js (`extraZapQty`).

---

#### 📊 2.4 Resumo da Simulação & Cálculo Proporcional (Prorata)
Painel lateral/inferior que exibe o resumo financeiro antes da confirmação final:

- **Plano Selecionado**: Nome e ciclo do novo plano.
- **Valor Recorrente do Novo Plano**: Ex: `R$ 5.990,00 / mês`.
- **Add-ons Selecionados**: Soma dos pacotes extras escolhidos.
- **Subtotal Recorrente**: Novo valor total mensal/anual.
- **Cálculo de Pro-Rata (Diferença Imediata)**:
  - Exibição transparente do crédito do plano atual (dias não utilizados) e cobrança proporcional do novo plano pelos dias restantes no ciclo vigência.
  - Exemplo visual: "Crédito do plano atual (15 dias restantes): -R$ 1.245,00 | Valor novo plano (15 dias): +R$ 2.995,00 | **Total a pagar hoje: R$ 1.750,00**".

---

#### 🔒 2.5 Confirmação & Checkout Modal / Step
- Botão principal: `Confirmar Upgrade de Plano`.
- Modal/Sub-step de confirmação com resumo dos termos, forma de pagamento cadastrada a ser cobrada e toggle de aceite dos termos de renovação.
- Feedback visual de sucesso: Toast/Alert notificando que o upgrade foi aplicado instantaneamente e que as novas cotas de IA/Leads já estão ativas.

---

### 3. ESTADO ALPINE.JS (INTEGRAÇÃO NO `dashboardApp()`)

Adicionar ao estado global no Alpine.js as propriedades e métodos para gestão de upgrade:

```javascript
// Exemplo de estado Alpine.js para Upgrade de Plano
showUpgradePlanModal: false,
selectedPlan: 'growth', // 'starter', 'growth', 'scale', 'custom'
billingCycle: 'monthly', // 'monthly', 'annual'
extraTokensQty: 0,
extraSeatsQty: 0,
extraZapQty: 0,

selectPlan(planKey) {
  this.selectedPlan = planKey;
},
calculateTotalRecurring() {
  // Lógica de cálculo dinâmico com base no plano, ciclo e add-ons
},
calculateProrataImmediate() {
  // Simulação de valor proporcional para cobrança imediata
},
confirmPlanUpgrade() {
  // Atualiza o plano ativo do tenant, exibe toast de sucesso e fecha o modal
}
```

---

### 4. ENTREGÁVEIS & EXCELÊNCIA VISUAL
1. **Design System Integrado**: Uso completo de DaisyUI (modals, cards, badges, stats, range sliders, toggles) totalmente estilizado conforme o tema White-Label ativo.
2. **Responsividade Total**: Layout adaptável para telas desktop, tablet e mobile.
3. **Animações e Transições**: Uso de `x-transition` Alpine.js para alteração suave de valores e modais.

---

**FIM DO PROMPT**
