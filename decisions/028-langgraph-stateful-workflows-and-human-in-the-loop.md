# ADR-028: Workflows de Agentes Baseados em Estado com LangGraph e Human-in-the-Loop

* **Status**: Aprovado
* **Data**: Agosto 2026
* **Autores**: Equipe de Engenharia de IA e Arquitetura de Software (Revenue SDR OS)

---

## 1. Contexto e Problema

No **Revenue SDR OS**, um Agente de IA de vendas não opera como um bot rígido de árvore de decisões nem como uma simples chamada stateless de LLM. O processo comercial exige:
1. **Persistência de Estado Conversacional**: Manter histórico, variáveis de contexto (lead_id, organization_id, stage, memory_summary, proposed_slot) e histórico de ferramentas entre turnos de conversa.
2. **Ciclo Dinâmico de Decisão e Ferramentas**: Modelo decide se gera mensagem ou invoca ferramenta (ex: consultar agenda, registrar intenção), processa o resultado da ferramenta e decide o próximo passo.
3. **Intervenção Humana (Human-in-the-Loop / Handoff)**: Em situações sensíveis (negociação de preço acima do limite, transferência para vendedor humano, confirmação de agendamento de reuniões enterprise), a IA deve **pausar a execução** e aguardar aprovação explícita do vendedor humano antes de prosseguir.

---

## 2. Decisão Arquitetural

Adotar **LangGraph (`langgraph`)** para modelar todos os Agentes de IA como **Grafos Dirigidos de Estado (`StateGraph`)** com persistência por Checkpointer (`MemorySaver` / SQLite / Turso) e suporte nativo a pontos de interrupção humana (`interrupt`).

### Topologia Genérica de Grafo LangGraph no SDR OS:

```
                  +-----------------------------------+
                  |             START                 |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------------------------+
                  |        Node: Agent Reasoner       |
                  |  (ChatPromptTemplate + LLM Model) |
                  +-----------------+-----------------+
                                    |
            +-----------------------+-----------------------+
            | (Tool Calls Pending?)                         | (Final Text Response)
            v                                               v
+-----------------------+                         +-------------------+
|  Node: Execute Tools  |                         |        END        |
| (LangGraph ToolNode)  |                         +-------------------+
+-----------+-----------+
            |
            v (Check if Human Approval Required)
+-----------------------------------+
| Conditional Edge: Needs Approval? |
+-----------------+-----------------+
        |                   |
 (Yes)  v                   v (No)
+-----------------+   +-----------------------------------+
| Node: Interrupt |   | Loop back to Agent Reasoner Node  |
|  (Wait Human)   |   +-----------------------------------+
+-----------------+
```

---

## 3. Padrões de Implementação em LangGraph

### A. Definição do Esquema de Estado do Agente (`AgentState`)

```python
from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class SDRAgentState(TypedDict):
    # Histórico de mensagens concatenado automaticamente pelo LangGraph
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Variáveis de contexto do domínio do Revenue SDR OS
    organization_id: str
    lead_id: str
    lead_name: str
    current_stage: str
    dhs_score: int
    memory_context: str
    requires_human_approval: bool
    pending_action: str
```

### B. Definição do Grafo e Checkpointer

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# Instanciar o construtor do grafo
workflow = StateGraph(SDRAgentState)

# 1. Adicionar Nós
workflow.add_node("agent", call_sdr_agent_node)
workflow.add_node("tools", ToolNode(tools=[schedule_meeting_tool, update_stage_tool]))
workflow.add_node("human_approval", human_approval_node)

# 2. Adicionar Arestas (Edges)
workflow.add_edge(START, "agent")

# Aresta condicional: se o agente chamou ferramentas, vai para "tools", senão para END
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

# 3. Compilar Grafo com Checkpointer de Persistência
checkpointer = MemorySaver() # Em produção: TursoSaver ou SqliteSaver
sdr_agent_graph = workflow.compile(checkpointer=checkpointer)
```

### C. Mecanismo de Human-in-the-Loop (`interrupt`)

```python
from langgraph.errors import NodeInterrupt

async def human_approval_node(state: SDRAgentState):
    """Pausa a execução do agente e aguarda confirmação do operador no Zap Copilot."""
    if state.get("requires_human_approval"):
        # Lança interrupção tratada nativamente pelo LangGraph
        raise NodeInterrupt(f"Ação sensível '{state.get('pending_action')}' requer aprovação humana.")
    return state
```

---

## 4. Integração com o Zap SDR Prototype (`02_ZAP_Prototype`)

- **Modo Copilot**: Quando o `requires_human_approval` dispara uma interrupção, o servidor envia um evento SSE para o protótipo `02_ZAP_Prototype`. O painel exibe o modal de confirmação do vendedor (`Copilot Execution Confirmation`).
- **Retomada de Estado**: Quando o vendedor clica em **"Aprovar Ação"**, o endpoint `/api/v1/conversations/{id}/approve` executa `sdr_agent_graph.ainvoke(None, config=thread_config)` passando o estado atualizado para resumir o grafo do ponto de pausa.

---

## 5. Consequências e Benefícios

- **Determinismo e Controle**: Previne ações indesejadas de LLMs em produção via aprovação humana explícita.
- **Rastreabilidade Total**: O checkpointer armazena cada versão do estado da conversa por `thread_id` (combinando `organization_id` + `lead_id`).
- **Resiliência a Desligamentos**: Se o servidor reiniciar no meio de um fluxo multi-turnos, o estado é recarregado intacto do banco local.

---

## 6. AI Coding Guardrails

1. **NUNCA** armazenar o estado de um agente em memória global Python (`globals()`). Usar o `checkpointer` do LangGraph configurado por `thread_id`.
2. **SEMPRE** passar o `organization_id` na chave de thread ou configuração do LangGraph para prevenir vazamento de dados entre clientes (`cross-tenant leak`).
3. **SEMPRE** utilizar `Annotated[List[BaseMessage], add_messages]` para gerenciar o histórico no `TypedDict` do estado.
