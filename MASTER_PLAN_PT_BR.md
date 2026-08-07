# MASTER PLAN — Revenue SDR OS & Arquitetura Conversacional de IA

> **Plano Mestre Técnico de Engenharia para Desenvolvimento da Solução End-to-End**  
> **Elaborado por**: Equipe de Engenharia (Arquitetos de Software, Engenheiros de IA, Desenvolvedores Backend/Frontend e DevOps/SRE)  
> **Versão**: 2.0.0 (Baseline pós-v0.2.0 — Software Engineering Execution Plan)  
> **Data**: Agosto de 2026  

---

## 1. Visão Geral e Estratégia Técnico-Operacional da Solução

O **Revenue SDR OS** é um **Sistema Operacional de Vendas Conversacional Autônomo** projetado sob uma mudança fundamental de paradigma: **a entidade raiz da automação comercial não é o cadastro estático do Lead nem um disparo de mensagens em massa, mas sim o Relacionamento (Conversa)** em evolução contínua através dos canais.

### Promessa e Valor Central
> *"Nunca mais perca um lead por falta de acompanhamento. O cliente compra agenda cheia."*

### Pilares Arquiteturais Principais
1. **Memória Persistente do Relacionamento**: Atributos extraídos no longo prazo (orçamento, tomadores de decisão, objeções, cronograma) armazenados por lead e fornecidos dinamicamente aos Agentes de IA.
2. **Ecossistema Multi-Agente de IA**: Agentes autônomos especializados atuando como SDRs seniores, extratores de memória em background, qualificadores de oportunidade, agendadores de cadência e coaches de vendas pós-conversa.
3. **Engine Omnichannel**: Continuidade fluida de conversa entre WhatsApp (Z-API), Instagram DM, E-mail e Voz.
4. **Arquitetura On-Premise-as-a-Service**: VPSs dedicadas single-tenant por organização, gerenciadas centralmente pelo **MyraOS Platform Console**, garantindo conformidade LGPD, zero compartilhamento de dados entre empresas e resiliência de execução local.
5. **Stack Auto-Contida**: Backend FastAPI + SQLModel sobre banco embarcado Turso (libSQL) + Frontend hypermedia Jinja2/HTMX/Alpine.js (vendored) + streaming em tempo real SSE.

---

## 2. Estrutura da Equipe de Engenharia e Processo de Desenvolvimento

A execução desta solução exige uma equipe de engenharia multidisciplinar operando sob um processo de desenvolvimento padronizado e rigoroso.

### 2.1 Papéis e Responsabilidades Técnicas

| Papel | Responsabilidades Principais |
|---|---|
| **Arquiteto Principal de Software** | Topologia do sistema, invariantes de multi-tenancy, evolução de schema, orquestração de VPS, arquitetura On-Premise-as-a-Service. |
| **Engenheiro Líder de Sistemas de IA** | Arquitetura do sistema multi-agente, engenharia de prompt, pipelines RAG, schemas de tool calling, roteamento de fallback de LLMs, compressão de contexto. |
| **Engenheiro Sênior de Backend e Dados** | Serviços de domínio FastAPI, integração com Turso/libSQL, arquitetura de eventos append-only, jobs em background (ARQ/APScheduler), broker SSE. |
| **Engenheiro Sênior de Frontend e UX** | Implementação hypermedia com Jinja2 + HTMX + Alpine.js, sistema de tradução de presets de cores white-label, integração copilot do ZAP Prototype. |
| **Especialista em Telemetria e FinOps Técnico** | Contabilidade de tokens por tenant, instrumentação Prometheus, otimização de janelas de contexto, estratégias de prompt caching e roteamento multi-tier de LLMs. |
| **Engenheiro de QA, Segurança e Infraestrutura** | Suíte de testes isolados cross-tenant com Pytest, linting ruff, validação de migrations Alembic, segurança do Update Agent via systemd. |

### 2.2 Workflow Oficial do Desenvolvedor

Para garantir consistência e evitar regressões, todo membro da equipe de engenharia deve seguir o workflow em camadas:

