# ADR-029: Observabilidade, Tracing e Avaliação de Agentes com LangSmith

* **Status**: Aprovado
* **Data**: Agosto 2026
* **Autores**: Equipe de Engenharia de IA e Observabilidade (Revenue SDR OS)

---

## 1. Contexto e Problema

Com a operação em produção do **Revenue SDR OS** em múltiplas VPSs dedicadas (modelo On-Premise-as-a-Service), diagnosticar o comportamento dos 6 Agentes de IA exige visibilidade detalhada de:
1. **Tracing de Execução Multi-Agente**: Visualizar a árvore completa de chamadas de LLM, tempo gasto em cada nó do LangGraph, parâmetros passados para as ferramentas (`@tool`) e respostas intermediárias.
2. **FinOps Técnico e Telemetria de Tokens**: Acompanhar consumo de tokens (`input`, `output`, `cached`) rotulados com o `organization_id` do tenant para contabilidade e faturamento.
3. **Avaliação Contínua de Qualidade (Evals)**: Testar regressões em prompts e comparar a taxa de conversão/qualificação dos agentes em relação a benchmarks históricos.
4. **Resiliência de Rede**: A telemetria de tracing não pode travar ou lentificar a execução da resposta ao cliente final caso o serviço de observabilidade esteja indisponível.

---

## 2. Decisão Arquitetural

Adotar o **LangSmith** como a plataforma oficial de observabilidade, tracing, gerenciamento de prompts e avaliação de agentes do ecossistema LangChain/LangGraph no Revenue SDR OS.

### Mecanismo de Ingestão e Instrumentação:

```
+-----------------------------------------------------------------------------------+
|                            FastAPI App / Taskiq Worker                            |
+----------------------------------------+------------------------------------------+
                                         |
                                         v (Async Tracing Collector)
+-----------------------------------------------------------------------------------+
|                      LangChain / LangGraph Execution Core                         |
|  (Injeta automaticamente tags: organization_id, lead_id, agent_name, environment) |
+----------------------------------------+------------------------------------------+
                                         |
                    +--------------------+--------------------+
                    | (Se LANGCHAIN_TRACING_V2=true)          | (Fallback Interno)
                    v                                         v
+----------------------------------------+ +----------------------------------------+
|          LangSmith API SaaS            | |      Structured JSON Logs (ADR-014)     |
| - Tracing Visual de Nós do LangGraph   | | - Ingestão local em structlog           |
| - Telemetria de Custo/Tokens           | | - Métricas Prometheus / OpenTelemetry  |
| - Suite de Testes de Evals             | +----------------------------------------+
+----------------------------------------+
```

---

## 3. Padrões de Configuração e Instrumentação

### A. Variáveis de Ambiente e Inicialização (em `.env`)

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="lsv2_pt_..."
LANGCHAIN_PROJECT="revenue-sdr-os-prod"
```

### B. Enriquecimento de Contexto Multi-Tenant no Middleware FastAPI

```python
from langchain_core.callbacks import AsyncCallbackHandler
from contextlib import asynccontextmanager

class TenantTracingCallbackHandler(AsyncCallbackHandler):
    """Callback customizado LangChain para injetar metadados de tenancy e tracing."""
    def __init__(self, organization_id: str, lead_id: str, agent_name: str):
        self.organization_id = organization_id
        self.lead_id = lead_id
        self.agent_name = agent_name

    async def on_chain_start(self, serialized, inputs, **kwargs):
        # Tags enviadas diretamente ao LangSmith
        kwargs.setdefault("tags", []).extend([
            f"org:{self.organization_id}",
            f"lead:{self.lead_id}",
            f"agent:{self.agent_name}"
        ])
```

### C. Uso em Invocação de Agente no Grafo LangGraph

```python
from langchain_core.runnables import RunnableConfig

async def run_sdr_agent_with_tracing(graph, initial_state: dict, org_id: str, lead_id: str):
    config: RunnableConfig = {
        "configurable": {"thread_id": f"{org_id}:{lead_id}"},
        "tags": [f"tenant:{org_id}", "agent:ai_sales_sdr"],
        "metadata": {
            "organization_id": org_id,
            "lead_id": lead_id,
            "environment": "production"
        }
    }
    
    # Executa o grafo LangGraph gravando o trace completo no LangSmith
    return await graph.ainvoke(initial_state, config=config)
```

---

## 4. Avaliação de Agentes (Evals) e Benchmarking

- **Datasets de Teste no LangSmith**: O time de engenharia mantém um dataset contendo 100+ diálogos reais anonimizados de leads (perguntas sobre preço, objeções técnicas, agendamento fora de horário).
- **Execução CI/CD**: A cada atualização de System Prompt ou versão de modelo, a suíte de avaliação é disparada via CLI do LangSmith para validar a taxa de acerto do scoring DHS e a ausência de alucinações.

---

## 5. Consequências e Benefícios

- **Diagnóstico em Segundos**: Identificação exata de qual nó do LangGraph causou latência ou resposta inadequada.
- **Auditoria de Custos por Cliente**: Relatórios de consumo por `organization_id` derivados dos atributos gravados no LangSmith.
- **Resiliência Silenciosa**: Se a conectividade com o LangSmith falhar ou a chave for omitida, a aplicação continua funcionando normalmente e canaliza logs estruturados para a infraestrutura local (ADR-014).

---

## 6. AI Coding Guardrails

1. **SEMPRE** repassar as `tags` e `metadata` contendo `organization_id` e `lead_id` nas chamadas ao LangGraph.
2. **NUNCA** gravar dados pessoais não criptografados ou senhas nos metadados do LangSmith (cumprimento LGPD - ADR-018).
3. **SEMPRE** utilizar o `LANGCHAIN_PROJECT` separado para ambientes de desenvolvimento (`dev`), homologação (`staging`) e produção (`prod`).
