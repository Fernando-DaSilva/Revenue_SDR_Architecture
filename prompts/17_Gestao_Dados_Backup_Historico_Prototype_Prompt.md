# Prompt para Agente de IA: Módulo de Gestão de Dados, Backup e Histórico de Conversas (01_SDR_Prototype)

> **Instrução para o usuário:** Copie o prompt abaixo e envie para o seu agente de codificação no workspace `01_SDR_Prototype` (ou execute-o diretamente no repositório do protótipo).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro Frontend Especialista em UX/UI encarregado de implementar o novo módulo de **"Gestão de Dados, Backup & Histórico de Conversas"** (`activeTab === 'data_management'`) no protótipo do **Revenue SDR OS** no repositório `01_SDR_Prototype`.

O objetivo desta tarefa é construir a experiência completa do painel de controle de infraestrutura de dados e histórico, refletindo a arquitetura de **Storage Tiering (ADR-002, ADR-015 e ADR-016)** que combina **Hot Storage** (Turso / libSQL local) e **Cold Storage** (PostgreSQL / Supabase DW com `pgvector` e Full-Text Search), permitindo a auditoria de backups, histórico de conversas antigas e execução de jobs D-1.

---

### 1. REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 / ADR-013 / ADR-015)
1. **Frontend Server-Driven & Estático**: Utilize HTML5 semântico com Tailwind CSS + DaisyUI + Alpine.js. Não introduza frameworks SPA pesados (como React ou Vue).
2. **Estilização White-Label**: Mantenha integração total com os 5 presets de temas White-Label dinâmicos no Header (`Sakura Bloom`, `Emerald Garden`, `Ocean Breeze`, `Obsidian Night`, `Amber Warmth`).
3. **Zero Backend / Client Mock State**: Mantenha todo o estado, estatísticas de uso de banco, backups e dados de histórico mockados reativamente diretamente no componente Alpine.js (`dashboardApp()`).

---

### 2. ESTRUTURA DO MÓDULO "GESTÃO DE DADOS & HISTÓRICO" (`activeTab === 'data_management'`)

Ao clicar em **"Gestão de Dados & Histórico"** no Menu Principal / Sidebar, a interface apresentará no topo um Header de Módulo e uma navegação por abas (`dataTab`) com **3 Sub-visões Operacionais**:

---

#### 📊 Sub-Visão 1: Storage Tiering & Pipeline D-1 (`dataTab === 'tiering_retention'`)
* **KPIs de Capacidade de Armazenamento**:
  * **Card Hot Storage (Turso / libSQL Local)**: Exibe o tamanho do arquivo `.db` local (ex: `142.5 MB / 500 MB`), total de conversas ativas (ex: `1.240`), latência média de leitura (`< 4ms`) e indicador visual de saúde (Badge Green).
  * **Card Cold Storage / DW (PostgreSQL / Supabase)**: Exibe tamanho acumulado no DW (ex: `12.8 GB`), mensagens arquivadas (ex: `450.200`), status das extensões (`pgvector` Ativo, `tsvector` Ativo).
  * **Card Status do Job ETL D-1**: Exibe o horário da última sincronização D-1 (ex: `Hoje às 02:00 AM`), contagem de registros migrados nas últimas 24h e próximo disparo agendado.
* **Painel de Configuração de Regras de Retenção & TTL**:
  * Input de Dias de Retenção no Hot DB (ex: `30 dias` por padrão para conversas ativas).
  * Toggle: *Reter conversas de leads com status "Em Negociação" indefinidamente no Hot DB*.
  * Toggle: *Executar expurgo automático (`DELETE` + `VACUUM`) após confirmação de cópia no Cold DB*.
  * Botão de Ação: `⚡ Executar Pipeline ETL D-1 Manualmente (On-Demand)`.
* **Tabela de Monitoramento de Jobs de Sincronização**:
  * Lista dos últimos 5 jobs D-1 executados com colunas: *Data/Hora*, *Tipo de Job (ETL D-1 / Vacuum / Backup)*, *Registros Processados*, *Status (Sucesso/Alerta)* e *Duração*.

---

#### 🔍 Sub-Visão 2: Histórico de Conversas & Cold Search (`dataTab === 'conversation_history'`)
* **Barra de Busca Inteligente (Full-Text & Semântica / RAG)**:
  * Input de busca com seletor de modo: `🔍 Busca Por Texto Exato (FTS)` vs `🧠 Busca Semântica por Contexto (pgvector)`.
  * Filtros avançados: *Período (Ex: Últimos 6 meses, Ano anterior)*, *Canal (Zap, E-mail, Telefone)*, *SDR Responsável (IA ou Humano)*, *Status do Lead*.