```
+-----------------------------------------------------------------------------------+
| 1. Leitura de Especificações & ADRs (FOUNDATION.md, ARCHITECTURE.md, Sprint Spec) |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. Alterações de Banco & Migration (SQLModel -> alembic revision --autogenerate)   |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 3. Implementação da Camada de Domínio (app/*/service.py com filtro organization_id)|
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 4. Schemas & Validação de Entrada (Pydantic schemas com validação estrita)         |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 5. Camada de Apresentação & API (FastAPI rotas finas / Jinja2 + HTMX pages)       |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 6. Matriz de Qualidade & Verificação (pytest 100% verde + cross-tenant + ruff)   |
+-----------------------------------------------------------------------------------+
```

---

## 3. Roadmap Técnico de Execução e Detalhamento das Sprints

O plano de desenvolvimento é estruturado em **10 Sprints de execução**, divididas em três fases estratégicas.

```
Sprint 00 [CONCLUÍDA] Arquitetura e Gestão
Sprint 01 [CONCLUÍDA] Foundation + Auth + White-Label (Baseline v0.2.0)
Sprint 01.5 [CONCLUÍDA] Prototype Standalone ZAP Copilot (02_ZAP_Prototype)
Sprint 02 [W1-W2] Lead Brain + Memory Brain
Sprint 03 [W3-W4] Conversations + Opportunity Brain + Cadence Engine
Sprint 04 [W5-W7] AI Sales Brain + Integração Z-API WhatsApp
Sprint 05 [W8-W9] Handoff Humano-IA + Integração Google Calendar + Observabilidade
Sprint 06 [W10-W11] Transcrição Whisper de Áudio + Gráfico DHS + Stream SSE Real-Time
Sprint 07 [W12-W14] Análise Pós-Conversa + Data Warehouse ETL/CDC + Dashboards Analíticos
Sprint 08 [W15-W17] Engine Omnichannel (Instagram DM, E-mail, Agente de Voz)
Sprint 09 [W18-W19] Automação de VPS Dedicada + Orquestrador de Updates MyraOS
Sprint 10 [W20-W22] Playbooks Verticais + Marketplace de Agentes Tribo
```

### Detalhamento Técnico por Fase e Entregáveis

#### Fase 1: Inteligência Core e Fundação da Engine (Sprints 02 - 04)
* **Sprint 02: Lead Brain & Memory Brain**
  * Unificação de identidades cross-channel em `leads` e `lead_identities`.
  * Tabela estruturada de `memories` de longo prazo com scores de confiança e categorias.
  * Timeline de eventos append-only (`lead_timeline_events`).
  * *Critério de Aceite*: Testes de isolamento cross-tenant 100% aprovados e endpoints CRUD funcionais.
* **Sprint 03: Conversations, Scoring de Oportunidade e Cadence Engine**
  * Agregado raiz `conversations` com histórico de `messages`.
  * Sistema de scoring por eventos (`Opportunity Brain`) calculando temperatura (Quente/Morno/Frio).
  * Fila leve de background jobs (ARQ/APScheduler) para gatilhos de régua de relacionamento.
  * *Critério de Aceite*: Transição autônoma de estágios do funil por scoring de eventos e agendador idempotente.
* **Sprint 04: AI Sales Brain & Engine Z-API WhatsApp**
  * Abstração `ZapProvider` para webhooks inbound e envios outbound da Z-API.
  * Agente conversacional AI Sales Brain com tool calling (`schedule_meeting`, `add_memory`, `update_stage`).
  * Toggle `ai_mode` com sincronização em tempo real para interface copilot do `02_ZAP_Prototype`.
  * *Critério de Aceite*: Execução de ciclo conversacional end-to-end com suporte a chamadas de ferramentas.

#### Fase 2: Operações em Tempo Real, Handoff e Analytics (Sprints 05 - 07)
* **Sprint 05: Handoff Humano-IA e Sincronização de Calendário**
  * Transferência sem fricção entre agente IA e operador humano com resumo de contexto.
  * Integração bidirecional com Google Calendar via chamada de ferramenta da IA.
  * Endpoints de métricas Prometheus e logs JSON estruturados via `structlog`.
  * *Critério de Aceite*: Preservação total de histórico no handoff e exportação limpa de métricas.
