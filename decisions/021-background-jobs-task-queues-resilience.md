# ADR-021: Processamento de Jobs Assíncronos, Filas de Tarefas e Resiliência (Taskiq / SAQ)

* **Status**: Aprovado
* **Data**: Agosto 2026
* **Autores**: Equipe de Arquitetura e Engenharia Backend (Revenue SDR OS)

---

## 1. Contexto e Problema

O **Revenue SDR OS** necessita processar diversas tarefas assíncronas em segundo plano:
1. **Ingestão de Webhooks**: Webhooks inbound do WhatsApp (Z-API), Instagram DM e E-mail precisam responder com `HTTP 200 OK` / `202 Accepted` em menos de 50ms para evitar retransmissões e timeouts do provedor.
2. **Execução do Agente SDR de IA**: Roteamento de LLM, recuperação RAG, chamada de ferramentas (*tool calling*) e geração de resposta levam de 500ms a 2000ms.
3. **Extração Assíncrona de Memória e Scoring**: Processamento em segundo plano do *Memory Brain* e *Opportunity Brain* sem travar a resposta principal do usuário.
4. **Réguas de Cadência e Reengajamento**: Notificações programadas (ex: disparar follow-up 2 horas após inatividade do lead).
5. **Transcrições de Áudio**: Envio de notas de voz para a API do Whisper / Groq e retorno do texto formatado.

Sem uma arquitetura de fila e mensageria resiliente, o backend FastAPI estaria sujeito a estouro de memória (OOM), bloqueio do event loop assíncrono e perda de mensagens em caso de restarts da aplicação ou VPS.

---

## 2. Decisão Arquitetural

Adotar a arquitetura de tarefas assíncronas baseada no **Taskiq** (ou **SAQ** como engine alternativa leve), configurado para operarem com dois modos de transporte (*Brokers*):

1. **Modo Cloud / Production com Redis/Valkey (`Taskiq-Redis`)**:
   - Utiliza Redis/Valkey pub/sub e data structures para agendamento, retentativas e concorrência distribuída.
   - Ideal para ambientes multi-worker ou VPSs escaláveis.

2. **Modo Standalone / VPS Local Single-Tenant (`Taskiq-AioSQLite` ou SQLite Broker)**:
   - Permite que o Taskiq grave a fila de tarefas diretamente no arquivo de banco de dados SQLite/libSQL embarcado local ou em memória, mantendo a garantia de **Custo R$ 0,00** e **Auto-Contenção** da VPS sem exigir um serviço Redis rodando se o tenant optar por deploy ultra-enxuto.

### Componentes Chave da Arquitetura:

```
FastAPI Webhook / Endpoint
        |
        v (202 Accepted / < 50ms)
+-------------------------------------------------------------+
| Taskiq Broker (Redis ou SQLite embarcado)                   |
|  - Task Queue: high_priority (webhooks, live messages)      |
|  - Task Queue: default (AI execution, tools, memory extract)|
|  - Task Queue: low_priority (batch analytics, ETL, reports) |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| Taskiq Worker Process (background execution)                 |
|  - Worker idempotente via `job_key` (dedup)                 |
|  - Retry com Exponential Backoff + Jitter                   |
|  - Dead Letter Queue (DLQ) para mensagens com falha         |
|  - Limite de tempo de execução (Timeout: 30s)               |
+-------------------------------------------------------------+
```

---

## 3. Diretrizes de Implementação e Guardrails para Agentes de IA

### A. Idempotência Obrigatória via `job_key`
Todo job assíncrono deve ser projetado para ser idempotente. Em caso de re-tentativa por timeout de rede ou reinicialização do worker, o job não pode gerar duplicidade de mensagens ou ações:

```python
# Exemplo de assinatura de job assíncrono no Taskiq
@taskiq_broker.task(
    retry_on_error=True,
    max_retries=3,
    delay=2,  # Segundos iniciais
)
async def process_incoming_whatsapp_message_task(
    organization_id: str,
    lead_id: str,
    message_id: str,
    payload: dict,
) -> None:
    # Setar ContextVar de tenancy no worker assíncrono
    set_current_organization(organization_id)
    
    # Validação de Idempotência
    job_key = f"job:wa:{organization_id}:{message_id}"
    if await cache_provider.exists(job_key):
        logger.info("Job já processado, ignorando duplicata", job_key=job_key)
        return
        
    await cache_provider.set(job_key, "processing", ttl=300)
    
    # Execução do serviço de domínio
    await conversation_service.handle_inbound_message(lead_id, payload)
```

### B. Gestão de Filas por Prioridade
- `queue_urgent`: Webhooks e envio imediato de mensagens no Zap (Worker de resposta instantânea).
- `queue_default`: Execução do agente de IA, chamadas de ferramentas RAG, agendamentos do Google Calendar.
- `queue_background`: Análise de sentimento pós-conversa, extração de memórias frias, sincronia DW/Cold Storage.

### C. Retentativas e Dead Letter Queue (DLQ)
- **Estratégia de Backoff**: Exponencial com Jitter ($2^n + \text{rand}(0, 1)$ segundos) até no máximo 3 tentativas para erros transientes de LLM ou API externa (Z-API).
- **Dead Letter Queue (DLQ)**: Jobs que falharem após todas as retentativas são movidos para a tabela `failed_jobs` no banco de dados com a causa e a stack trace para auditoria no Manager Brain.

---

## 4. Consequências e SLAs

* **Positivas**:
  - Respostas instantâneas em webhooks (`< 50ms`), eliminando perda de mensagens ou bloqueios de HTTP client.
  - Total desacoplamento entre a recepção de mensagens e o tempo de raciocínio de LLMs.
  - Funcionamento em modo standalone (com SQLite/libSQL broker) ou escalável (com Redis/Valkey).
* **Negativas / Riscos**:
  - Requer a execução de um processo worker adicional (`taskiq worker app.tasks.broker:broker`) supervisionado por `systemd` na VPS.

---

## 5. Invariantes para Agentes de Codificação (AI Coding Guardrails)

1. **NUNCA** executar chamadas de LLM ou chamadas HTTP para APIs externas (Z-API, Whisper, Google API) diretamente na thread síncrona do request FastAPI.
2. **SEMPRE** propagar a ContextVar `current_organization` explicitamente na entrada de qualquer função de tarefa assíncrona.
3. **SEMPRE** definir um `timeout` estrito para jobs (default: 30 segundos) evitando workers pendurados infinitamente.
