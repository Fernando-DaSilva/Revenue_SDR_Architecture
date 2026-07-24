# Prompt para Agente de IA: Tela de Gerenciar Assinaturas e Métodos de Pagamento no Protótipo (01_SDR_Prototype)

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI encarregado de implementar e atualizar a funcionalidade de **"Gerenciar Assinaturas"** (substituindo a antiga denominação "Gerenciar Cartão") no protótipo do **Revenue SDR OS** no repositório `01_SDR_Prototype`.

O objetivo desta tarefa é construir uma experiência moderna e completa para gestão da assinatura do tenant e dos **multimeios de pagamento**, incorporando suporte prioritário às formas de pagamento do mercado brasileiro — em especial o **PIX** (QR Code e Copia e Cola) e **Boleto Bancário Corporativo**, além dos tradicionais **Cartões de Crédito/Débito** —, bem como a gestão de dados fiscais para emissão de Nota Fiscal Eletrônica (NF-e) e histórico financeiro.

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
4. **Renomeação Importante**: Substitua em toda a UI o texto e os seletores do botão `Gerenciar Cartão` por **`Gerenciar Assinaturas`** (`showManageSubscriptionsModal` ou sub-visão dedicada em `settingsTab = 'billing_usage'`).

---

### 2. ESTRUTURA E COMPONENTES DA TELA DE GERENCIAR ASSINATURAS

A tela/modal de Gerenciar Assinaturas deve ser organizada em 4 abas/seções operacionais fluidas:

---

#### 📋 2.1 Resumo da Assinatura Vigente & Status de Renovação
- **Painel de Destaque do Plano**:
  - Nome do Plano Ativo: **Enterprise Growth**.
  - Valor Recorrente: **R$ 2.490,00 / mês**.
  - Ciclo de Cobrança: **Mensal** (Próxima renovação: `15/08/2026`).
  - Status da Assinatura: Badge de destaque (`● Assinatura Ativa` em verde, `● Pagamento Pendente` em amarelo, ou `● Em Atraso` em vermelho).
  - Forma de Pagamento Padrão Ativa: Card compacto com o método ativo (ex: `⚡ PIX Automático Recorrente` ou `💳 Cartão Visa final 4892`).
- **Ações Rápidas de Assinatura**:
  - Botão `Alterr Mídia de Pagamento Padrão`.
  - Botão `Pausar Assinatura Temporariamente` (com modal de confirmação).
  - Link/Botão `Cancelar Assinatura` (abre o fluxo de retenção e feedback).

---

#### 💳 2.2 Gestão de Métodos de Pagamento (Multimeios)
Seletor com 3 opções principais de métodos de pagamento suportados:

##### A. ⚡ PIX (Pagamento Instantâneo BR - Destaque de Inovação)
- **PIX Copia e Cola / QR Code Dinâmico**:
  - Exibição de QR Code gerado para cobrança/renovação do mês.
  - Campo com a chave PIX Copia e Cola (`00020126580014BR.GOV.BCB.PIX...`) com botão de clique único `📋 Copiar Código PIX`.
  - Timer visual de expiração do QR Code (ex: "QR Code válido por 29:45 min").
  - Status em tempo real (simulado via Alpine.js): Indicator animado `⏳ Aguardando confirmação do PIX...` -> altera dinamicamente para `✅ Pagamento PIX Confirmado com Sucesso!`.
- **PIX Automático / Recorrente (Nova modalidade BACEN)**:
  - Toggle de ativação: *Ativar PIX Automático Recorrente para os próximos meses*.
  - Explicação amigável de como o banco do tenant autoriza a cobrança recorrente direta no app do banco.

##### B. 💳 Cartões de Crédito & Débito
- **Lista de Cartões Salvos**:
  - Cards com a bandeira identificada (Visa, Mastercard, Elo, Amex), final do cartão (`•••• 4892`), data de expiração (`09/28`), e badges (`Principal` / `Backup`).
  - Opção para `Remover Cartão` e `Definir como Principal`.
- **Formulário de Adicionar Novo Cartão**:
  - Campos: Número do Cartão, Nome Impresso no Cartão, Validade (MM/AA), CVC/CVV e CPF/CNPJ do Titular.
  - Auto-detecção visual da bandeira do cartão conforme os primeiros dígitos digitados.

##### C. 📄 Boleto Bancário Corporativo
- **Geração de Boleto para Faturamento**:
  - Opção recomendada para empresas e órgãos com departamento financeiro tradicional.
  - Exibição da Linha Digitável do Boleto (`34191.09008 61234.567890 12345.678901 8 98760000249000`) com botão `Copiar Linha Digitável`.
  - Botão de Ação: `📥 Baixar Boleto em PDF`.
  - Alerta informativo sobre o prazo de compensação bancária (até 24-48h úteis).