* **Sprint 06: Processamento de Áudio e Streaming SSE em Tempo Real**
  * Transcrição de mensagens de áudio inbound via OpenAI Whisper / Groq API.
  * Broker Server-Sent Events (SSE) para atualização live da UI sem WebSockets.
  * Gráfico de saúde da conversa DHS (Dynamic Health Score) em tempo real.
  * *Critério de Aceite*: Streaming unidirecional estável e transcrição com latência controlada.
* **Sprint 07: Análise Pós-Conversa, Data Warehouse e Dashboards**
  * Agente coach de vendas pós-conversa (identificando padrões de objeção e oportunidades perdidas).
  * Pipeline ETL/CDC para arquivamento e exportação dos dados locais do Turso para Data Warehouse externo (PostgreSQL/Supabase com `pgvector`).
  * Dashboards analíticos do Manager Brain (conversão de funil, CAC, ROI, canais campeões).
  * *Critério de Aceite*: Expurgo seguro de dados frios mantendo acesso unificado via DW.

#### Fase 3: Expansão Omnichannel, Infraestrutura e Marketplace (Sprints 08 - 10)
* **Sprint 08: Engine Omnichannel**
  * Conectores nativos para Instagram DMs, E-mail e chamadas de Voz com IA.
  * Gerenciador de continuidade entre canais permitindo que a conversa migre de plataforma sem perder contexto.
  * *Critério de Aceite*: Continuidade de diálogo identificando o lead em múltiplos canais.
* **Sprint 09: VPS Dedicada e Orquestração de Updates**
  * Console Central MyraOS para provisionamento e monitoramento de VPSs dos clientes.
  * Agent de Update automático via `systemd` fazendo pull de releases a cada 6h com rollback automático.
  * *Critério de Aceite*: Deploy automatizado com recuperação autônoma diante de falhas de healthcheck.
* **Sprint 10: Playbooks Verticais e Marketplace de Agentes**
  * Playbooks verticais pré-configurados (Saúde/Clínicas, Imobiliário, Automotivo, Serviços Financeiros).
  * Framework de Marketplace para distribuição de personas e fluxos customizados.
  * *Critério de Aceite*: Instalação de novos playbooks com substituição dinâmica de prompts e memórias.

---

## 4. Arquitetura do Sistema Multi-Agente de IA

O sistema opera como um **ecossistema orquestrado de 6 Agentes de IA especializados**, garantindo modularidade, separação clara de responsabilidades e controle refinado de contexto e execução:

```
                          +-----------------------------------+
                          |    Mensagem / Evento de Entrada   |
                          +-----------------+-----------------+
                                            |
                                            v
+-----------------------------------------------------------------------------------+
|                              1. Agente AI Sales SDR                               |
|  - Conduz conversa ativa com Lead via WhatsApp / Instagram / E-mail / Voz         |
|  - Acessa Base RAG, Persona do System Prompt e Memórias do Lead                   |
|  - Invoca Ferramentas: schedule_meeting(), update_stage(), add_lead_memory()     |
+-------------------+-------------------------------------------+-------------------+
                    |                                           |
                    v (Background Assíncrono)                   v (Background Assíncrono)
+---------------------------------------+   +---------------------------------------+
|      2. Agente Extrator de Memória     |   | 3. Classificador de Scoring e Intenção |
| - Analisa diálogo para extrair fatos, |   | - Avalia intenção e sentimento do lead|
|   orçamento, objeções e preferências  |   | - Atualiza score DHS e temperatura    |
| - Salva registros estruturados no DB  |   | - Dispara alerta prioritário se Quente|
+---------------------------------------+   +---------------------------------------+
                    |                                           |
                    +-------------------+-----------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                    4. Agente de Cadência e Reengajamento                          |
| - Disparado pelo ARQ Scheduler em inatividade de leads ou regras de régua         |
| - Gera mensagem contextual de follow-up usando memórias passadas                  |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                     5. Agente de Processamento de Voz e Áudio                     |
| - Transcreve mensagens de áudio inbound/outbound via Whisper API                  |
| - Formata texto para processamento downstream pelo AI Sales SDR                   |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                     6. Coach de Vendas e Analista Pós-Conversa                    |
| - Roda ao encerrar conversa/chamada para avaliar desempenho do SDR                |
| - Alimenta insights analíticos para os Brains Manager e Revenue                   |
+-----------------------------------------------------------------------------------+
```

