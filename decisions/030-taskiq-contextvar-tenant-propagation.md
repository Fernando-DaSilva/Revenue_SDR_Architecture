# ADR-030: Middleware de Propagação Automática de ContextVar de Tenancy no Taskiq (TenantTaskiqMiddleware)

* **Status**: Aprovado
* **Data**: Agosto 2026
* **Autores**: Equipe de Arquitetura e Engenharia Backend (Revenue SDR OS)

---

## 1. Contexto e Problema

No **Revenue SDR OS**, a segurança multi-tenant baseia-se no princípio **Zero-Trust com ContextVar**:
- Quando uma requisição HTTP chega ao FastAPI, o `TenantResolutionMiddleware` resolve a organização ativa e seta a variável de contexto `current_organization` (Python `ContextVar`).
- Todos os serviços de domínio (`LeadService`, `ConversationService`, `RAGService`) dependem da ContextVar `current_organization` para injetar o filtro obrigatório `.where(Model.organization_id == current_organization.get().id)` nas queries SQL.

### A Vulnerabilidade Crítica Descoberta no Audit (RSK-01)
Ao receber um webhook inbound (ex: mensagem do WhatsApp via Z-API), o endpoint HTTP responde em menos de 50ms com `HTTP 202 Accepted` e despacha o processamento da LLM para a fila assíncrona usando o Taskiq (`await broker.kiq(...)`).

Contudo, **as variáveis de contexto do Python (`ContextVar`) NÃO são propagadas automaticamente através de threads ou processos workers do Taskiq**.

**Impacto:**
1. Os workers do Taskiq executavam tarefas em segundo plano com `current_organization` vazia (`None`), gerando exceções do tipo `LookupError`.
2. Em cenários sem tratamento estrito, queries em workers assíncronos poderiam ser executadas sem o filtro de `organization_id`, violando o isolamento Zero-Trust e arriscando vazamento de dados cross-tenant.
3. Adicionalmente, no modo Standalone VPS onde o Taskiq utiliza broker SQLite embarcado, compartilhar o mesmo arquivo de banco de dados (`app_data.db`) entre a aplicação FastAPI e a fila do Taskiq gerava travamento de gravação (`database is locked`) sob carga pesada de webhooks.

---

## 2. Decisão Arquitetural

Adotar o middleware customizado **`TenantTaskiqMiddleware`** no Taskiq para garantir a serialização e hidratação automática do contexto de tenancy em todas as tarefas assíncronas, combinado com a **separação física de arquivos SQLite** em deployments standalone.

### A. Funcionamento do `TenantTaskiqMiddleware`

O middleware estende `TaskiqMiddleware` e intercepta o ciclo de vida da tarefa em três etapas:

1. **`pre_send(message: TaskiqMessage)` (Thread da Requisição HTTP)**:
   - Captura a organização ativa via `current_organization.get(None)`.
   - Serializa o `organization_id` nos rótulos de contexto da mensagem do Taskiq (`message.labels["organization_id"] = str(org.id)`).

2. **`pre_execute(message: TaskiqMessage)` (Thread/Processo do Worker Taskiq)**:
   - Extrai o `organization_id` do cabeçalho da mensagem (`message.labels`).
   - Hidrata a ContextVar `current_organization.set(OrganizationContext(id=org_id))`.
   - **Guardrail**: Se `organization_id` não estiver presente na mensagem, lança imediatamente uma exceção `RuntimeError("Taskiq job executed without organization_id context!")`, abortando o job antes de qualquer interações com banco ou serviços.

3. **`post_execute(message: TaskiqMessage, result: TaskiqResult)` (Finalização do Job)**:
   - Reseta a ContextVar `current_organization.set(None)` para evitar contaminação do pool de threads do worker.

```
FastAPI Endpoint (Request Thread)
  | ContextVar: current_organization = org_123
  v
Taskiq Broker (kiq)
  | TenantTaskiqMiddleware.pre_send()
  | -> Inject message.labels["organization_id"] = "org_123"
  v
[Queue: Redis / Taskiq Queue DB]
  |
  v
Taskiq Worker Process
  | TenantTaskiqMiddleware.pre_execute()
  | -> Hydrate ContextVar: current_organization.set(OrganizationContext(id="org_123"))
  v
Service / LangGraph Agent Execution (Safely filtered by org_123)
  v
TenantTaskiqMiddleware.post_execute()
  | -> Clear ContextVar
```

### B. Separação Física de Bancos SQLite em Modo Standalone VPS

Para eliminar o risco de lock em concorrência (`database is locked`), deployments em standalone VPS usando broker SQLite do Taskiq DEVEM utilizar arquivos de banco separados:
- `app_data.db`: Banco principal de dados de aplicação, leads e conversas (Turso / libSQL local WAL mode).
- `taskiq_queue.db`: Arquivo SQLite isolado exclusivamente para a fila e estado do broker Taskiq.

---

## 3. Código de Referência de Implementação

```python
# app/tasks/middleware.py
from taskiq import TaskiqMiddleware, TaskiqMessage, TaskiqResult
from app.tenancy.context import current_organization, OrganizationContext
from app.core.logging import logger

class TenantTaskiqMiddleware(TaskiqMiddleware):
    """
    Garante a propagação transparente e segura da ContextVar organization_id
    da thread da API HTTP para o contexto de execução dos workers do Taskiq.
    """

    def pre_send(self, message: TaskiqMessage) -> TaskiqMessage:
        org = current_organization.get(None)
        if org and hasattr(org, "id"):
            message.labels["organization_id"] = str(org.id)
            logger.debug(
                "Tenant context serialized into Taskiq message",
                task_name=message.task_name,
                org_id=str(org.id),
            )
        return message

    def pre_execute(self, message: TaskiqMessage) -> TaskiqMessage:
        org_id = message.labels.get("organization_id")
        if not org_id:
            logger.error(
                "CRITICAL: Taskiq task dispatched without organization_id label",
                task_name=message.task_name,
            )
            raise RuntimeError(
                f"Task '{message.task_name}' executed without required organization_id context!"
            )

        current_organization.set(OrganizationContext(id=org_id))
        logger.debug(
            "Tenant context hydrated in Taskiq worker",
            task_name=message.task_name,
            org_id=org_id,
        )
        return message

    def post_execute(self, message: TaskiqMessage, result: TaskiqResult) -> None:
        current_organization.set(None)
```

---

## 4. Consequências

* **Positivas**:
  - Eliminada a brecha de isolamento em tarefas de background. 100% dos workers operam com tenant hidratado de forma transparente.
  - Tentativas de despachar ou executar jobs sem tenant falham ruidosamente no `pre_execute`, impedindo comportamentos não determinísticos.
  - A separação de `app_data.db` e `taskiq_queue.db` zera travamentos `database is locked` sob alta ingestão de webhooks.
* **Negativas / Riscos**:
  - Exige o registro obrigatório de `TenantTaskiqMiddleware` na inicialização do broker do Taskiq (`broker.add_middlewares(TenantTaskiqMiddleware())`).

---

## 5. Invariantes para Agentes de Codificação (AI Coding Guardrails)

1. **NUNCA** remover ou burlar o `TenantTaskiqMiddleware` na declaração de brokers em `app/tasks/broker.py`.
2. **NUNCA** assumir que `current_organization` se propaga sozinho sem o middleware do Taskiq.
3. **SEMPRE** utilizar `taskiq_queue.db` como DSN do broker SQLite em modo standalone, mantendo-o fisicamente separado de `app_data.db`.
