# Prompt para Agente de IA: Atualização das Telas de AI Memory & Brain no Protótipo (01_SDR_Prototype)

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI encarregado de atualizar e implementar a seção **"AI Memory & Brain"** no protótipo do **Revenue SDR OS** no repositório `01_SDR_Prototype`.

O objetivo desta tarefa é construir a experiência completa da aba **"AI Memory & Brain"** (`activeTab === 'memory'`), permitindo ao usuário gerenciar a Base de Conhecimento RAG (Vector Store & Documentos), visualizar e gerenciar o Grafo de Memórias de Longo Prazo dos Leads, configurar os Guardrails Globais de Inteligência / Segurança da IA e auditá-la através dos logs de raciocínio (Chain of Thought).

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

### 2. ESTRUTURA DAS TELAS DE AI MEMORY & BRAIN (SUB-VISÕES)

Garantir que, ao clicar em **"AI Memory & Brain"** na Sidebar principal (`activeTab = 'memory'`), a interface apresente no Header/Barra de Sub-Navegação as seguintes 4 sub-visões operacionais:

#### 📚 Sub-Visão 1: Base de Conhecimento RAG & Documentos (`memoryTab = 'knowledge_base'`)
- **Header & Estatísticas de RAG**:
  - Resumo de indexação: *Total de Documentos (ex: 28)*, *Chunks Vetoriais (ex: 1.420)*, *Modelo de Embedding (ex: text-embedding-3-large)*, *Status da Base (ex: 100% Sincronizado)*.
  - Botão de Destaque: `+ Upload de Documento` e `🧪 Testar RAG Simulator`.
- **Filtros & Busca de Documentos**:
  - Filtro por Categoria (*Todas*, *Tabelas de Preços*, *Playbook de Vendas*, *Manuais & FAQs*, *Políticas & LGPD*, *Objecões*) e campo de busca rápida.
- **Grid / Lista de Documentos Ingeridos**:
  - Cards ou tabela de documentos com:
    - Ícone por tipo de arquivo (PDF, DOCX, URL, Texto Rápido).
    - Nome do arquivo e tag de categoria.
    - Metadados: Tamanho do arquivo, quantidade de Chunks extraídos, data da última re-indexação.
    - Badge de Status de Embeddings (*Indexado*, *Processando*, *Erro*).
    - Ações rápidas: `Visualizar Chunks`, `Re-indexar`, `Excluir`.
- **Painel de Teste de RAG em Tempo Real (RAG Playground / Simulator)**:
  - Área interativa para simular perguntas que um lead faria (ex: *"Qual o prazo de cancelamento do plano anual?"*).
  - Exibição dos **Chunks Recuperados**: mostrando a pontuação de relevância (*Cosine Similarity Score %*), a fonte do documento e o trecho de texto exato usado para contextualizar o LLM.

#### 🧠 Sub-Visão 2: Memória de Longo Prazo dos Leads (Lead Memory Graph) (`memoryTab = 'lead_memories'`)
- **Header da Memória Consolidada**:
  - Métricas de Memória: *Total de Fatos Extraídos (ex: 842)*, *Score Médio de Confiança (ex: 94.8%)*, *Memórias Validadas por Humanos (ex: 312)*.
  - Filtro por Categoria de Memória (*Todas*, *Preferências*, *Fatos Financeiros/Orçamento*, *Restrições & Datas*, *Histórico de Objeções*, *Relacionamento*) e filtro por Lead.
- **Tabela / Lista de Memórias Estruturadas**:
  - Exibição dos fatos capturados pela IA ao longo das conversas:
    - **Lead Associado**: Nome do Lead com link rápido para abrir o perfil/Raio-X.
    - **Categoria**: Badge colorida da categoria (ex: 💰 *Orçamento*, 🚫 *Objeção*, 📅 *Prazo*).
    - **Chave / Atributo**: Nome da variável (ex: `orcamento_teto`, `decisor_final`, `software_atual`, `dor_principal`).
    - **Valor Extraído**: Texto exato extraído (ex: *"Possui orçamento máximo de R$ 15k/mês"*, *"Precisa aprovar com CFO Sr. Carlos"*).
    - **Confiança (AI Score)**: Badge de confiança com barra de progresso (ex: `98% Confiança`).
    - **Origem da Memória**: Badge de proveniência (ex: *WhatsApp IA*, *Transcrição de Chamada*, *Edição Manual*).
    - **Ações**: `Editar Fato`, `Aprovar/Validar`, `Remover`.

#### 🛡️ Sub-Visão 3: Guardrails, Diretrizes & Objeções (`memoryTab = 'guardrails'`)
- **Painel de Controle de Segurança & Compliance da IA**:
  - **Diretrizes de Segurança Globais**:
    - Toggles funcionais: *Conformidade LGPD estrita*, *Bloqueio de Promessas Financeiras*, *Respeito a Horário Comercial*, *Proibição de Fornecer Desconto Superior a X%*.
  - **Palavras & Tópicos Proibidos (Blacklist)**:
    - Tags de palavras ou termos vetados que a IA jamais deve citar (ex: *"garantia 100%"*, *"sem risco"*, *"desconto secreto"*).
  - **Gatilhos de Escalação Humana (Handoff Triggers)**:
    - Configuração de regras de transbordo imediato para SDRs humanos (ex: *Mencionar processo judicial*, *Pedir falar com gerente*, *Lead Enterprise > 500 funcionários*, *Objeção de segurança da informação*).
  - **Matriz de Playbook & Objeções de Vendas**:
    - Tabela de objeções mapeadas com estratégias recomendadas de contorno:
      - Objeção (ex: *"Está muito caro"*).
      - Resposta Orientada / Guideline (ex: *"Focar no ROI de redução de custo de aquisição e apresentar caso de sucesso similar"*).
      - Ação: `Editar Regra`, `Testar Resposta`.