---

#### 🏛️ 2.3 Dados de Faturamento & Emissão de Nota Fiscal (NF-e)
Formulário fiscal para garantia de compliance financeiro do tenant:

- **Dados da Empresa / Pagador**:
  - Razão Social / Nome Completo.
  - CNPJ / CPF (com máscara de validação).
  - Inscrição Estadual (IE) e Inscrição Municipal (IM).
- **Endereço Fiscal de Faturamento**:
  - CEP, Logradouro, Número, Complemento, Bairro, Cidade e Estado (UF).
- **E-mail Financeiro para Envio Automático**:
  - Input para cadastrar e-mail da controladoria/financeiro (ex: `financeiro@clinicabela.com.br`) para recebimento automático de notas fiscais e comprovantes de pagamento a cada ciclo.
- Botão: `💾 Salvar Dados Fiscais`.

---

#### 📜 2.4 Histórico Financeiro, Faturas & Comprovantes NFe
Tabela completa contendo o histórico transparente de faturamento do tenant:

- **Colunas da Tabela**:
  1. **Data da Fatura**: ex: `15/07/2026`.
  2. **Descrição do Item**: ex: `Mensalidade Enterprise Growth + 1M Tokens Extra`.
  3. **Valor Total**: ex: `R$ 2.680,00`.
  4. **Método de Pagamento Utilizado**: Badge visual (`⚡ PIX`, `💳 Cartão Visa (4892)`, `📄 Boleto`).
  5. **Status de Pagamento**: Badge DaisyUI (`Paga` em verde, `Pendente` em amarelo, `Falhou` em vermelho).
  6. **Ações & Documentos**:
     - Botão `📄 Fatura (PDF)`.
     - Botão `🏛️ NF-e (PDF/XML)`.

---

#### 🔄 2.5 Fluxo de Retenção & Cancelamento de Assinatura
Modal / Sub-step ativado ao clicar em "Cancelar Assinatura":

- **Pesquisa de Motivo de Cancelamento**:
  - Seleção de opções (ex: "Preço elevado", "Pouco uso dos agentes de IA", "Migrou para outra ferramenta", "Falta de recursos").
- **Oferta de Retenção Dinâmica**:
  - Apresentação de alternativa (ex: "Deseja pausar por 60 dias sem perder os dados dos seus leads?" ou "Aplicar 30% de desconto no próximo ciclo?").
- **Confirmação Final**:
  - Botão `Confirmar Cancelamento da Assinatura` com lembrete de que o acesso continuará disponível até o final do período já pago (`15/08/2026`).

---

### 3. ESTADO ALPINE.JS (INTEGRAÇÃO NO `dashboardApp()`)

Adicionar ao componente Alpine.js as seguintes variáveis e funções para a gestão de assinaturas:

```javascript
// Exemplo de estado Alpine.js para Gerenciar Assinaturas
showManageSubscriptionsModal: false,
activeSubscriptionTab: 'overview', // 'overview', 'payment_methods', 'fiscal_info', 'invoices'
selectedPaymentMethodType: 'pix', // 'pix', 'credit_card', 'boleto'
pixCopiedToast: false,
boletoCopiedToast: false,

// Simulação de alteração do status do PIX em tempo real
pixPaymentStatus: 'pending', // 'pending' -> 'confirmed'

copyPixCode() {
  navigator.clipboard.writeText(this.pixCodeString);
  this.pixCopiedToast = true;
  setTimeout(() => this.pixCopiedToast = false, 3000);
},

simulatePixConfirmation() {
  setTimeout(() => {
    this.pixPaymentStatus = 'confirmed';
  }, 4000);
},

saveFiscalData() {
  // Atualiza dados fiscais de NF-e do tenant
}
```

---

### 4. ENTREGÁVEIS & EXCELÊNCIA VISUAL
1. **Atualização da Botonera**: Alterar a label do botão no card de plano de "Gerenciar Cartão" para **"Gerenciar Assinaturas"**.
2. **Experiência Localizada para o Brasil (PIX & Boleto)**: Garantir destaque visual rico aos badges e fluxos de PIX (QR Code e Copia e Cola) e Boleto Bancário.
3. **Fidelidade ao Tema White-Label**: Respeitar o tema ativo no sistema (`Sakura Bloom`, `Emerald Garden`, etc.).
4. **Responsividade & Usabilidade**: Layout com abas limpas, modais com `x-transition` e feedbacks visuais em tempo real.

---

**FIM DO PROMPT**
