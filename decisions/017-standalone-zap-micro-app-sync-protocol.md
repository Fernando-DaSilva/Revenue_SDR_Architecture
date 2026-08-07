# ADR-017 — Arquitetura de Standalone Zap SDR Micro-App, Grid de Painéis 3 Colunas e Protocolo de Auto-Sync em Background

## Contexto

Para maximizar a eficiência dos vendedores e SDRs no atendimento ao vivo via WhatsApp, bem como permitir testes e operações descentralizadas sem carregar interfaces administrativas pesadas, foi desenvolvido o sub-produto **02_ZAP_Prototype (Zap SDR Standalone Micro-App)**.

A aplicação precisa funcionar de forma **100% autônoma, leve e offline-resiliente**, oferecendo uma experiência nativa de chat estilo Zap Web. Ao mesmo tempo, todas as ações realizadas pelo operador (envio de mensagens, alternância de modos IA Copiloto / Humano, aceitação de sugestões RAG, áudios com transcrição Whisper e variações de humor/interesse do lead) DEVEM ser transmitidas continuamente em segundo plano para o core backend do **Revenue SDR OS (`00_SDR_architecture`)**.

## Decisão

Adotar a arquitetura de **Standalone Micro-App de Atendimento com Sincronização Automática em Background**:

1. **Interface Focada & Grid de 3 Colunas Customizável**:
   - **Coluna 1 (Sidebar)**: Lista de conversas ativas, status dos leads, badges de modo e busca em tempo real.
   - **Coluna 2 (Central Chat Stream)**: Chat estilo Zap Web com alternador de modo (`🤖+👤 IA Copiloto` vs `👤 SDR Humano`), player interativo de áudio com transcrição Whisper e indicadores de sincronização em cada mensagem.
   - **Coluna 3 (Painéis de Inteligência)**: Gráfico de Saúde da Negociação (**DHS Score -100 a +100**) via Chart.js v4 e Sugestões de Respostas Inteligentes alimentadas pela Base RAG (`qa` e `docs`) com score de confiança e botão **"Usar esta resposta"**.
   - **Controle Dinâmico de Layout**: Suporte a movimentação lateral de painéis (move left/right), minimizar, maximizar e restaurar layout.

2. **Protocolo de Auto-Sync em Background (`dispatchAutoSyncEvent`)**:
   - Transmissão contínua de eventos estruturados em JSON para os endpoints centrais (`/v1/copilot/sync`, `/v1/copilot/dhs`, `/v1/copilot/suggestions`).
   - Resiliência Offline: Se a conexão falhar ou o modo offline estiver ativo, os payloads são enfileirados em `pendingSyncQueue` e armazenados no `localStorage`, sendo descarregados automaticamente ao reconectar.
   - Inspector de Transmissão (`Auto-Sync Data Stream Ledger`): Gaveta colapsável no rodapé exibindo a transmissão contínua dos payloads para auditoria dev.

3. **Motor White-Label (5 Presets CSS)**:
   - Alternância dinâmica entre 5 temas CSS: `Obsidian Night` (dark mode Zap Web default), `Emerald Garden`, `Ocean Breeze`, `Sakura Bloom` e `Amber Warmth`, notificando o evento `THEME_PRESET_CHANGED` à API central.

4. **Dev Simulation Toolbar**:
   - Barra superior de simulação permitindo disparar cenários em tempo real (Objeção de Preço, Dúvida RAG, Fechamento, Mensagem de Áudio Whisper, Objeção LGPD/TI e alternador de simulação offline).

## Consequências

- **Positivas**:
  - Operadores SDR ganham uma interface ultrarrápida e limpa, focada exclusivamente na conversão de leads.
  - Sincronização perfeita de dados com o Core OS: histórico completo, score DHS e feedback de RAG são preservados sem intervenção manual.
  - Permite testes ponta a ponta e prototipagem rápida de fluxos de IA antes do deploy em larga escala.
- **Negativas**:
  - Necessidade de manter o contrato de payload do `AutoSyncEvent` alinhado entre o standalone app e a API central.

---

*"Atendimento rápido ao vivo com sincronia total e inteligência centralizada."*
