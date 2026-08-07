# Prompt para Agente de IA: Etapa 01 - Layout Base Standalone do Prototótipo Zap SDR OS

> **Instruções para o Dono do Projeto:** Envie este prompt para o seu agente de codificação para construir a Etapa 01 do sub-produto `01_SDR_Prototipo`.

***

**INÍCIO DO PROMPT:**

Você é um Engenheiro de Frontend Especialista focado em UX/UI, encarregado de criar a estrutura de layout do sub-produto **01_SDR_Prototipo (Zap SDR OS Standalone App)**.
O objetivo desta tarefa é construir uma interface de atendimento estritamente focada e leve, que possa ser executada de forma **isolada (standalone)** por vendedores e clientes, enquanto garante o **compartilhamento automático de todos os dados coletados com o sistema principal (`Revenue SDR OS / 00_SDR_architecture`)**.

**REGRAS DE ARQUITETURA E STACK (OBRIGATÓRIO - ADR-001 e ADR-013):**
1. **Aplicação Standalone & Focada**: Desenvolva uma interface limpa em HTML5 + Tailwind CSS + DaisyUI + Alpine.js que não exija navegação para menus administrativos do sistema central.
2. **Estilização**: Utilize **Tailwind CSS (v3)** + **DaisyUI (v4)**.
3. **Interatividade**: Inicialize o **Alpine.js (v3)** e configure o `Alpine.store('sdrApp')` com suporte a `isStandalone: true` e `autoSyncStatus: 'synced'`.
4. **Design White-Label (5 Temas CSS)**: Implemente o seletor de temas no Header permitindo alternar dinamicamente entre:
   - `theme-sakura` (Sakura Bloom)
   - `theme-emerald` (Emerald Garden)
   - `theme-ocean` (Ocean Breeze)
   - `theme-obsidian` (Obsidian Night - Dark Mode inspirado no Zap Web)
   - `theme-amber` (Amber Warmth)

---

### O QUE VOCÊ DEVE DESENVOLVER NESTA ETAPA:

1. **Header Superior Standalone & Auto-Sync Status**:
   - Logo / Título: `Zap SDR Copilot (Standalone)`.
   - Seletor de Temas (Dropdown DaisyUI com os 5 presets).
   - Badge de Status de Auto-Sync com o Sistema Principal: `<span class="badge badge-success gap-2">🟢 Auto-Sync com Core SDR OS (Org: clinica-bela)</span>`.

2. **Layout Principal em Grid de 3 Colunas**:
   - **Coluna 1 (Esquerda - 300px/320px)**:
     - Header da Sidebar: Avatar do vendedor, campo de busca de conversas ativas.
     - Lista de Conversas / Leads: Leads mockados com avatar, nome, última mensagem, horário e tag de status.
   - **Coluna 2 (Central - Flex Grow)**:
     - Header da Conversa Ativa: Avatar do Lead, status online, indicador do modo IA ("🤖 AI Copilot Active") e alternador para modo Humano.
     - Área de Histórico de Mensagens: Balões estilo Zap Web com micro-badges de sincronização em segundo plano.
     - Rodapé de Input de Mensagens: Campo flexível `#messageInput` e botão enviar.
   - **Coluna 3 (Direita - 400px - Container dos Painéis Extras IA)**:
     - Container estruturado pronto para os **Painéis Extras de DHS (Gráfico) e Sugestões RAG**.

3. **Injeção de Dados Mockados no Alpine Store**:
   - Configure o `Alpine.store('sdrApp')` com dados iniciais de leads e métodos para registrar eventos isolados de chat e agendar a transmissão automática em background para a API do `00_SDR_architecture`.

Entendido? Crie a estrutura HTML5 standalone completa e responsiva em `index.html` demonstrando a operação isolada do Zap Copilot e o indicador de Auto-Sync!

***
**FIM DO PROMPT.**
