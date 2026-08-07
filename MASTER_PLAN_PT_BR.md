# MASTER PLAN — Revenue SDR OS & Arquitetura Conversacional de IA

> **Plano Mestre Executivo e Tecnico para Desenvolvimento da Solucao End-to-End**  
> **Elaborado por**: Taskforce de Engenharia (Arquitetos de Software, Engenheiros de IA, Desenvolvedores de Sistemas e Engenheiros FinOps)  
> **Versao**: 1.0.0 (Baseline pos-v0.2.0)  
> **Data**: Agosto de 2026  

---

## 1. Visao Geral e Estrategia da Solucao

O **Revenue SDR OS** e um **Sistema Operacional de Vendas Conversacional Autonomo** projetado sob uma mudanca fundamental de paradigma: **a entidade raiz da automacao comercial nao e o cadastro estatico do Lead nem um disparo de mensagens em massa, mas sim o Relacionamento (Conversa)** em evolucao continua atraves dos canais.

### Promessa e Valor Central
> *"Nunca mais perca um lead por falta de acompanhamento. O cliente compra agenda cheia."*

### Pilares Arquiteturais Principais
1. **Memoria Persistente do Relacionamento**: Atributos extraidos no longo prazo (orcamento, tomadores de decisao, objecoes, cronograma) armazenados por lead e fornecidos dinamicamente aos Agentes de IA.
2. **Ecosistema Multi-Agente de IA**: Agentes autonomos especializados atuando como SDRs seniores, extratores de memoria em background, qualificadores de oportunidade, agendadores de cadencia e coaches de vendas pos-conversa.
3. **Engine Omnichannel**: Continuidade fluida de conversa entre WhatsApp (Z-API), Instagram DM, E-mail e Voz.
4. **Arquitetura On-Premise-as-a-Service**: VPSs dedicadas single-tenant por organizacao, gerenciadas centralmente pelo **MyraOS Platform Console**, garantindo conformidade LGPD, zero compartilhamento de dados entre empresas e resiliencia de execucao local.
5. **Stack Auto-Contida**: Backend FastAPI + SQLModel sobre banco embarcado Turso (libSQL) + Frontend hypermedia Jinja2/HTMX/Alpine.js + streaming em tempo real SSE.

---

## 2. Estrutura da Equipe de Engenharia e Papeis

A execucao desta solucao exige uma equipe de engenharia multidisciplinar:

| Papel | Responsabilidades Principais |
|---|---|
| **Arquiteto Principal de Software** | Topologia do sistema, invariantes de multi-tenancy, evolucao de schema, orquestracao de VPS, arquitetura On-Premise-as-a-Service. |
| **Engenheiro Lider de Sistemas de IA** | Arquitetura do sistema multi-agente, engenharia de prompt, pipelines RAG, schemas de tool calling, roteamento de fallback de LLMs, compressao de contexto. |
| **Engenheiro Senior de Backend e Dados** | Servicos de dominio FastAPI, integracao com Turso/libSQL, arquitetura de eventos append-only, jobs em background (ARQ/APScheduler), broker SSE. |
| **Engenheiro Senior de Frontend e UX** | Implementacao hypermedia com Jinja2 + HTMX + Alpine.js, sistema de traducao de presets de cores white-label, integracao copilot do ZAP Prototype. |
| **Especialista em FinOps e Otimizacao de Custos** | Previsao de consumo de tokens, roteamento multi-tier de LLMs, estrategias de prompt caching, custos unitarios mensais por tenant. |
| **Engenheiro de QA, Seguranca e Infraestrutura** | Suite de testes isolados cross-tenant com Pytest, linting ruff, validacao de migrations Alembic, seguranca do Update Agent via systemd. |

---

## 3. Cronograma Detalhado e Estimativa de Prazos

O tempo total estimado de desenvolvimento e de **22 Semanas (~5,5 Meses)** divididos em **10 sprints de execucao**, considerando uma equipe dedicada.