#### 🔍 Sub-Visão 4: Auditoria & Raciocínio da IA (Brain Logs & CoT) (`memoryTab = 'brain_audit'`)
- **Central de Inspeção de Raciocínio (Chain of Thought - CoT Logs)**:
  - Stream de auditoria das últimas 50 decisões tomadas pela IA em tempo real.
  - Tabela/Cards com: Timestamp, Lead, Canal, Intenção Detectada, Confiança e Status do Guardrail (*Aprovado*, *Ajustado*, *Bloqueado pelo Guardrail*).
- **Inspector Detalhado de Raciocínio (Drawer / Card Ampliado)**:
  - Ao selecionar um log, exibe os 3 pilares do raciocínio da IA:
    - **1. Pergunta / Entradas do Lead**: Texto original recebido do WhatsApp/E-mail.
    - **2. Contexto Recuperado (RAG + Lead Memories)**: Quais documentos do RAG e quais memórias do lead foram injetados no prompt.
    - **3. Prompt Montado & Avaliação de Guardrail**: O prompt final enviado ao modelo LLM, a resposta gerada e a verificação do guardrail de segurança.
  - **Feedback & Fine-Tuning Humano (RLHF / DPO)**:
    - Botões de classificação: `👍 Resposta Perfeita`, `👎 Resposta Incorreta / Alucinação`.
    - Campo para *Corrigir Resposta e Alimentar o RAG*, aprimorando continuamente o cérebro da IA.

---

### 3. MODAIS INTERATIVOS E ESTADO ALPINE.JS

1. **Modal Upload / Ingestão de Documento RAG (`showUploadDocModal`)**:
   - Form para upload de arquivo (PDF, DOCX, TXT) ou inserção de URL/Texto.
   - Seleção da Categoria de Conhecimento e opções de fragmentação (Chunk Size / Overlap).
   - Barra de progresso visual de processamento de embeddings ao salvar.
2. **Modal Adicionar / Editar Memória de Lead (`showAddMemoryModal`)**:
   - Seletor do Lead, Categoria da Memória, Chave/Variável, Valor e Confiança.
3. **Modal/Drawer RAG Playground (`showRagSimulatorModal`)**:
   - Simulador interativo em janela inteira ou drawer para testar prompts e visualizar busca vetorial em tempo real.
4. **Modal Novo Guardrail / Gatilho de Handoff (`showGuardrailModal`)**:
   - Form para adicionar palavras proibidas, gatilhos de escalação humana ou diretrizes de vendas.

---

### 4. ESTADO ALPINE.JS (MOCK DATASETS & CONTROLES)

Adicionar/expandir no `dashboardApp()` do `index.html`:
- `memoryTab: 'knowledge_base'` (sub-visões: `'knowledge_base'`, `'lead_memories'`, `'guardrails'`, `'brain_audit'`)
- `searchMemoryQuery: ''`, `selectedCategoryFilter: 'all'`
- `showUploadDocModal: false`, `showAddMemoryModal: false`, `showRagSimulatorModal: false`, `showGuardrailModal: false`
- Mock Dataset `documentsList`: 6+ documentos realistas (ex: *Tabela de Preços 2026.pdf*, *Playbook de Objeções B2B.docx*, *Política de Garantia & Cancelamento.pdf*, *Manual da Clínica Bela Health.pdf*).
- Mock Dataset `leadMemoriesList`: 8+ memórias detalhadas de leads (ex: *Dr. Roberto Alves*, *Mariana Costa*, *Carlos Eduardo*).
- Mock Dataset `guardrailsConfig`: Palavras proibidas, gatilhos de handoff e diretrizes ativas.
- Mock Dataset `brainAuditLogs`: 5+ logs recentes de raciocínio CoT com insumos de RAG e avaliação de guardrail.

---

### 5. CHECKLIST DE VALIDAÇÃO
- [ ] Clicar em **"AI Memory & Brain"** na sidebar ativa a aba principal (`activeTab === 'memory'`).
- [ ] As 4 sub-visões no header/topo (*Base de Conhecimento RAG*, *Memória dos Leads*, *Guardrails & Objeções*, *Auditoria & Raciocínio*) alternam dinamicamente sem recarregar a página.
- [ ] O RAG Simulator / Playground permite digitar uma pergunta e exibe os chunks mockados recuperados com score de relevância.
- [ ] A tabela de Memórias dos Leads traz filtros por categoria e ação de validação humana.
- [ ] O painel de Guardrails exibe os toggles de compliance e os gatilhos de escalação humana de forma clara.
- [ ] O leitor de Logs de Raciocínio (Chain of Thought) abre a inspeção detalhada dos 3 pilares da decisão da IA.
- [ ] A alteração do preset de tema White-Label no header reflete perfeitamente nas novas telas.

***

**FIM DO PROMPT.**