### Especificação dos Agentes e Recursos Técnicos

| Nome do Agente | Função Principal | Gatilho de Execução | Tier de Modelo / Capacidade | Recursos Chave |
|---|---|---|---|---|
| **1. Agente AI Sales SDR** | Atendimento direto, qualificação e agendamento | Mensagem Inbound do Lead | Tier Raciocínio Avançado | Tool Calling, Busca vetorial RAG, Adaptação de Persona, Modo Copilot. |
| **2. Extrator de Memória** | Extração de memória de longo prazo | Lote assíncrono pós-mensagem | Tier Rápido / JSON Estruturado | Saída JSON estruturada estrita, validação Pydantic. |
| **3. Classificador de Intenção** | Scoring de intenção e definição de temperatura | Pós-turno assíncrono | Tier Rápido / Classificação | Classificação rápida, análise de sentimento, ajuste de DHS. |
| **4. Agente de Cadência** | Reativação de leads frios ou dormentes | Timer agendado no ARQ | Tier Intermediário | Reentrada contextual, tom anti-spam, integração de memória. |
| **5. Processador de Voz** | Transcrição e diarização de áudio | Áudio inbound recebido | Modelo de Transcrição Dedicado | Alta precisão em PT-BR, formatação texto-áudio. |
| **6. Coach de Vendas** | Auditoria de performance e análise de perdas | Fim da conversa / Mudança de estágio | Tier Raciocínio Profundo | Raciocínio analítico, scoring de técnicas de vendas, relatórios. |

---

## 5. Arquitetura de Telemetria, Otimização de Contexto e FinOps Técnico

Em substituição a estimativas comerciais voláteis, o controle de consumo da infraestrutura de IA é gerido via **engenharia de contexto, instrumentação de telemetria e padrões de roteamento técnico**.

### 5.1 Instrumentação de Telemetria de Tokens

Para garantir observabilidade total do consumo de LLMs por tenant:

1. **Middleware de Rastreamento de Tokens**: Todas as chamadas para provedores de LLM são envelopadas por um decorator de telemetria que registra `input_tokens`, `output_tokens` e `cached_tokens`.
2. **Isolamento de Métricas por Organização**: Toda métrica de consumo é etiquetada com o `organization_id` da ContextVar e exportada via Prometheus.
3. **Budget Capping Operacional**: Limites de segurança por tenant configuráveis no banco para prevenir loops ou consumo descontrolado.

### 5.2 Estratégias de Gestão e Compressão de Contexto

Para manter a latência baixa e a estabilidade das chamadas de IA:

* **Janela Deslizante (Sliding Window)**: O histórico de chat enviado ao modelo é limitado às últimas $N$ mensagens relevantes, evitando o crescimento exponencial da janela.
* **Injeção de Memória Resumida**: Em vez de passar transcrições completas do passado, o sistema injeta os atributos de longo prazo extraídos pelo *Memory Brain*.
* **Capping de RAG Top-K**: O número de chunks recuperados da base vetorial é estritamente limitado por orçamento de tokens por turno.

### 5.3 Padrão Abstrato de Roteamento de Modelos (Multi-Tier LLM Router)

O sistema utiliza a abstração `LLMProviderInterface` permitindo alterar ou alternar modelos sem alterar o código de domínio:

```python
class LLMProviderInterface(Protocol):
    async def generate_response(
        self,
        prompt: str,
        system_prompt: str,
        tools: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse: ...
```

* **Tier Rápido / Leve**: Utilizado para extração de dados estruturados, classificação de intenção e tarefas de segundo plano.
* **Tier de Raciocínio Avançado**: Reservado para o diálogo ativo com o cliente, resolução de objeções complexas e coaching pós-venda.

### 5.4 Mecanismos Tecnológicos de Eficiência

