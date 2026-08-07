# Prompt para Agente de IA: Etapa 03 - Painel de Sugestões de Resposta Alimentado pela RAG Central

> **Instruções para o Dono do Projeto:** Envie este prompt para o seu agente de codificação para implementar a Etapa 03 no repositório do sub-produto `01_SDR_Prototipo`.

***

**INÍCIO DO PROMPT:**

Você é um Engenheiro de Frontend Especialista em UX/UI e RAG Interfaces, encarregado de implementar o **Painel Extra 2: Sugestões de Respostas Inteligentes (AI Sales Assistant)** no aplicativo standalone **01_SDR_Prototipo**.

O objetivo desta etapa é construir um painel lateral na metade inferior da Coluna 3 que consulta remotamente em tempo real a Base de Conhecimento RAG do **Revenue SDR OS (`00_SDR_architecture`)**, permitindo ao vendedor isolado responder com dados precisos e fechar vendas rapidamente.

---

### O QUE VOCÊ DEVE DESENVOLVER NESTA ETAPA:

1. **Estrutura Visual do Painel de Sugestões (Coluna 3 Inferior)**:
   - Header do Painel: Título `Sugestões de Resposta (AI Copilot)` + Ícone de lâmpada + Badge `<span class="badge badge-accent text-xs">RAG Connected</span>`.
   - Campo de Busca Rápida: Input `<input type="text" placeholder="Buscar na base RAG central..." x-model="searchQuery">`.
   - Abas de Navegação (DaisyUI Tabs):
     - `Respostas da Q&A` (FAQ oficial de vendas).
     - `Documentos RAG` (Trechos de manuais, tabela de preços e políticas).

2. **Cards de Sugestão de Resposta**:
   - Cada card deve conter:
     - **Título/Categoria**: Ex: `Fechamento de Acordo / Prazos`, `Contorno de Objeção / Preço`.
     - **Texto Recomendado**: Parágrafo formatado com o texto de resposta.
     - **Score de Confiança**: Badge destacado `<span class="badge badge-primary font-bold">Score 95%</span>`.
     - **Origem RAG Central**: Tag da fonte (`Fonte: Memory Brain - Core SDR OS`).
     - **Botão Usar esta resposta (`useSuggestion`)**: Botão com ícone que insere o texto diretamente no input do chat `#messageInput` com foco automático.

3. **Compartilhamento da Escolha do Vendedor (Auto-Sync Feedback)**:
   - Quando o vendedor seleciona uma sugestão e envia a mensagem, o app dispara um evento em background: `dispatchAutoSyncEvent('AI_SUGGESTION_USED', { suggestionId, text, score })` para registrar o feedback no Memory Brain do projeto central.

Entendido? Construa o Painel de Sugestões de Resposta conectado à base RAG central com busca rápida, score de confiança e auto-sync de feedback!

***
**FIM DO PROMPT.**
