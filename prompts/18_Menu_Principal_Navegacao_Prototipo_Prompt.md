# Prompt para Agente de IA: Atualização do Menu Principal e Estrutura de Navegação da UI (01_SDR_Prototype)

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI encarregado de atualizar o **Menu Principal / Sidebar Lateral** do protótipo do **Revenue SDR OS** no repositório `01_SDR_Prototype`.

O objetivo desta tarefa é reorganizar e enriquecer o menu de navegação principal, incluindo a nova opção dedicada **"Gestão de Dados & Histórico"** (`activeTab === 'data_management'`) e garantindo que todas as telas, sub-visões e ferramentas operacionais do sistema estejam perfeitamente categorizadas e acessíveis de forma clara e profissional.

---

### 1. REGRAS DE DESIGN E ARQUITETURA (ADR-001 / ADR-013)
1. **Estilo & Componentização**: Utilize Tailwind CSS + DaisyUI. O menu lateral (Sidebar) deve suportar estado recolhido/expandido (`sidebarCollapsed: false`), responsividade mobile (drawer) e badges informativos de notificação.
2. **Integração White-Label**: O menu deve respeitar as cores primárias do tema ativo selecionado (Sakura Bloom, Emerald Garden, Ocean Breeze, Obsidian Night, Amber Warmth) e exibir a logo do Tenant no topo da Sidebar.
3. **Indicador de Aba Ativa**: Destaque sutil com borda lateral primária e fundo levemente destacado (`bg-primary/10 text-primary font-semibold`) para a opção selecionada (`activeTab`).

---

### 2. ESTRUTURA COMPLETA DAS OPÇÕES DO MENU PRINCIPAL

A Sidebar principal deve ser organizada nas seguintes **5 Categorias Semânticas**:

```
+-------------------------------------------------------------+
|  [LOGO TENANT]  Revenue SDR OS                 [< Collapse] |
+-------------------------------------------------------------+
|  📍 OPERAÇÃO & ATENDIMENTO                                  |
|   • 📊 Pipeline & Leads            (activeTab: 'pipeline')  |
|   • 🎯 Central de Controle / DHS  (activeTab: 'dhs')       |
|   • 💬 Inbox de Atendimento       (activeTab: 'inbox')     |
|                                                             |
|  🤖 INTELIGÊNCIA & AUTOMAÇÃO                                |
|   • ⚡ Cadências & Agentes IA     (activeTab: 'cadences')  |
|   • 🧠 Memória & Revenue Brain    (activeTab: 'brain')     |
|                                                             |
|  ⚙️ INFRAESTRUTURA DE DADOS (NOVA OPÇÃO)                    |
|   • 🗄️ Gestão de Dados & Histórico (activeTab: 'data_management') |
|     └─ Sub-visões: Tiering D-1 | Cold Search | Backup & Restore |
|                                                             |
|  🎨 PERSONALIZAÇÃO & MARCA                                  |
|   • 🎨 Studio de Temas White-Label (activeTab: 'theme_studio')|
|                                                             |
|  🏢 ADMINISTRAÇÃO TENANT                                    |
|   • ⚙️ Configurações Tenant       (activeTab: 'settings')  |
|   • 💳 Planos, Faturamento & Cotas (activeTab: 'billing')   |
+-------------------------------------------------------------+
|  👤 [Avatar Admin] User Name      [🔒 Sair / Dropdown]       |
+-------------------------------------------------------------+
```

---

### 3. DETALHAMENTO DAS OPÇÕES E SUB-TELAS NO MENU

#### Categoria 1: 📍 Operação & Atendimento
* **📊 Pipeline & Leads (`activeTab === 'pipeline'`)**:
  * *Funções UI:* Visualização em Kanban por fases do funil, lista detalhada de leads, drawer de jornada do lead, atalhos de qualificação rápida e scoring.
* **🎯 Central de Controle / DHS (`activeTab === 'dhs'`)**:
  * *Funções UI:* Monitoramento em tempo real do SDR Humano + IA, fila de execução diária (Daily High-Speed), métricas operacionais e confirmação de ações de Copilot.