```
Sprint 00 [CONCLUIDA] Arquitetura e Gestao
Sprint 01 [CONCLUIDA] Foundation + Auth + White-Label (Baseline v0.2.0)
Sprint 01.5 [CONCLUIDA] Prototype Standalone ZAP Copilot (02_ZAP_Prototype)
Sprint 02 [W1-W2] Lead Brain + Memory Brain
Sprint 03 [W3-W4] Conversations + Opportunity Brain + Cadence Engine
Sprint 04 [W5-W7] AI Sales Brain + Integracao Z-API WhatsApp
Sprint 05 [W8-W9] Handoff Humano-IA + Integracao Google Calendar + Observabilidade
Sprint 06 [W10-W11] Transcricao Whisper de Audio + Grafico DHS + Stream SSE Real-Time
Sprint 07 [W12-W14] Analise Pos-Conversa + Data Warehouse ETL/CDC + Dashboards Analiticos
Sprint 08 [W15-W17] Engine Omnichannel (Instagram DM, E-mail, Agente de Voz)
Sprint 09 [W18-W19] Automacao de VPS Dedicada + Orquestrador de Updates MyraOS
Sprint 10 [W20-W22] Playbooks Verticais + Marketplace de Agentes Tribo
```

### Detalhamento por Fase e Entregaveis

#### Fase 1: Inteligencia Core e Fundacao da Engine (Sprints 02 - 04) | Prazo: Semanas 1 - 7
* **Sprint 02: Lead Brain & Memory Brain (2 Semanas)**
  * Unificacao de identidades cross-channel em `leads` e `lead_identities`.
  * Tabela estruturada de `memories` de longo prazo com scores de confianca e categorias.
  * Timeline de eventos append-only (`events`).
* **Sprint 03: Conversations, Scoring de Oportunidade e Cadence Engine (2 Semanas)**
  * Agregado raiz `conversations` com historico de `messages`.
  * Sistema de scoring por eventos (`Opportunity Brain`) calculando temperatura (Quente/Morno/Frio).
  * Fila leve de background jobs (ARQ/APScheduler) para gatilhos de regua de relacionamento.
* **Sprint 04: AI Sales Brain & Engine Z-API WhatsApp (3 Semanas)**
  * Abstracao `ZapProvider` para webhooks inbound e envios outbound da Z-API.
  * Agente conversacional AI Sales Brain com tool calling (`schedule_meeting`, `add_memory`, `change_stage`).
  * Toggle `ai_mode` com sincronizacao em tempo real para interface copilot do `02_ZAP_Prototype`.

#### Fase 2: Operacoes em Tempo Real, Handoff e Analytics (Sprints 05 - 07) | Prazo: Semanas 8 - 14
* **Sprint 05: Handoff Humano-IA e Sincronizacao de Calendario (2 Semanas)**
  * Transferencia sem friccao entre agente IA e operador humano com resumo de contexto.
  * Integracao bidirecional com Google Calendar via chamada de ferramenta da IA.
  * Endpoints de metricas Prometheus e logs JSON estruturados.
* **Sprint 06: Processamento de Audio e Streaming SSE em Tempo Real (2 Semanas)**
  * Transcricao de mensagens de audio inbound via OpenAI Whisper / Groq API.
  * Broker Server-Sent Events (SSE) para atualizacao live da UI sem WebSockets.
  * Grafico de saude da conversa DHS (Dynamic Health Score) em tempo real.
* **Sprint 07: Analise Pos-Conversa, Data Warehouse e Dashboards (3 Semanas)**
  * Agente coach de vendas pos-conversa (identificando padroes de objecao e oportunidades perdidas).
  * Pipeline ETL/CDC para arquivamento e exportacao dos dados locais do Turso para Data Warehouse externo (PostgreSQL/Supabase).
  * Dashboards analiticos do Manager Brain (conversao de funil, CAC, ROI, canais campeoes).

#### Fase 3: Expansao Omnichannel, Infraestrutura e Marketplace (Sprints 08 - 10) | Prazo: Semanas 15 - 22
* **Sprint 08: Engine Omnichannel (3 Semanas)**
  * Conectores nativos para Instagram DMs, E-mail e chamadas de Voz com IA.
  * Gerenciador de continuidade entre canais permitindo que a conversa migre de plataforma sem perder contexto.
* **Sprint 09: VPS Dedicada e Orquestracao de Updates (2 Semanas)**
  * Console Central MyraOS para provisionamento e monitoramento de VPSs dos clientes.
  * Agent de Update automatico via `systemd` fazendo pull de releases a cada 6h com rollback automatico.
* **Sprint 10: Playbooks Verticais e Marketplace de Agentes (3 Semanas)**
  * Playbooks verticais pre-configurados (Saude/Clinicas, Imobiliario, Automotivo, Servicos Financeiros).
  * Framework de Marketplace para distribuicao de personas e fluxos customizados.

---

## 4. Arquitetura do Sistema Multi-Agente de IA

O sistema opera como um **ecosistema orquestrado de 6 Agentes de IA especializados**, garantindo modularidade, separacao clara de responsabilidades e otimizacao de custos e latencia:

