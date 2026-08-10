---
name: langchain-langgraph-agent-architecture
description: Padrões de engenharia para desenvolvimento de Agentes de IA usando o ecossistema LangChain (langchain-core) e LangGraph (StateGraph), com fallbacks multinível, tool calling, checkpointers de estado, human-in-the-loop e observabilidade LangSmith.
---

# LangChain & LangGraph Multi-Agent Architecture Guidelines

> **Carregue esta skill para criar, refatorar ou depurar Agentes de IA, Grafos de Estado e Ferramentas no Revenue SDR OS.**

---

## 1. Princípios de Engenharia LangChain & LangGraph

1. **Separação de Preocupações**:
   - Prompts vivem em `ChatPromptTemplate` declarativos (nunca formatação manual de strings).
   - Ferramentas (`@tool`) utilizam schemas Pydantic `BaseModel` estritos em `args_schema`.
   - Agentes são construídos como **Grafos Dirigidos de Estado (`StateGraph`)** com checkpointers (`MemorySaver` / SQLite).
2. **Resiliência Multi-Provedor (`with_fallbacks`)**:
   - Todo modelo instanciado para produção DEVE envolver uma cadeia de fallback: Primário (Gemini 2.5 Flash / Claude 3.5 Sonnet) -> Secundário (GPT-4o-mini / Groq Llama-3.3).
3. **Isolamento de Tenant Zero-Trust**:
   - Cada sessão de agente LangGraph DEVE ter seu `thread_id` configurado no formato `{organization_id}:{lead_id}` para impedir vazamento de contexto entre organizações.
4. **Human-in-the-Loop (`interrupt`)**:
   - Ações de alto risco (reagendamento crítico, mudanças bruscas de preço, orçamentos especiais) devem invocar `interrupt()` para pausar o grafo e solicitar confirmação do vendedor no `02_ZAP_Prototype`.
5. **Observabilidade & Tracing via LangSmith**:
   - Injetar `tags` e `metadata` com `organization_id` e `lead_id` em todas as invocações de grafos ou LCEL chains.

---

## 2. Estrutura Padrão de Código de Agente (`app/ai/sdr_graph.py`)

```python
from typing import Annotated, List, TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# 1. Esquema de Estado do Agente
class SDRAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    organization_id: str
    lead_id: str
    lead_name: str
    current_stage: str
    requires_human_approval: bool

# 2. Definição da Ferramenta @tool
class ScheduleMeetingInput(BaseModel):
    start_time_iso: str = Field(description="Horário de início ISO8601 UTC")
    topic: str = Field(description="Pauta/assunto da reunião comercial")

@tool("schedule_meeting", args_schema=ScheduleMeetingInput)
async def schedule_meeting_tool(start_time_iso: str, topic: str) -> str:
    """Agenda uma reunião comercial no calendário do vendedor responsável."""
    return f"Reunião agendada para {start_time_iso} sobre {topic}."

# 3. Fábrica de Modelo Resiliente com Fallback
def build_resilient_sdr_model():
    primary = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3, request_timeout=2.5)
    fallback = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, request_timeout=3.0)
    tools = [schedule_meeting_tool]
    
    # Adiciona ferramentas e fallbacks nativos LangChain
    model_with_tools = primary.bind_tools(tools)
    fallback_with_tools = fallback.bind_tools(tools)
    return model_with_tools.with_fallbacks([fallback_with_tools])

# 4. Nó do Raciocinador do Grafo
async def sdr_agent_node(state: SDRAgentState):
    model = build_resilient_sdr_model()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é o Agente SDR Sênior da empresa. Nome do Lead: {lead_name}. Estágio: {current_stage}."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    chain = prompt | model
    response = await chain.ainvoke({
        "lead_name": state["lead_name"],
        "current_stage": state["current_stage"],
        "messages": state["messages"]
    })
    return {"messages": [response]}

# 5. Construção e Compilação do Grafo LangGraph
def create_sdr_agent_graph():
    workflow = StateGraph(SDRAgentState)
    
    workflow.add_node("agent", sdr_agent_node)
    workflow.add_node("tools", ToolNode(tools=[schedule_meeting_tool]))
    
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")
    
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)
```

---

## 3. Streaming SSE com LangChain `astream_events`

Para streaming de tokens em tempo real para o protótipo `02_ZAP_Prototype` via FastAPI e `sse-starlette`:

```python
from sse_starlette.sse import EventSourceResponse

async def stream_sdr_graph_response(graph, input_messages, org_id: str, lead_id: str):
    config = {
        "configurable": {"thread_id": f"{org_id}:{lead_id}"},
        "tags": [f"tenant:{org_id}", "agent:sdr"],
        "metadata": {"organization_id": org_id, "lead_id": lead_id}
    }
    
    async def event_generator():
        async for event in graph.astream_events({"messages": input_messages}, config=config, version="v2"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield {"event": "token", "data": content}
            elif kind == "on_tool_start":
                yield {"event": "tool_start", "data": event["name"]}
            elif kind == "on_tool_end":
                yield {"event": "tool_end", "data": str(event["data"].get("output"))}

    return EventSourceResponse(event_generator())
```

---

## 4. Checklist para Revisão de Código com LangChain / LangGraph

- [ ] Prompts utilizam `ChatPromptTemplate` e `MessagesPlaceholder` (sem f-strings brutas).
- [ ] Ferramentas `@tool` possuem `args_schema` derivado de `BaseModel` Pydantic v2 com descrições em todos os campos.
- [ ] Invocação do modelo inclui `with_fallbacks()` configurado com timeout.
- [ ] O estado do grafo utiliza `Annotated[List[BaseMessage], add_messages]`.
- [ ] Configuração da thread do LangGraph contém a tag `{organization_id}:{lead_id}`.
- [ ] Variáveis `LANGCHAIN_TRACING_V2` e metadados de tenant são repassados ao LangSmith.
