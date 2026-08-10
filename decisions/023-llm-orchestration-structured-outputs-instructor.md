# ADR-023: Orquestração de LLMs, Saídas Estruturadas via Instructor e Cadeia de Fallbacks

* **Status**: Aprovado
* **Data**: Agosto 2026
* **Autores**: Equipe de Sistemas de IA e Arquitetura de Software (Revenue SDR OS)

---

## 1. Contexto e Problema

O **Revenue SDR OS** depende fundamentalmente de LLMs para operar como um vendedor autônomo e analista de receita. As tarefas de IA incluem:
1. **Extração de Memórias do Lead** (*Memory Brain*): Identificar nome, empresa, orçamento, tomadores de decisão e objeções do texto e retornar JSON estrito.
2. **Qualificação e Scoring de Oportunidade** (*Opportunity Brain*): Calcular temperatura, score DHS (-100 a +100) e próximos passos.
3. **Diálogo Ativo e Tool Calling** (*AI Sales SDR Agent*): Decidir se deve agendar reunião (`schedule_meeting`), atualizar estágio (`update_stage`) ou solicitar intervenção humana (`handoff_to_human`).
4. **Coaching Pós-Conversa**: Gerar pareceres estruturados de performance comercial.

Se a LLM retornar texto livre com formatação JSON inválida, Markdown solto ou parâmetros errados em chamadas de ferramentas, a aplicação sofrerá exceções de parsing (`JSONDecodeError`), falhas de validação de schema e comportamento imprevisível em produção.

---

## 2. Decisão Arquitetural

Adotar o **Instructor** (baseado em **Pydantic v2**) como a biblioteca oficial de orquestração de saídas estruturadas (*Structured Outputs*) de LLMs em todo o backend Python, combinado com o padrão de **Cadeia de Fallback de Provedores (Multi-Tier LLM Gateway)**.

### Pilares da Decisão:

```
+-----------------------------------------------------------------------------------+
| Roteador de Chamadas LLM (LLM Gateway Service)                                     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| Provedor Primário: Google Gemini 2.5 Flash / Claude 3.5 Sonnet                     |
|  - Instructor (Pydantic Schema Validation)                                        |
|  - Retry automático em caso de erro de Schema Validation (máx 2 retentativas)      |
+----------------------------------------+------------------------------------------+
                                         | (Se falhar / Timeout > 3s / Erro 5xx)
                                         v
+-----------------------------------------------------------------------------------+
| Provedor de Fallback: OpenAI GPT-4o-mini / Groq Llama 3.3                         |
|  - Validação estrita mantida via mesmo schema Pydantic                            |
+-----------------------------------------------------------------------------------+
```

---

## 3. Padrões de Implementação com Instructor & Pydantic

### A. Extração Estruturada Estrita (Exemplo Memory Extractor)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
import instructor
from google.genai import types

# 1. Definir Schema Pydantic estrito de Saída
class ExtractedMemoryItem(BaseModel):
    category: str = Field(description="Categoria: orcamento, objecao, cronograma, decisor, preferencia")
    key: str = Field(description="Chave normalizada em snake_case (ex: orcamento_maximo)")
    value: str = Field(description="Valor extraído ou fato identificado")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Score de confiança de 0.0 a 1.0")

class LeadMemoryExtractionResult(BaseModel):
    memories: List[ExtractedMemoryItem]
    detected_intent: str = Field(description="Intenção principal do lead no turno")
    suggested_dhs_delta: int = Field(ge=-20, le=20, description="Variação sugerida no score DHS")

# 2. Executar via Client Instructor com Validação Automática
async def extract_memories_from_transcript(
    transcript_text: str,
    client: instructor.AsyncInstructor
) -> LeadMemoryExtractionResult:
    result = await client.chat.completions.create(
        response_model=LeadMemoryExtractionResult,
        messages=[
            {"role": "system", "content": "Você é um extrator de inteligência comercial sênior."},
            {"role": "user", "content": f"Extraia fatos e memórias relevantes do texto:\n{transcript_text}"}
        ],
        max_retries=2,  # Instructor reinsere o erro no prompt e pede correção à LLM automaticamente!
    )
    return result
```

---

## 4. Estratégia de Fallback e Resiliência (LLM Circuit Breaker)

1. **Timeout Estrito por Turno**:
   - Agente SDR Principal: Timeout de 2.5s.
   - Jobs de Extração de Memória / Background: Timeout de 10.0s.
2. **Circuit Breaker Pattern**:
   - Se o provedor principal registrar 5 falhas consecutivas de rede ou erro 5xx num período de 60 segundos, a rota é comutada automaticamente para o provedor secundário de reserva.
3. **Prompt Caching Header**:
   - Cabeçalhos de cache de System Prompt ativados em todas as chamadas para reaproveitar instâncias de RAG estáticas e reduzir latência e custos em 75-90%.

---

## 5. Consequências e Benefícios

* **Zero Exceções de Parsing**: Todas as saídas de LLM chegam convertidas e validadas como objetos Pydantic nativos com garantia de tipagem estática.
* **Recuperação Autônoma de Erros**: O Instructor envia a mensagem de erro da validação Pydantic de volta para a LLM refazer a resposta em caso de tipo inválido.
* **Independência de Provedor**: A camada de serviços consome schemas Pydantic; trocar de OpenAI para Gemini ou Anthropic requer apenas alterar a instância do client Instructor.

---

## 6. Invariantes para Agentes de Codificação (AI Coding Guardrails)

1. **NUNCA** utilizar expressões regulares (`re.search`) ou `json.loads()` brutos para extrair JSON de respostas de LLMs. Usar **SEMPRE** o Instructor com um `response_model` Pydantic.
2. **SEMPRE** utilizar `Field(description=...)` em todos os atributos dos schemas Pydantic de LLM, pois as descrições orientam o modelo durante a geração.
3. **SEMPRE** tratar a exceção `instructor.exceptions.InstructorRetryException` capturando falhas definitivas e registrando no log estruturado com contexto do tenant.