1. **System Prompt Caching**: Utilização de cabeçalhos de cache nativos dos provedores para reaproveitar os prompts de sistema e bases de conhecimento RAG estáticas entre turnos.
2. **Processamento Assíncrono em Lote**: Tarefas de extração de memória e análise de intenção são desacopladas do fluxo principal de resposta ao usuário via filas de background.
3. **Truncamento Dinâmico de Ferramentas**: Envio apenas dos schemas de ferramentas estritamente necessários para a fase atual do diálogo.

---

## 6. Invariantes Técnicos e Governança

Todos os desenvolvedores e agentes de IA devem seguir rigorosamente os seguintes invariantes estabelecidos desde a v0.2.0:

1. **Padrão App Factory**: Sem singletons globais de módulo. O estado vive estritamente em `app.state`.
2. **Camadas Estritas**: Rota FastAPI -> `service.py` de domínio -> Tabelas SQLModel. Queries SQL NUNCA vivem nas rotas da API.
3. **Defesa em Profundidade Multi-Tenant**: Toda query DEVE filtrar por `organization_id`. Tentativas cross-tenant retornam `404 Not Found` genérico. O `organization_id` vem estritamente do contexto `ContextVar`, NUNCA do payload enviado pelo usuário.
4. **Envelope de Erros Unificado**: Erros lançam subclasses de `AppError` resultando no envelope JSON padrão `{"error": {"code": ..., "message": ..., "details": ...}}`.
5. **Versionamento Rígido com Alembic**: Modelos de tabela refletem o banco. Alterações de schema exigem script de migration (`alembic revision --autogenerate`).
6. **Auto-Contenção On-Premise**: Zero dependência de CDNs ou assets externos. Todos os assets estão embarcados localmente.
7. **Tempo Real via SSE**: Utilizar Server-Sent Events para atualizações unidirecionais do servidor para o cliente.
8. **Data Tiering (Hot/Cold Storage)**: O banco local Turso (libSQL) mantém dados quentes do atendimento ativo; pipeline assíncrono ETL migra históricos consolidados para PostgreSQL/Supabase.

---

## 7. Matriz de Qualidade, Integração Contínua e Operações de Deploy

### 7.1 Checklist de Validação Obrigatória (Pré-Commit / Pré-Merge)

Antes de submeter qualquer Pull Request, o código deve passar 100% nos seguintes verificadores:

```bash
pytest                                            # Suíte completa de testes isolados
ruff check app/ tests/ scripts/ alembic/          # Análise estática de código e segurança
ruff format --check app/ tests/ scripts/          # Verificação de formatação de código
alembic upgrade head && alembic downgrade -1 && alembic upgrade head # Validação round-trip de migration
./start &                                         # Teste de inicialização e rotas de saúde
curl http://127.0.0.1:8000/api/v1/health/
```

### 7.2 Arquitetura de Deploy On-Premise-as-a-Service

O modelo de implantação em VPSs dedicadas é operado da seguinte forma:

1. **Instalação Auto-Contida**: Cada nó de cliente executa a aplicação Python com Turso local em arquivo `.db`.
2. **Update Agent via `systemd`**: Um serviço de segundo plano consulta o **MyraOS Platform Console** a cada 6 horas por novas versões de release.
3. **Estratégia de Rollback Autônomo**: Durante o processo de atualização, o agente executa a migration do Alembic e os testes de healthcheck (`/api/v1/health/`). Caso o endpoint responda com erro ou falhe na inicialização, o agent executa automaticamente o rollback para a versão anterior e notifica o console central.
4. **Probes de Liveness e Readiness**: Monitoramento contínuo da saúde dos processos de segundo plano e da integridade da conexão com a base de dados local.

---

## 8. Próximos Passos de Execução

- **Ação Imediata**: Continuar a implementação técnica da **Sprint 02 — Lead Brain + Memory Brain** no repositório `~/AGENCIA/SDR/`.
- **Validação Arquitetural**: Garantir a cobertura de testes de isolamento cross-tenant para as tabelas `leads`, `lead_identities` e `memories`.
- **Instrumentação de Métricas**: Adicionar contadores de telemetria de tokens no middleware do FastAPI para observabilidade de uso desde a Sprint 02.