```
                          +-----------------------------------+
                          |    Mensagem / Evento de Entrada   |
                          +-----------------+-----------------+
                                            |
                                            v
+-----------------------------------------------------------------------------------+
|                              1. Agente AI Sales SDR                               |
|  - Conduz conversa ativa com Lead via WhatsApp / Instagram / E-mail / Voz         |
|  - Acessa Base RAG, Persona do System Prompt e Memorias do Lead                   |
|  - Invoca Ferramentas: schedule_meeting(), update_stage(), add_lead_memory()     |
+-------------------+-------------------------------------------+-------------------+
                    |                                           |
                    v (Background Assincrono)                   v (Background Assincrono)
+---------------------------------------+   +---------------------------------------+
|      2. Agente Extrator de Memoria     |   | 3. Classificador de Scoring e Intencao |
| - Analisa dialogo para extrair fatos, |   | - Avalia intencao e sentimento do lead|
|   orcamento, objecoes e preferencias  |   | - Atualiza score DHS e temperatura    |
| - Salva registros estruturados no DB  |   | - Dispara alerta prioritario se Quente|
+---------------------------------------+   +---------------------------------------+
                    |                                           |
                    +-------------------+-----------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                    4. Agente de Cadencia e Reengajamento                          |
| - Disparado pelo ARQ Scheduler em inatividade de leads ou regras de regua         |
| - Gera mensagem contextual de follow-up usando memorias passadas                  |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                     5. Agente de Processamento de Voz e Audio                     |
| - Transcreve mensagens de audio inbound/outbound via Whisper API                  |
| - Formata texto para processamento downstream pelo AI Sales SDR                   |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                     6. Coach de Vendas e Analista Pos-Conversa                    |
| - Roda ao encerrar conversa/chamada para avaliar desempenho do SDR                |
| - Alimenta insights analiticos para os Brains Manager e Revenue                   |
+-----------------------------------------------------------------------------------+
```

### Especificacao dos Agentes e Estrategia de Modelos

| Nome do Agente | Funcao Principal | Gatilho de Execucao | Modelo de LLM Recomendado | Recursos Chave |
|---|---|---|---|---|
| **1. Agente AI Sales SDR** | Atendimento direto, qualificacao e agendamento | Mensagem Inbound do Lead | **Claude 3.5 Sonnet / GPT-4o** (Alto valor); **Gemini 1.5 Flash** (Padrao) | Tool Calling, Busca vetorial RAG, Adaptacao de Persona, Modo Copilot. |
| **2. Extrator de Memoria** | Extração de memoria de longo prazo | Lote assincrono pos-mensagem | **Gemini 1.5 Flash-Lite / GPT-4o-mini** | Saida JSON estruturada estrita, validacao Pydantic, baixo custo. |
| **3. Classificador de Intencao** | Scoring de intencao e definicao de temperatura | Pos-turno assincrono | **Gemini 1.5 Flash / Claude 3.5 Haiku** | Classificacao rapida, analise de sentimento, ajuste de DHS. |
| **4. Agente de Cadencia** | Reativacao de leads frios ou dormentes | Timer agendado no ARQ | **Claude 3.5 Haiku / Gemini 1.5 Flash** | Reentrada contextual, tom anti-spam, integracao de memoria. |
| **5. Processador de Voz** | Transcricao e diarizacao de audio | Audio inbound recebido | **Groq Whisper Large v3 / OpenAI Whisper** | Alta precisao em PT-BR, formatacao texto-audio. |
| **6. Coach de Vendas** | Auditoria de performance e analise de perdas | Fim da conversa / Mudanca de estagio | **Claude 3.5 Sonnet / Gemini 1.5 Pro** | Raciocinio profundo, scoring de tecnicas de vendas, relatorios. |

---

## 5. Estimativa de Tokens, Previsao e Modelo de Precos (FinOps)

Para garantir a viabilidade comercial e margens previsiveis, o consumo de tokens foi modelado por ciclo de vida de lead e projetado para diferentes perfis operacionais.

### 5.1 Consumo Base de Tokens por Ciclo de Vida do Lead

Considerando um ciclo medio de **12 turnos conversacionais** (pares inbound/outbound):

```
Detalhamento de Contexto por Turno (Agente AI Sales SDR):
- Persona do Sistema e Instrucoes Prompt: ~1.000 tokens
- Contexto de Memoria do Lead Extraido: ~500 tokens
- Contexto de Produto Relevante via RAG: ~500 tokens
- Historico de Chat (janela deslizante de 6 turnos): ~500 tokens
--------------------------------------------------------------
Entrada (Input) Media por turno:  2.500 Tokens
Saida (Output) Media por turno:   250 Tokens
```

