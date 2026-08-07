# Prompt para Agente de IA: Etapa 04 - Motor de Simulação Interativa & Inspector de Auto-Sync em Background

> **Instruções para o Dono do Projeto:** Envie este prompt para o seu agente de codificação para implementar a Etapa 04 no repositório do sub-produto `01_SDR_Prototipo`.

***

**INÍCIO DO PROMPT:**

Você é um Engenheiro de Software Fullstack e especialista em UX Interativa, encarregado de finalizar a **Etapa 04: Motor de Simulação em Tempo Real e Inspector de Auto-Sync em Background** no aplicativo standalone **01_SDR_Prototipo**.

O objetivo desta etapa é permitir que o aplicativo funcione **100% isolado no navegador para os vendedores e clientes**, enquanto demonstra visualmente o **compartilhamento automático e contínuo de todos os dados coletados com o sistema central (`Revenue SDR OS / 00_SDR_architecture`)**.

---

### O QUE VOCÊ DEVE DESENVOLVER NESTA ETAPA:

1. **Simulador de Interações da Conversa (Lead Message Generator)**:
   - Crie uma barra de ferramentas no topo com cenários pré-configurados:
     - **Cenário 1: Objeção Severa de Preço** (Lead envia objeção -> DHS cai -25 pts -> Auto-Sync envia alerta de risco para o CRM central).
     - **Cenário 2: Pergunta Técnica / Garantia** (Lead questiona integração -> DHS neutro -> Busca sugestão na RAG central).
     - **Cenário 3: Avanço de Fechamento** (Lead aceita proposta -> DHS avança +35 pts -> Auto-Sync atualiza oportunidade no pipeline central).
     - **Cenário 4: Envio de Áudio pelo Lead** (Simula mensagem de áudio com transcrição Whisper).

2. **Dispatcher Automático em Background (Auto-Sync Queue)**:
   - Sempre que uma mensagem é trocada ou uma sugestão é aceita:
     1. O evento é inserido no chat localmente para o vendedor/lead.
     2. O **Gráfico DHS (Painel Extra 1)** atualiza a saúde da negociação.
     3. O **Painel de Sugestões (Painel Extra 2)** renova as recomendações.
     4. A função `dispatchAutoSyncEvent` empacota a transação e envia em segundo plano para o `00_SDR_architecture`.
     5. Em caso de queda simulada da rede, o evento é retido no `localStorage` e sincronizado na reconexão.

3. **Inspector de Transmissão Automática (`Core Auto-Sync Data Stream Log`)**:
   - Uma gaveta colapsável no rodapé da aplicação (com o botão `🔍 Ver Tráfego Auto-Sync com Core SDR OS`).
   - Ao abrir, exibe em tempo real o payload JSON que é compartilhado com a API principal em background:
```json
{
  "sync_event_id": "evt_9918231",
  "app_mode": "STANDALONE_MICRO_APP",
  "tenant_key": "sk_live_clinica_bela",
  "lead_identifier": "+55 47 92002-9033",
  "collected_data": {
    "latest_message": "Fechado assim! Podemos definir a data para a 1a semana de Setembro.",
    "sentiment_dhs_score": 88,
    "lead_objections_resolved": ["price", "timeline"],
    "ai_suggestion_accepted": "sug_1"
  },
  "auto_synced_at": "2026-08-06T11:27:00Z"
}
```

4. **Validação da Operação Isolada**:
   - Garantir que a experiência de uso do vendedor e do lead seja fluida, sem depender do carregamento dos dashboards do sistema principal.
   - Manter a responsividade e a troca impecável das 5 paletas White-Label.

Entendido? Implemente a simulação interativa, a fila offline resiliente e o Inspector de Auto-Sync em Background entre o app isolado e o Core OS!

***
**FIM DO PROMPT.**