* **💬 Inbox de Atendimento (`activeTab === 'inbox'`)**:
  * *Funções UI:* Chat multicanal (WhatsApp/E-mail) unificado, envio de mensagens manuais, assunção de conversa (Handoff IA -> Humano).

#### Categoria 2: 🤖 Inteligência & Automação
* **⚡ Cadências & Agentes IA (`activeTab === 'cadences'`)**:
  * *Funções UI:* Construtor de réguas de contato, configuração de personas da IA SDR, cadências multicanal, regras de transição de etapa e tom de voz.
* **🧠 Memória & Revenue Brain (`activeTab === 'brain'`)**:
  * *Funções UI:* Base de conhecimento da empresa, objeções e respostas treinadas, regras de negócio para RAG e memórias do assistente.

#### Categoria 3: 🗄️ Infraestrutura de Dados (NOVA OPÇÃO NO MENU)
* **🗄️ Gestão de Dados & Histórico (`activeTab === 'data_management'`)**:
  * *Badge de Destaque:* `[NOVO]` ou indicador de saúde da base (`OK`).
  * *Sub-visões elencadas:*
    1. **Storage Tiering & Retenção D-1** (Uso de disco Turso Hot vs Postgres Cold Storage, parametrização de TTL).
    2. **Histórico de Conversas & Cold Search** (Pesquisa FTS e Semântica RAG em mensagens arquivadas, exportação de transcrições).
    3. **Backups, Replicas & Restauração** (Status de sincronia Turso Cloud, snapshots `.db`, simulação de Disaster Recovery).

#### Categoria 4: 🎨 Personalização & Marca
* **🎨 Studio de Temas White-Label (`activeTab === 'theme_studio'`)**:
  * *Funções UI:* Preview e alternância em tempo real entre os 5 presets (Sakura Bloom, Emerald Garden, Ocean Breeze, Obsidian Night, Amber Warmth), personalização de variáveis CSS e logos.

#### Categoria 5: 🏢 Administração Tenant
* **⚙️ Configurações Tenant (`activeTab === 'settings'`)**:
  * *Sub-visões:* Perfil da Organização, Gestão da Equipe & Permissões RBAC, Conectores de Canais (WhatsApp/E-mail/CRM), Tradução e Localização de Telas.
* **💳 Planos, Faturamento & Cotas (`activeTab === 'billing'`)**:
  * *Funções UI:* Monitoramento de consumo de tokens de IA, licenças de usuários, histórico de faturas e upgrade de plano.

---

### 4. COMPORTAMENTO ALPINE.JS & ESTADO DA SIDEBAR

Garantir que a Sidebar reaja aos seguintes estados reativos no Alpine.js:

```javascript
// Atributos no dashboardApp()
sidebarCollapsed: false, // Suporte a menu recolhido (exibindo apenas ícones com tooltips)
activeTab: 'pipeline',   // Aba selecionada por padrão
dataManagement: {
  activeSubTab: 'tiering_retention' // Sub-visão ativa no Módulo de Gestão de Dados
}
```

- **Tooltips na Sidebar Recolhida**: Quando `sidebarCollapsed === true`, os itens do menu exibem tooltips DaisyUI (`tooltip tooltip-right`) ao passar o mouse.
- **Badge Informativo**: A nova opção "Gestão de Dados & Histórico" inclui um pequeno badge visual mostrando o status do backup (`badge-success badge-xs` com ponto pulsante).

---

### 5. CHECKLIST DE VALIDAÇÃO VISUAL DA SIDEBAR
- [ ] O menu principal inclui formalmente a nova opção **"Gestão de Dados & Histórico"** com o ícone `🗄️` / `database`.
- [ ] Ao clicar em cada item do menu, a variável `activeTab` é atualizada e a área de conteúdo principal exibe a tela correspondente.
- [ ] O botão de alternar expansão/recolhimento da Sidebar (`sidebarCollapsed = !sidebarCollapsed`) funciona perfeitamente sem quebrar o layout.
- [ ] O menu responsivo para telas móbiles fecha o drawer automaticamente ao selecionar uma opção.
- [ ] As cores ativas do menu acompanham o tema White-Label ativo no sistema.

**FIM DO PROMPT.**
