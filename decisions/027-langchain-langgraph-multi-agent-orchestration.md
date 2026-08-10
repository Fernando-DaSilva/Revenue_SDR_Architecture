# ADR-027: Orquestração de Agentes com Ecossistema LangChain e LangGraph

* **Status**: Aprovado
* **Data**: Agosto 2026
* **Autores**: Equipe de Engenharia de IA e Arquitetura de Software (Revenue SDR OS)

---

## 1. Contexto e Problema

O **Revenue SDR OS** necessita conduzir diálogos complexos e conversacionais de vendas através de múltiplos canais (WhatsApp, Instagram DM, E-mail, Voz). A operação envolve 6 Agentes de IA especializados:
1. **AI Sales SDR Agent**: Atendimento ativo, qualificação e agendamento de reuniões.
2. **Lead Memory Extractor Agent**: Extração contínua de preferências, fatos e objeções em background.
3. **Opportunity Intent Classifier Agent**: Scoring de intenção e ajuste da temperatura do lead.
4. **Cadence Re-engagement Agent**: Reativação contextual de leads dormentes via réguas.
5. **Voice Audio Agent**: Transcrição, diarização e análise de mensagens de voz.
6. **Sales Coach Agent**: Análise pós-conversa, auditoria de performance comercial e feedback.

No estágio anterior (ADR-023), o sistema utilizava `Instructor + Pydantic v2` para chamadas 1-shot de saída estruturada e um roteador customizado. Porém, fluxos conversacionais avançados demandam:
- **Execução de Ferramentas (Tool Calling)**: Decisão dinâmica de executar ferramentas como `schedule_meeting`, `update_lead_stage`, `add_memory`.
- **Cadeias de Execução Declarativas (LCEL)**: Composição transparente de Prompts, Modelos, Output Parsers e Tools.
- **Roteamento de Fallbacks Multinível**: Transição automática entre Gemini 2.5 Flash, Claude 3.5 Sonnet, GPT-4o-mini e Groq Llama-3.3 sem reescrever código.
- **Orquestração de Grafos de Estado**: Agentes com memória conversacional persistente, ramificações condicionais e ciclos de execução.

---

## 2. Decisão Arquitetural

Adotar o **Ecossistema LangChain (`langchain-core`, `langchain-community`)** e o **LangGraph (`langgraph`)** como a estrutura oficial de orquestração de Agentes de IA, execução de ferramentas, cadeias conversacionais e grafos de estado no Revenue SDR OS.

### Arquitetura de Camadas com LangChain & LangGraph:

```
+-----------------------------------------------------------------------------------+
|                           LangGraph Stateful Multi-Agent                          |
|                       (StateGraph + MemorySaver Checkpointer)                     |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        LangChain Runnable (LCEL Chain)                            |
|    ChatPromptTemplate -> ChatModel.with_fallbacks() -> Pydantic / Tool Parser    |
+----------------------------------------+------------------------------------------+
                                         |
                                         +-----------------------+
                                         |                       |
                                         v                       v
+---------------------------------------------------+ +-----------------------------+
| Modelos de Chat (langchain_core / providers)      | | Ferramentas (@tool)         |
| - ChatGoogleGenerativeAI (Gemini 2.5 Flash)       | | - schedule_meeting()        |
| - ChatAnthropic (Claude 3.5 Sonnet)               | | - update_lead_stage()       |
| - ChatOpenAI (GPT-4o-mini) / ChatGroq (Llama-3.3)  | | - query_knowledge_base()    |
+---------------------------------------------------+ +-----------------------------+
```

---

## 3. Padrões de Implementação

### A. Roteamento de Modelos com Fallbacks Nativos (`with_fallbacks`)

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

def get_resilient_sdr_model():
    # Modelos configurados com timeouts e retentativas
    primary = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        request_timeout=2.5,
    )
    fallback_sonnet = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.3,
        request_timeout=2.5,
    )
    fallback_gpt = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        request_timeout=3.0,
    )
    
    # Cadeia de Fallback declarativa via LangChain
    return primary.with_fallbacks([fallback_sonnet, fallback_gpt])
```

### B. Definição de Ferramentas (`@tool` Decorator)

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class MeetingBookingInput(BaseModel):
    lead_id: str = Field(description="ID do lead no sistema")
    start_time_iso: str = Field(description="Horário de início em formato ISO8601 UTC")
    topic: str = Field(description="Pauta/assunto da reunião")

@tool("schedule_meeting", args_schema=MeetingBookingInput)
async def schedule_meeting_tool(lead_id: str, start_time_iso: str, topic: str) -> str:
    """Agenda uma reunião comercial no Google Calendar do vendedor responsável."""
    # Acesso via service layer filtrado por tenant
    return f"Reunião agendada com sucesso para {start_time_iso} com pauta: {topic}."
```

### C. Saídas Estruturadas via `with_structured_output`

```python
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

class LeadScoringOutput(BaseModel):
    intent_score: int = Field(ge=-100, le=100, description="Score DHS de intenção (-100 a +100)")
    temperature: str = Field(description="Temperatura: Frio, Morno, Quente, Pegando Fogo")
    reasoning: str = Field(description="Justificativa sucinta do scoring")

scoring_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um classificador de intenção de vendas B2B."),
    ("user", "Analise a conversa do lead {lead_name}:\n{transcript}")
])

async def evaluate_lead_intent(lead_name: str, transcript: str, model):
    structured_model = model.with_structured_output(LeadScoringOutput)
    chain = scoring_prompt | structured_model
    result: LeadScoringOutput = await chain.ainvoke({"lead_name": lead_name, "transcript": transcript})
    return result
```

---

## 4. Integração com FastAPI e Taskiq Background Jobs

- **Execução Assíncrona**: Todas as invocações LangChain devem ser executadas via métodos assíncronos (`ainvoke`, `astream`, `astream_events`).
- **Streaming em Tempo Real (SSE)**: O endpoint FastAPI de bate-papo via web ou Zap Copilot utiliza `astream_events` para emitir eventos parciais de geração para a interface do vendedor via Server-Sent Events (`sse-starlette`).
- **Isolamento por Tenant**: O `organization_id` do tenant é injetado nas ferramentas e no estado do grafo via ContextVar ASGI, garantindo que o agente só acesse dados da sua organização.

---

## 5. Consequências e Benefícios

- **Padronização**: Toda a lógica de comunicação com LLMs segue a especificação oficial LangChain.
- **Resiliência Máxima**: Falhas no provedor principal disparam fallbacks instantâneos sem quebrar a sessão do usuário.
- **Modularidade de Ferramentas**: Agentes compartilham ferramentas tipadas com validação Pydantic.
- **Compatibilidade com Instructor**: O Instructor permanece utilizado para validações de schema ultra-estritas em jobs batch, enquanto LangChain/LangGraph lidera fluxos conversacionais e multi-agentes.

---

## 6. AI Coding Guardrails

1. **NUNCA** concatenar strings manualmente para montar prompts. Usar `ChatPromptTemplate` do LangChain.
2. **SEMPRE** aplicar `with_fallbacks()` ao instanciar modelos para produção.
3. **SEMPRE** utilizar `@tool` com `args_schema` derivado de `BaseModel` Pydantic v2.
