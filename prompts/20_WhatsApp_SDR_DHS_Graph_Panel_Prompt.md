# Prompt para Agente de IA: Etapa 02 - Painel DHS com Sincronização Automática no CRM Central

> **Instruções para o Dono do Projeto:** Envie este prompt para o seu agente de codificação para implementar a Etapa 02 no repositório do sub-produto `01_SDR_Prototipo`.

***

**INÍCIO DO PROMPT:**

Você é um Engenheiro de Frontend Especialista em Visualização de Dados e UX/UI, encarregado de implementar o **Painel Extra 1: Gráfico de Sentimento / Saúde da Negociação (Dynamic Health Score - DHS)** no sub-produto **01_SDR_Prototipo (Standalone)**.

O objetivo desta etapa é construir o gráfico de linha temporal em Chart.js na Coluna 3 que monitora a conversa minuto a minuto e **transmite automaticamente em background todas as variações de score para o CRM do sistema principal (`Revenue SDR OS / 00_SDR_architecture`)**:
- **Movimento Positivo (+)**: Transmite avanço da oportunidade em direção ao fechamento.
- **Movimento Negativo (-)**: Transmite sinal de risco de perda e objeção para o pipeline central.

---

### O QUE VOCÊ DEVE DESENVOLVER NESTA ETAPA:

1. **Estrutura Visual do Painel DHS (Coluna 3 Superior)**:
   - Cabeçalho do Painel: Título `Saúde da Negociação (DHS)` + Score Atual (ex: `+78 / 100`) + Badge `<span class="badge badge-info text-xs">Auto-Push CRM</span>`.
   - Card de Métrica: Indicador visual de variação (ex: `▲ +15 pts - Avanço no Fechamento`).
   - Elemento do Gráfico: `<canvas id="dhsChart" class="w-full h-48"></canvas>`.

2. **Integração com Chart.js v4**:
   - Inicialize o gráfico de linha responsivo com curvas suaves e atualização reativa via Alpine.js.
   - Configuração de **Eixo X** (minutos) e **Eixo Y** (`-100` a `+100` com linha zero neutra).
   - Linha adaptativa (Verde para tendência positiva, Vermelha/Âmbar para tendência negativa).

3. **Auto-Push de Métricas para o Sistema Central**:
   - Sempre que o score DHS for alterado, dispare a função em background `dispatchAutoSyncEvent('PIPELINE_SCORE_UPDATE', { leadId, currentDhsScore, trend })`.
   - Exiba um aviso discreto no topo do chat: `[Auto-Sync: CRM Pipeline Deal Score updated to 78%]`.

4. **Barra de Testes de Sentimento (Dev Simulation Bar)**:
   - Botões de simulação rápida para testar a reação do gráfico e o auto-push para o Core OS:
     - `🟢 Simular Acordo/Fechamento (+20 pts)`
     - `🔴 Simular Objeção de Preço (-15 pts)`
     - `🟡 Simular Pergunta Neutra (+0 pts)`

Entendido? Implemente o Painel DHS com Chart.js, garantindo a atualização reativa por minutos e o envio automático das métricas em background para o CRM do projeto central!

***
**FIM DO PROMPT.**
