# Prompt para Agente de IA: Atualização das Telas de Configurações Tenant no Protótipo (01_SDR_Prototype)

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI encarregado de atualizar e implementar a seção **"Configurações Tenant"** no protótipo do **Revenue SDR OS** no repositório `01_SDR_Prototype`.

O objetivo desta tarefa é construir a experiência completa da aba **"Configurações Tenant"** (`activeTab === 'settings'`), permitindo ao usuário gerenciar todas as configurações da organização/empresa, branding White-Label, gestão da equipe e permissões (RBAC), conectores de canais de comunicação (Zap / E-mail / CRM) e monitoramento de plano, faturamento e cotas de uso de IA.

---

### 1. REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 / ADR-013)
1. **Frontend Server-Driven & Estático**: Utilize HTML5 semântico com Tailwind CSS + DaisyUI + Alpine.js. Não introduza frameworks SPA pesados (como React ou Vue).
2. **Estilização White-Label**: Mantenha integração total com os 5 presets de temas White-Label dinâmicos no Header e aplique atualizações em tempo real ao alterar temas:
   - 🌸 `Sakura Bloom` (Rosa/Roxo vibrante)
   - 🌲 `Emerald Garden` (Verde esmeralda)
   - 🌊 `Ocean Breeze` (Azul vibrante)
   - 🖤 `Obsidian Night` (Dark mode puro com alto contraste)
   - 🌅 `Amber Warmth` (Laranja/Amarelo quente)
3. **Zero Backend**: Mantenha todo o estado e dados mockados diretamente no componente Alpine.js (`dashboardApp()`).

---

### 2. ESTRUTURA DAS TELAS DE CONFIGURAÇÕES TENANT (SUB-VISÕES)

Garantir que, ao clicar em **"Configurações Tenant"** na Sidebar principal (`activeTab = 'settings'`), a interface apresente no Header uma barra de sub-navegação com as seguintes 4 sub-visões operacionais:

---

#### 🏢 Sub-Visão 1: Perfil da Organização & Branding White-Label (`settingsTab = 'organization'`)
- **Informações Gerais do Tenant**:
  - Formulário com os campos da organização:
    - *Nome da Empresa/Organização* (ex: "Clínica Bela Harmonia", "Imobiliária Center").
    - *Slug / Subdomínio* (ex: `clinica-bela` com sufixo visual `.localhost:8000` / `.revenuesdros.com`).
    - *CNPJ / Registro Fiscal* e *E-mail Principal de Contato*.
    - *Fuso Horário* (seletor: `America/Sao_Paulo (UTC-3)`).
    - *Idioma Padrão do Tenant* (seletor: `Português (pt-BR)`, `Inglês (en-US)`, `Espanhol (es-ES)`).
- **Painel de Branding & Presets de Temas White-Label**:
  - **Seletor Visual de Presets**: Cards clicáveis dos 5 temas White-Label com preview das cores primárias e secundárias em badges.
  - **Acesso ao Studio de Temas**: Atalhos/Callout para abrir o Gerenciador de Temas completo (Studio).
  - **Gestão de Logos & Favicon**:
    - Upload / URL do Logo para Modo Claro (Preview em tempo real).
    - Upload / URL do Logo para Modo Escuro (Preview em tempo real).
    - Upload / URL do Favicon.
  - **Configurações da Marca & Rodapé**:
    - Toggle: *Remover chancela "Powered by Revenue SDR OS"*.
    - Input: *Texto de copyright/marca personalizada no rodapé*.
  - Botão de Ação: `💾 Salvar Alterações de Branding` (atualiza instantaneamente os temas e logos no protótipo).

---

#### 👥 Sub-Visão 2: Equipe, Usuários & Permissões RBAC (`settingsTab = 'users_team'`)
- **Header de Gestão da Equipe**:
  - Cards de resumo: *Total de Membros (ex: 8)*, *Licenças Ativas (ex: 8/10)*, *Administradores (ex: 2)*.
  - Botão de destaque: `+ Convidar Novo Membro`.
- **Tabela de Membros do Tenant**:
  - Lista completa de usuários com:
    - **Usuário**: Avatar, Nome Completo e E-mail.
    - **Função / Papel (RBAC)**: Badge com a função (`Tenant Admin`, `SDR Manager`, `Operador SDR`, `Auditor Read-Only`).
    - **Status**: Badge de status (`Ativo`, `Pendente`, `Suspenso`).
    - **Último Acesso**: Timestamp amigável (ex: "Há 12 minutos", "Ontem às 16:45").
    - **Ações**: Menu com opções (`Editar Papel`, `Reenviar Convite`, `Redefinir Senha`, `Desativar Usuário`).
- **Painel Explicativo da Matriz de Permissões RBAC**:
  - Tabela/Accordion de comparação das 4 funções (Admin vs Manager vs Operador vs Auditor) detalhando permissões de acesso: *Visualizar Leads*, *Editar Cadências & Agentes*, *Configurar AI Memory & Guardrails*, *Gerenciar Faturamento & Tenant*.

---

