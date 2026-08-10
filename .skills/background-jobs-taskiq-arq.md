---
name: background-jobs-taskiq-arq
description: |
  Carregue esta skill sempre que for criar ou modificar tarefas em segundo plano,
  filas de execução (Taskiq / SAQ), retentativas idempotentes com job_key e
  agendamentos de régua de cadência.
version: 1.0.0
author: Hermes (arquiteto)
license: Proprietary
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
metadata:
  hermes:
    tags: [taskiq, saq, arq, background-jobs, idempotency, dlq, redis, sqlite]
---

# Skill: Processamento de Jobs Assíncronos e Filas de Tarefas (Taskiq)

## 1. Princípio Fundamental

Operações pesadas (processamento de LLM, chamada de APIs de terceiros, sincronização de calendários e transcrições de áudio) **NUNCA** devem rodar de forma síncrona dentro da requisição HTTP do FastAPI.
O FastAPI deve responder com `HTTP 202 Accepted` em $< 50\text{ ms}$ e enfileirar a tarefa no **Taskiq**.

---

## 2. Padrão de Definição de Tarefa Idempotente

```python
import structlog
from app.core.tasks import taskiq_broker
from app.tenancy.context import set_current_organization
from app.core.cache import cache_provider

logger = structlog.get_logger()

@taskiq_broker.task(
    retry_on_error=True,
    max_retries=3,
    delay=2,  # Delay inicial em segundos
)
async def process_inbound_message_task(
    organization_id: str,
    lead_id: str,
    message_id: str,
    payload: dict,
) -> None:
    # 1. Definir ContextVar de tenancy no worker assíncrono
    set_current_organization(organization_id)
    
    # 2. Garantir Idempotência via job_key
    job_key = f"job:wa_inbound:{organization_id}:{message_id}"
    if await cache_provider.exists(job_key):
        logger.info("Job duplicado ignorado", job_key=job_key, organization_id=organization_id)
        return
        
    await cache_provider.set(job_key, "processing", ttl=300)
    
    # 3. Chamar a camada de serviço de domínio
    try:
        await conversation_service.handle_inbound_message(lead_id, payload)
    except Exception as exc:
        logger.error("Erro no processamento da mensagem inbound", error=str(exc), job_key=job_key)
        raise exc
```

---

## 3. Disparo de Jobs na Rota FastAPI (HTTP 202)

```python
@router.post("/webhooks/zapi/incoming", status_code=202)
async def handle_zapi_webhook(payload: dict, request: Request):
    organization = request.state.organization
    message_id = payload.get("messageId")
    lead_id = payload.get("phone")
    
    # Enfileirar tarefa no Taskiq de forma assíncrona
    await process_inbound_message_task.kiq(
        organization_id=organization.id,
        lead_id=lead_id,
        message_id=message_id,
        payload=payload
    )
    
    # Retornar imediatamente para a Z-API
    return {"status": "queued"}
```

---

## 4. Anti-Patterns (NUNCA faça)

```
[X] Rodar await llm_service.generate() diretamente na rota HTTP -> Use task.kiq()
[X] Esquecer de passar organization_id para o job               -> Impossibilita isolamento tenant
[X] Não definir job_key para deduplicação                       -> Risco de re-envio duplo
[X] Deixar jobs rodando sem timeout                            -> Setar max execution time (ex: 30s)
```

---

## 5. Checklist de Validação

- [ ] A tarefa utiliza o decorator `@taskiq_broker.task`
- [ ] O primeiro passo da tarefa é invocar `set_current_organization(organization_id)`
- [ ] O `job_key` de deduplicação é validado no cache antes de executar
- [ ] A rota da API retorna `202 Accepted` imediatamente sem travar