| Tarefa do Agente | Frequencia por Lead | Tokens por Gatilho | Total de Tokens / Ciclo do Lead |
|---|---|---|---|
| **Agente AI Sales SDR** | 12 turnos | 2.500 Input / 250 Output | **30.000 Input / 3.000 Output** |
| **Extrator de Memoria** | 4 lotes (a cada 3 turnos) | 1.500 Input / 150 Output | **6.000 Input / 600 Output** |
| **Classificador de Intencao** | 3 avaliacoes | 1.000 Input / 50 Output | **3.000 Input / 150 Output** |
| **Agente de Cadencia** | 2 disparos de regua | 2.000 Input / 200 Output | **4.000 Input / 400 Output** |
| **Coach de Vendas / Analista** | 1 execucao pos-conversa | 4.000 Input / 400 Output | **4.000 Input / 400 Output** |
| **Processamento de Voz (Whisper)**| 2 audios por lead | 2 minutos de audio | **2,0 Minutos de Audio** |
| **TOTAL DO CICLO DO LEAD** | — | — | **47.000 Input / 4.550 Output + 2 min Audio** |

---

### 5.2 Tabela Benchmark de Precos dos Modelos (Por 1 Milhao de Tokens)

*Baseado nos precos oficiais de API em Agosto de 2026:*

| Provedor / Modelo | Preco Input / 1M Tokens | Preco Output / 1M Tokens | Preco Input Cache / 1M Tokens |
|---|---|---|---|
| **Google Gemini 1.5 Flash-Lite** | $0,0375 | $0,150 | $0,009 |
| **Google Gemini 1.5 Flash** | $0,075 | $0,300 | $0,018 |
| **Google Gemini 1.5 Pro** | $1,250 | $5,000 | $0,312 |
| **Anthropic Claude 3.5 Haiku** | $1,000 | $5,000 | $0,100 |
| **Anthropic Claude 3.5 Sonnet** | $3,000 | $15,000 | $0,300 |
| **OpenAI GPT-4o-mini** | $0,150 | $0,600 | $0,075 |
| **OpenAI GPT-4o** | $2,500 | $10,000 | $1,250 |
| **Whisper Audio API** | $0,006 / minuto | — | — |

---

### 5.3 Previsao de Custos Mensais por Porte de Empresa

Comparamos duas estrategias de implantacao:
- **Stack Hibrida Otimizada**: Roteamento multi-tier usando *Gemini 1.5 Flash / Flash-Lite* para extrações, classificacoes e dialogos padrao, reservando *Claude 3.5 Haiku / Sonnet* para negociacoes complexas.
- **Stack Premium**: Utilizando *Claude 3.5 Sonnet* e *GPT-4o* em todas as etapas.

#### Tier 1: Pequena Empresa / Clinica (500 Leads / Mes)
* Volume Mensal: 23,5 Milhoes de Tokens Input | 2,27 Milhoes de Tokens Output | 1.000 Minutos de Audio

| Metrica | Stack Hibrida Otimizada | Stack Premium |
|---|---|---|
| **Custo Agente AI Sales SDR** | $2,02 (Gemini 1.5 Flash) | $56,25 (Claude 3.5 Sonnet) |
| **Custo Extracao de Memoria** | $0,16 (Gemini 1.5 Flash-Lite) | $4,95 (GPT-4o-mini) |
| **Custo Scoring de Oportunidade** | $0,13 (Gemini 1.5 Flash) | $2,47 (Claude 3.5 Haiku) |
| **Custo Cadencia e Coaching** | $1,20 (Claude 3.5 Haiku) | $12,00 (Claude 3.5 Sonnet) |
| **Transcricao de Audio (Whisper)** | $6,00 | $6,00 |
| **ESTIMATIVA TOTAL MENSAL** | **~$9,51 / mes** | **~$81,67 / mes** |

#### Tier 2: Empresa Medio Porte (2.500 Leads / Mes)
* Volume Mensal: 117,5 Milhoes de Tokens Input | 11,37 Milhoes de Tokens Output | 5.000 Minutos de Audio