#### 🔌 Sub-Visão 3: Canais de Comunicação & Integrações (`settingsTab = 'channels_integrations'`)
- **Conectores de Canais de Prospecção**:
  - **Card Zap Business (Evolution API / Baileys)**:
    - Status visual: Badge verde `● Conectado`, Número vinculado (`+55 11 99887-6655`), Nível de Bateria (88%), Nome do Aparelho ("Samsung S23 SDR").
    - Ações rápidas: `Escanear QR Code`, `Testar Conexão`, `Desconectar Instância`.
  - **Card E-mail Corporativo (SMTP / Google Workspace / Outlook)**:
    - Status: Badge verde `● Autenticado (OAuth2)`.
    - Conta ativa: `sdr.atendimento@clinicabela.com.br`.
    - Verificação de entregabilidade: Badges para `SPF ✓`, `DKIM ✓`, `DMARC ✓`.
  - **Card LinkedIn Automation / Sales Navigator**:
    - Status: Badge azul `● Sincronizado`.
- **Integrações de CRM & Webhooks**:
  - **Cards de CRMs**: Integradores para *HubSpot*, *Pipedrive*, *RD Station* e *Salesforce* com toggles de ativado/desativado, indicador de status e botão `Configurar Mapeamento de Campos`.
  - **Webhooks de Entrada de Leads (Inbound Webhook URL)**:
    - Campo de URL do webhook único do tenant: `https://api.revenuesdros.com/v1/webhooks/inbound/org_clinicabela_891`.
    - Botão `Copiar URL`, indicador de Secret Token e log dos últimos 5 eventos de webhook recebidos.

---

#### 💳 Sub-Visão 4: Plano, Consumo de IA & Faturamento (`settingsTab = 'billing_usage'`)
- **Resumo do Plano & Assinatura Ativa**:
  - Card de destaque com o plano atual: **Plano Enterprise Growth**.
  - Valor: **R$ 2.490,00 / mês** (Faturamento Mensal).
  - Status: Badge verde `● Assinatura Ativa` (Renovação em: 15/08/2026).
  - Botão de Ação: `🚀 Fazer Upgrade de Plano` ou `Gerenciar Assinatura`.
- **Métricas de Consumo em Tempo Real (Cotas de Uso no Mês)**:
  - **Tokens de IA / LLM**: Barra de progresso visual (ex: *1.250.000 / 2.000.000 Tokens* — 62.5% utilizado).
  - **Leads no Pipeline**: Barra de progresso (ex: *2.840 / 5.000 Leads* — 56.8% utilizado).
  - **Mensagens Zap Disparadas**: Barra de progresso (ex: *8.900 / 15.000 Mensagens* — 59.3% utilizado).
- **Provedores de IA & Chaves Próprias (BYOK - Bring Your Own Key)**:
  - Toggle: *Utilizar Infraestrutura Gerenciada do SDR OS* vs *Usar Chaves Próprias (BYOK)*.
  - Inputs mascarados para chaves de API: `OpenAI API Key` (`sk-proj-...****`), `Anthropic API Key` (`sk-ant-...****`) e `DeepSeek API Key` (`sk-ds-...****`), com botões para `Testar Chave` e `Salvar Keys`.
- **Histórico de Faturas & Recibos**:
  - Tabela com faturas recentes: Data, Descrição (ex: "Mensalidade Enterprise Growth - Julho/2026"), Valor (R$ 2.490,00), Status (`Paga`), e Ação (`Baixar PDF`).

---

### 3. MODAIS INTERATIVOS E ESTADO ALPINE.JS

Garantir os seguintes modais e controles de estado no Alpine.js (`dashboardApp()`):

1. **Modal Convidar Novo Membro (`showInviteUserModal`)**:
   - Form com: Nome Completo, E-mail Corporativo, Seleção de Papel/Role (`Tenant Admin`, `SDR Manager`, `Operador SDR`, `Auditor`), e Toggle *Enviar e-mail de convite com link de acesso*.
2. **Modal Pareamento QR Code Zap (`showQrCodeModal`)**:
   - Exibição de QR Code simulado com instruções de conexão ("Abra o Zap > Aparelhos Conectados > Conectar Aparelho").
   - Timer regressivo visual de expiração do QR Code (ex: 45 segundos) e botão `Gerar Novo QR Code`.
3. **Modal Editar Configuração de CRM (`showCrmConfigModal`)**:
   - Configuração de chave de API do CRM (ex: HubSpot/Pipedrive) e mapeamento de campos (Nome -> Lead Name, E-mail -> Lead Email, Zap -> Phone).

---

### 4. ENTREGÁVEIS & QUALIDADE VISUAL

1. **Sub-Navegação Fluida**: Garantir que as 4 sub-visões operem via `settingsTab` (`organization`, `users_team`, `channels_integrations`, `billing_usage`), alterando a exibição sem recarregar a página.
2. **Design System Impecável**: Utilizar DaisyUI (cards, badges, modals, stats, tables, toggles) com transições suaves de entrada (`x-transition`).
3. **Fidelidade ao Tema White-Label**: Garantir que todas as telas de configurações respeitem e reflitam o tema ativo no sistema.

---

**FIM DO PROMPT**
