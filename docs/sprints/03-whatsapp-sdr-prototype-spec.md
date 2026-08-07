# Especificação Técnica: Prototótipo Zap SDR OS (`01_SDR_Prototipo`)

```
+----------------------------------------------------------------------+
|                                                                      |
|   ESPECIFICAÇÃO TÉCNICA — PROTOTIPO ZAP SDR OS                  |
|   Sub-produto / Micro-App de Atendimento Isolado com Sync SDR OS     |
|   Status:  APROVADO E DOCUMENTADO                                    |
|   Stack:   HTML5 + TailwindCSS + DaisyUI + Alpine.js + Chart.js      |
|   Repo:    ~/AGENCIA/SDR/ (00_SDR_architecture)                       |
|   Alvo:    Sub-módulo / App standalone `01_SDR_Prototipo`             |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## 1. Visão Geral e Arquitetura Standalone (Execução Isolada)

O **01_SDR_Prototipo** é concebido como uma **interface de atendimento leve, focada e independente** (Micro-App / Standalone Copilot). Ele foi desenhado para permitir que vendedores, SDRs e clientes/leads interajam **exclusivamente através da interface no estilo Zap Web**, sem necessitarem navegar pelos painéis e dashboards complexos do sistema central **Revenue SDR OS** (`00_SDR_architecture`).

### 1.1 Modos de Operação
1. **Modo Standalone (Isolado)**: O aplicativo roda de forma autônoma (uma SPA estática/server-driven leve) acessível por vendedores via link direto ou subdomínio dedicado (ex: `chat.clinica-bela.com`).
2. **Sincronização Automática em Background**: Mesmo rodando isoladamente, **100% dos dados capturados na conversa** (mensagens, score de sentimento DHS, objeções detectadas, transcrições de áudio e sugestões de IA utilizadas) são **automaticamente transmitidos em segundo plano** para a API central do **Revenue SDR OS**.

---

## 2. Arquitetura de Comunicação e Autenticação do Micro-App

```
+---------------------------------------------------+         +---------------------------------------------------+
|     SUB-PRODUTO ISOLADO (01_SDR_Prototipo)       |         |        SISTEMA PRINCIPAL (Revenue SDR OS)         |
|                                                   |         |             (00_SDR_architecture)                 |
| +-----------------------------------------------+ |         |                                                   |
| | Interface Zap Web Simplificada          | |         | +-----------------------------------------------+ |
| | - Vendedor & Lead negociam aqui              | |         | | Database Central & Multi-Tenant Engine        | |
| | - Gráfico DHS + Sugestões de Resposta IA     | |         | | - Pipeline de Vendas & CRM                    | |
| +-----------------------------------------------+ |         | | - Memory Brain (Base de Conhecimento RAG)     | |
|                         |                         |         | | - Analytics & Dashboard de Gestão             | |
|                         | (Events Dispatcher)     |         | +-----------------------------------------------+ |
|                         v                         |         |                         ^                         |
|   [Background Auto-Sync: Tenant API Key Auth] ----+-------->| (REST / SSE Webhook API: POST /api/v1/copilot)    |
+---------------------------------------------------+         +---------------------------------------------------+
```

### 2.1 Configuração de Tenant via API Key / Token
- Ao abrir o app isolado, ele obtém o identificador da organização via parâmetro de URL (`?tenant=clinica-bela`) ou via `TENANT_API_KEY` armazenada no `localStorage`.
- Todas as requisições de sugestões de IA (RAG) e despachos de eventos de histórico utilizam o header `X-Tenant-Key: <key>`.

---

## 3. Layout da Interface e Arquitetura Visual (3 Colunas)

A interface é mantida em um **Grid de 3 Colunas Principais**, totalmente responsivo e compatível com as 5 paletas do sistema White-Label:

```
+--------------------------------------------------------------------------------------------------------+
| HEADER STANDALONE: [Logo White-Label] [Seletor de Tema] [🟢 Auto-Sync Ativo: Core SDR OS]              |
+-------------------+------------------------------------+-----------------------------------------------+
| COLUNA 1 (300px)  | COLUNA 2 (Flex / Central)          | COLUNA 3 (400px - Painéis Extras IA)          |
|                   |                                    |                                               |
| [Busca & Filtros] | [Header do Lead: Status + Modos]   | [ PAINEL EXTRA 1: GRÁFICO DHS DE NEGOCIAÇÃO ] |
| [Lista de Chats]  |                                    | - Monitoramento Minuto a Minuto               |
|  - Lead 1 (Novo)  | [Área de Mensagens / Chat Stream]  | - Tendência Positiva / Negativa               |
|  - Lead 2 (DHS+)  |  - Balão Lead (Objeção)            | - Auto-Push de Score para o CRM Central       |
|  - Lead 3 (DHS-)  |  - Balão SDR (Resposta IA)         |-----------------------------------------------|
|                   |  - Badge: [Auto-Synced to OS]      | [ PAINEL EXTRA 2: SUGESTÕES DE RESPOSTA IA ]  |
|                   |                                    | - Alimentado pela Base RAG Central            |
|                   | [Campo de Input + Botão Enviar]    | - Cards com Score de Confiança + Botão Usar   |
|                   |  - [Botão Copiar Resposta IA]      |-----------------------------------------------|
|                   |  - [Alternador Modos: IA/Humano]   | [ INSPECTOR: CORE AUTO-SYNC DATA STREAM ]     |
+-------------------+------------------------------------+-----------------------------------------------+
```

---

## 4. Especificação dos 2 Painéis Extras de Inteligência

### 4.1 Painel Extra 1: Gráfico de Sentimento / Saúde da Negociação (DHS)
- Renderizado via **Chart.js** monitorando minuto a minuto a conversa.
- **Auto-Sync de Saúde da Negociação**: Cada alteração no DHS recalcula a saúde da oportunidade e envia automaticamente em background para o CRM do Revenue SDR OS, atualizando o valor e o estágio do pipeline de vendas sem intervenção manual.

### 4.2 Painel Extra 2: Sugestões de Respostas Inteligentes (AI Sales Assistant)
- As sugestões de resposta exibidas no app isolado são consultadas em tempo real na Base RAG Central do `00_SDR_architecture`.
- Permite que o vendedor isolado tenha acesso ao conhecimento completo da empresa (preços, garantias, scripts de venda).

---

## 5. Sincronização Automática em Background & Fallback Resiliente

1. **Dispatcher de Eventos em Background**:
   - A cada mensagem trocada ou evento de sentimento, o Alpine.js engrena o dispatch de um evento JSON assíncrono.
2. **Fila Local Resiliente (`Offline Queue`)**:
   - Caso a conexão com o servidor central seja interrompida, as mensagens e métricas coletadas são salvas no `localStorage`.
   - Assim que a conexão for restabelecida, o app processa o flush automático dos dados para o `00_SDR_architecture`.
3. **Inspector de Sincronização (Auto-Sync Log)**:
   - Mantém uma gaveta colapsável no rodapé exibindo a taxa de sincronização (`100% Synced - 0 PENDENTES`) e o último payload transmitido.

---

## 6. Suporte ao Sistema White-Label (5 Temas CSS)

1. **Sakura Bloom** (`theme-sakura`)
2. **Emerald Garden** (`theme-emerald`)
3. **Ocean Breeze** (`theme-ocean`)
4. **Obsidian Night** (`theme-obsidian`)
5. **Amber Warmth** (`theme-amber`)

---

## 7. Critérios de Aceite para Desenvolvimento Standalone

```
[ ] Interface opera 100% isolada sem exigir telas de gestão/dashboard do SDR principal.
[ ] Configuração do identificador de Tenant (API Key / Tenant Slug) funcional no app.
[ ] Todos os dados coletados (chat, sentimento, notas) são enviados automaticamente em background para o Core OS.
[ ] Fila offline para retenção de eventos no localStorage caso a conexão caia.
[ ] Gráfico Chart.js reativo atualizando o DHS minuto a minuto e sincronizando o score com o pipeline central.
[ ] Painel de Sugestões de IA alimentado pela base RAG do sistema principal.
[ ] Inspector de Auto-Sync demonstrando o tráfego de dados isolado -> central.
```