| Metrica | Stack Hibrida Otimizada | Stack Premium |
|---|---|---|
| **Custo Agente AI Sales SDR** | $10,10 (Gemini 1.5 Flash) | $281,25 (Claude 3.5 Sonnet) |
| **Custo Extracao de Memoria** | $0,80 (Gemini 1.5 Flash-Lite) | $24,75 (GPT-4o-mini) |
| **Custo Scoring de Oportunidade** | $0,65 (Gemini 1.5 Flash) | $12,35 (Claude 3.5 Haiku) |
| **Custo Cadencia e Coaching** | $6,00 (Claude 3.5 Haiku) | $60,00 (Claude 3.5 Sonnet) |
| **Transcricao de Audio (Whisper)** | $30,00 | $30,00 |
| **ESTIMATIVA TOTAL MENSAL** | **~$47,55 / mes** | **~$408,35 / mes** |

#### Tier 3: Enterprise / Grande Agencia (10.000 Leads / Mes)
* Volume Mensal: 470 Milhoes de Tokens Input | 45,5 Milhoes de Tokens Output | 20.000 Minutos de Audio

| Metrica | Stack Hibrida Otimizada | Stack Premium |
|---|---|---|
| **Custo Agente AI Sales SDR** | $40,40 (Gemini 1.5 Flash) | $1.125,00 (Claude 3.5 Sonnet) |
| **Custo Extracao de Memoria** | $3,20 (Gemini 1.5 Flash-Lite) | $99,00 (GPT-4o-mini) |
| **Custo Scoring de Oportunidade** | $2,60 (Gemini 1.5 Flash) | $49,40 (Claude 3.5 Haiku) |
| **Custo Cadencia e Coaching** | $24,00 (Claude 3.5 Haiku) | $240,00 (Claude 3.5 Sonnet) |
| **Transcricao de Audio (Whisper)** | $120,00 | $120,00 |
| **ESTIMATIVA TOTAL MENSAL** | **~$190,20 / mes** | **~$1.633,40 / mes** |

---

### 5.4 Otimizacoes FinOps (Boas Praticas)

1. **Prompt Caching**: Ativar cache de prompt Anthropic / Gemini para prompts de sistema e documentacao de produto. *Reduz custos de input em ate 75-90% em turnos repetitivos.*
2. **Extracao em Lote Assincrona**: Nao executar extracao de memoria a cada mensagem individual. Processar em lotes em segundo plano usando modelos ultrabaratos (*Gemini 1.5 Flash-Lite*).
3. **Compressao Dinamica de Contexto**: Truncar historico de chat usando janelas deslizantes e confiar nas memorias de longo prazo extraidas em vez de enviar transcricoes brutas completas.
4. **Escalonamento Inteligente de Modelos (Smart Router)**: Rotear perguntas padrao para modelos leves ($0,075/1M) e escalar para modelos premium ($3,00/1M) apenas quando a gravidade da objecao ou a temperatura do lead forem elevadas.

---

## 6. Invariantes Tecnicos e Governanca

Todos os desenvolvedores e agentes de IA devem seguir rigorosamente os seguintes invariantes estabelecidos desde a v0.2.0:

1. **Padrao App Factory**: Sem singletons globais de modulo. O estado vive estritamente em `app.state`.
2. **Camadas Estritas**: Rota FastAPI -> `service.py` de dominio -> Tabelas SQLModel. Queries SQL NUNCA vivem nas rotas da API.
3. **Defesa em Profundidade Multi-Tenant**: Toda query DEVE filtrar por `organization_id`. Tentativas cross-tenant retornam `404 Not Found` generico. O `organization_id` vem estritamente do contexto `ContextVar`, NUNCA do payload enviado pelo usuario.
4. **Envelope de Erros Unificado**: Erros lancam subclasses de `AppError` resultando no envelope JSON padrao `{"error": {"code": ..., "message": ..., "details": ...}}`.
5. **Versionamento Rigido com Alembic**: Modelos de tabela refletem o banco. Alteracoes de schema exigem script de migration (`alembic revision --autogenerate`).
6. **Auto-Contencao On-Premise**: Zero dependencia de CDNs ou assets externos. Todos os assets estao embarcados localmente.
7. **Tempo Real via SSE**: Utilizar Server-Sent Events para atualizacoes unidirecionais do servidor para o cliente.

---

## 7. Proximos Passos de Execucao

- **Acao Imediata**: Iniciar a implementacao da **Sprint 02 — Lead Brain + Memory Brain** em `~/AGENCIA/SDR/`.
- **Validacao Arquitetural**: Testar isolamento cross-tenant e scripts de migration Alembic antes do merge do Pull Request.
- **Monitoramento FinOps**: Implementar contador de tokens no middleware FastAPI para monitorar o gasto real de tokens por organizacao em tempo real.
