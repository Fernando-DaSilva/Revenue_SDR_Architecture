# Prompt para Agente de IA: Etapa 02 - Painel DHS com Sincronização Automática no CRM Central

> **Instruções para o Dono do Projeto:** Envie este prompt para o seu agente de codificação para implementar a Etapa 02 no repositório do sub-produto **02_ZAP_Prototype**.

***

**INÍCIO DO PROMPT:**

Você é um Engenheiro de Frontend Especialista em Visualização de Dados e UX/UI, encarregado de implementar o **Painel Extra 1: Gráfico de Sentimento / Saúde da Negociação (Dynamic Health Score - DHS)** no sub-produto **02_ZAP_Prototype (Standalone Micro-App)**.

O objetivo desta etapa é construir o gráfico de linha temporal em **Chart.js v4** na Coluna 3 que monitora a conversa minuto a minuto e **transmite automaticamente em background todas as variações de score para o CRM do sistema principal (`Revenue SDR OS / 00_SDR_architecture`)**:
- **Movimento Positivo (+)**: Transmite avanço da oportunidade em direção ao fechamento.
- **Movimento Negativo (-)**: Transmite sinal de risco de perda e objeção para o pipeline central.

---

### O QUE VOCÊ DEVE DESENVOLVER NESTA ETAPA:

1. **Estrutura Visual do Painel DHS (Coluna 3 Superior)**:
   - Cabeçalho do Painel: Título `Saúde da Negociação (DHS)` + Score Atual (ex: `+78 / 100`) + Badge `<span class="badge badge-info text-xs">Auto-Push CRM</span>`.
   - Card de Métrica: Indicador visual de variação (ex: `▲ +15 pts - Avanço no Fechamento`).
   - Elemento do Gráfico: `<canvas id="dhsChart" class="w-full h-48"></canvas>`.

2. **Integração com Chart.js v4**:
   - Inicialize o gráfico de linha responsivo com curvas suaves e atualização reativa via `Alpine.store('sdrApp').refreshChart()`.
   - Configuração de **Eixo X** (minutos `11:00`, `11:05`, `11:10`...) e **Eixo Y** (`-100` a `+100` com linha zero neutra).
   - Linha adaptativa (Verde `#10b981` para tendência positiva, Vermelha `#f43f5e` para tendência negativa).

3. **Auto-Push de Métricas para o Sistema Central**:
   - Sempre que o score DHS for alterado via `updateDhsScore(delta, reason)`, dispare a função em background:
     `dispatchAutoSyncEvent('PIPELINE_SCORE_UPDATE', { leadId, leadName, currentDhsScore, trend, reason })`.

4. **Barra de Testes de Sentimento (Dev Simulation Bar)**:
   - Botões de simulação rápida para testar a reação do gráfico e o auto-push para o Core OS:
     - `🔴 Objeção de Preço (-20 pts)`
     - `🟡 Recuperação (+40 pts)`
     - `🟢 Fechamento (+25 pts)`
     - `⚠️ Objeção Crítica (-45 pts)`

Entendido? Implemente o Painel DHS com Chart.js v4, garantindo a atualização reativa por minutos e o envio automático das métricas em background para o CRM do projeto central!

***
**FIM DO PROMPT.**

