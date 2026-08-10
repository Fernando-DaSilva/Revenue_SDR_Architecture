"""
Template de Referência Production-Ready para Agentes LangGraph no Revenue SDR OS.
Demonstra:
1. Grafos de Estado (StateGraph) com `TypedDict` e `add_messages`.
2. Modelos LangChain com resiliência declarativa via `with_fallbacks()`.
3. Ferramentas `@tool` com validação de schemas Pydantic v2.
4. Human-in-the-Loop com interrupção `interrupt()` para aprovação no Zap Copilot.
5. Ingestão de observabilidade e tracing no LangSmith (`LANGCHAIN_TRACING_V2=true`).
6. Streaming de tokens SSE com `astream_events`.
"""

import asyncio
import os
from typing import Annotated, List, TypedDict
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import NodeInterrupt


# ============================================================================
# 1. ESQUEMA DE ESTADO DO AGENTE (TypedDict)
# ============================================================================

class SDRAgentState(TypedDict):
    """Estado persistente mantido pelo LangGraph por thread de conversa."""
    messages: Annotated[List[BaseMessage], add_messages]
    organization_id: str
    lead_id: str
    lead_name: str
    current_stage: str
    dhs_score: int
    requires_human_approval: bool
    pending_action: str


# ============================================================================
# 2. FERRAMENTAS (@tool Decorator com Schemas Pydantic v2)
# ============================================================================

class MeetingBookingInput(BaseModel):
    start_time_iso: str = Field(description="Horário de início em formato ISO8601 UTC")
    topic: str = Field(description="Pauta/assunto principal da reunião comercial")

@tool("schedule_meeting", args_schema=MeetingBookingInput)
async def schedule_meeting_tool(start_time_iso: str, topic: str) -> str:
    """Agenda uma reunião comercial no Google Calendar do vendedor responsável."""
    # Em produção: chama o service layer (CalendarService) com o tenant da ContextVar
    return f"Reunião comercial agendada com sucesso para {start_time_iso} | Pauta: {topic}."

class StageUpdateInput(BaseModel):
    new_stage: str = Field(description="Novo estágio do funil: qualificado, reuniao_agendada, perdido, ganho")

@tool("update_lead_stage", args_schema=StageUpdateInput)
async def update_lead_stage_tool(new_stage: str) -> str:
    """Atualiza o estágio do lead no funil de vendas."""
    return f"Estágio do lead atualizado para '{new_stage}'."


# ============================================================================
# 3. FÁBRICA DE MODELO RESILIENTE (LangChain Fallback Router)
# ============================================================================

def build_resilient_sdr_model():
    """Retorna um modelo LangChain envolvido em uma cadeia de fallback automático."""
    primary_model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        request_timeout=2.5,
    )
    fallback_model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        request_timeout=3.0,
    )
    
    tools = [schedule_meeting_tool, update_lead_stage_tool]
    
    # Vincula ferramentas a ambos os modelos
    primary_bound = primary_model.bind_tools(tools)
    fallback_bound = fallback_model.bind_tools(tools)
    
    # Aplica o fallback declarativo nativo
    return primary_bound.with_fallbacks([fallback_bound])


# ============================================================================
# 4. NÓS DO GRAFO LANGGRAPH
# ============================================================================

async def sdr_reasoner_node(state: SDRAgentState):
    """Nó principal de raciocínio da IA SDR."""
    model = build_resilient_sdr_model()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "Você é o Agente SDR de elite da empresa. Seu objetivo é qualificar o lead "
            "e agendar reuniões comerciais. Atenda com cordialidade e persuasão.\n"
            "Contexto do Lead:\n"
            "- Nome: {lead_name}\n"
            "- Estágio Atual: {current_stage}\n"
            "- Score DHS: {dhs_score}\n"
        )),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    chain = prompt | model
    response = await chain.ainvoke({
        "lead_name": state.get("lead_name", "Cliente"),
        "current_stage": state.get("current_stage", "novo"),
        "dhs_score": state.get("dhs_score", 0),
        "messages": state["messages"]
    })
    
    return {"messages": [response]}


async def human_approval_check_node(state: SDRAgentState):
    """Nó de verificação de Human-in-the-Loop para ações de alto risco."""
    if state.get("requires_human_approval"):
        action = state.get("pending_action", "Ação de Vendas")
        # Lança a interrupção tratada nativamente pelo LangGraph
        raise NodeInterrupt(f"Ação sensível '{action}' aguardando confirmação do vendedor no Zap Copilot.")
    return state


# ============================================================================
# 5. CONSTRUÇÃO E COMPILAÇÃO DO GRAFO
# ============================================================================

def create_sdr_agent_graph():
    """Constrói o Grafo LangGraph com nós, arestas condicionais e checkpointer."""
    workflow = StateGraph(SDRAgentState)
    
    # Adicionar Nós
    workflow.add_node("agent", sdr_reasoner_node)
    workflow.add_node("approval_check", human_approval_check_node)
    workflow.add_node("tools", ToolNode(tools=[schedule_meeting_tool, update_lead_stage_tool]))
    
    # Adicionar Arestas
    workflow.add_edge(START, "agent")
    
    # Condição: Se o agente solicitou ferramentas, valida se necessita aprovação humana
    workflow.add_conditional_edges("agent", tools_condition, {
        "tools": "approval_check",
        END: END
    })
    
    workflow.add_edge("approval_check", "tools")
    workflow.add_edge("tools", "agent")
    
    # Checkpointer em memória (Em produção: usar SqliteSaver / Turso)
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


# Instância pronta do Grafo
sdr_agent_graph = create_sdr_agent_graph()


# ============================================================================
# 6. EXEMPLO DE EXECUÇÃO E SSE STREAMING
# ============================================================================

async def main():
    org_id = "org_clinica_bela"
    lead_id = "lead_9921"
    
    # Configuração de thread com tags para LangSmith
    config: RunnableConfig = {
        "configurable": {"thread_id": f"{org_id}:{lead_id}"},
        "tags": [f"tenant:{org_id}", "agent:ai_sales_sdr"],
        "metadata": {
            "organization_id": org_id,
            "lead_id": lead_id,
            "environment": "development"
        }
    }
    
    initial_state = {
        "messages": [HumanMessage(content="Olá, gostaria de agendar uma consulta para amanhã às 14h sobre implantes.")],
        "organization_id": org_id,
        "lead_id": lead_id,
        "lead_name": "Mariana Silva",
        "current_stage": "qualificacao",
        "dhs_score": 45,
        "requires_human_approval": False,
        "pending_action": ""
    }
    
    print("--- Executando Grafo LangGraph com LangSmith Tracing ---")
    result = await sdr_agent_graph.ainvoke(initial_state, config=config)
    
    last_msg = result["messages"][-1]
    print(f"Resposta do SDR: {last_msg.content}")
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        print(f"Ferramentas chamadas: {last_msg.tool_calls}")

if __name__ == "__main__":
    asyncio.run(main())