* **Visualizador de Threads Arquivadas**:
  * Lista de conversas históricas encontradas com destaque visual de badge `[Cold Storage - Postgres/Supabase]`.
  * Drawer / Modal de Inspeção Completa do Chat: Ao clicar na conversa, abre a transcrição completa com tags de horário, remetente (Lead / AI SDR), pontuação de sentimento e resumo gerado pela IA.
* **Ações no Histórico**:
  * Botão `📥 Exportar Transcrição (JSON / PDF / CSV)`.
  * Botão `🔄 Restaurar Lead para o Hot DB` (Re-injeta o histórico do lead no Turso local para atendimento imediato).

---

#### 💾 Sub-Visão 3: Backups, Embedded Replicas & Desastre (`dataTab === 'backup_restore'`)
* **Status das Replicas Incorporadas (Turso Cloud Sync)**:
  * Widget de saúde da sincronização entre o `.db` local e o cluster Turso na nuvem.
  * Status da replicação: *Sincronizado em tempo real (0 ms de atraso)*.
* **Gestão de Snapshots & Backups Locais**:
  * Tabela com histórico de snapshots do banco de dados (`.db` local e dumps SQL):
    * *Nome do Arquivo* (ex: `snapshot_2026-07-27_0200.db.gz`).
    * *Tamanho* (ex: `138 MB`).
    * *Tipo* (Automático D-1 / Manual).
    * *Checksum SHA-256*.
    * *Ações*: `⬇️ Download`, `🔄 Simular Restore`, `🗑️ Excluir`.
  * Botão de Destaque: `💾 Criar Snapshot de Backup Agora (On-Demand)`.
* **Modal de Simulação de Disaster Recovery (Restore Test)**:
  * Modal interativo permitindo selecionar um backup antigo e simular o processo de restore com barra de progresso mockada e logs em tempo real.

---

### 3. DADOS MOCKADOS REQUISITADOS NO ALPINE.JS (`dashboardApp()`)

Instanciar a chave `dataManagement` no estado reativo do Alpine.js:

```javascript
dataManagement: {
  hotStorage: { sizeMb: 142.5, maxMb: 500, activeConversations: 1240, readLatencyMs: 3.8, status: 'healthy' },
  coldStorage: { sizeGb: 12.8, totalArchivedMessages: 450200, pgvectorActive: true, ftsActive: true, provider: 'Supabase (PostgreSQL)' },
  etlJob: { lastRun: '2026-07-27 02:00:00', recordsProcessed: 14250, nextRun: '2026-07-28 02:00:00', status: 'completed' },
  retentionDays: 30,
  keepActiveLeadsInHot: true,
  autoVacuum: true,
  searchMode: 'fts', // 'fts' ou 'semantic'
  searchQuery: '',
  searchResults: [
    { id: 'hist_101', leadName: 'Dr. Roberto Alves', company: 'Clínica Sorriso', channel: 'Zap', date: '2026-03-14', messageCount: 42, matchSnippet: '...gostaria de agendar a demonstração sobre o plano premium...' },
    { id: 'hist_102', leadName: 'Mariana Lima', company: 'Imóveis Prime', channel: 'Zap', date: '2026-02-20', messageCount: 28, matchSnippet: '...fechamos a proposta conforme enviado no contrato...' }
  ],
  backups: [
    { id: 'bak_01', filename: 'rsdr_snapshot_2026-07-27_0200.db.gz', size: '138.4 MB', type: 'Automático D-1', date: '2026-07-27 02:00', checksum: 'a8f9c2d1...' },
    { id: 'bak_02', filename: 'rsdr_snapshot_2026-07-26_0200.db.gz', size: '136.1 MB', type: 'Automático D-1', date: '2026-07-26 02:00', checksum: 'b7e8d3c2...' }
  ]
}
```

---

### 4. CHECKLIST DE VALIDAÇÃO VISUAL
- [ ] A navegação por abas (`tiering_retention`, `conversation_history`, `backup_restore`) alterna suavemente sem recarregar a página.
- [ ] O modo de busca (FTS vs Semântica) altera dinamicamente os badges e explicações na UI.
- [ ] As tabelas de backup e logs possuem visual limpo com badges do DaisyUI (`badge-success`, `badge-info`, `badge-warning`).
- [ ] O modal de restauração exibe um indicador de progresso dinâmico simulado.
- [ ] Presets de cores White-Label do Header aplicam-se perfeitamente aos gráficos e botões deste módulo.

**FIM DO PROMPT.**
