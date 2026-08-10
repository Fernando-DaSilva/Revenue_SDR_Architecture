---
name: llm-agent-orchestration-and-instructor
description: |
  Carregue esta skill sempre que for implementar orquestração de LLMs, 
  extração de saídas estruturadas com Instructor/Pydantic v2, chamadas de ferramentas 
  (tool calling), prompt caching, ou roteamento de fallback entre Gemini e Claude/OpenAI.
version: 1.0.0
author: Hermes (arquiteto)
license: Proprietary
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
metadata:
  hermes:
    tags: [instructor, pydantic, llm-router, structured-outputs, gemini, claude, prompt-caching]
---

# Skill: Orquestração de LLMs, Instructor e Saídas Estruturadas

## 1. Princípio Fundamental

No **Revenue SDR OS**, chamadas para LLMs **NUNCA** devem utilizar parsing de texto livre ou `json.loads()` brutos.
Toda e qualquer interação com modelos de linguagem que exija dados estruturados DEVE utilizar o **Instructor** acoplado a **Schemas Pydantic v2**.

---

## 2. Padrão de Código — Client Instructor com Pydantic v2

```python
from typing import List, Optional
from pydantic import BaseModel, Field
import instructor
from google.genai import types

# 1. Definir Schema Pydantic estrito
class ExtractedMemory(BaseModel):
    category: str = Field(description="Categoria: orcamento, objecao, cronograma, decisor, preferencia")
    key: str = Field(description="Chave em snake_case (ex: orcamento_maximo)")
    value: str = Field(description="Valor extraído ou fato identificado")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Score de confiança entre 0.0 e 1.0")

class ExtractionResponse(BaseModel):
    memories: List[ExtractedMemory]
    intent: str = Field(description="Intenção principal identificada no turno")
    suggested_dhs_delta: int = Field(ge=-20, le=20, description="Variação no score DHS")

# 2. Executar Chamada via Client Instructor
async def extract_structured_data(
    prompt_text: str,
    client: instructor.AsyncInstructor
) -> ExtractionResponse:
    try:
        response = await client.chat.completions.create(
            response_model=ExtractionResponse,
            messages=[
                {"role": "system", "content": "Você é um extrator de inteligência comercial sênior."},
                {"role": "user", "content": prompt_text}
            ],
            max_retries=2,  # Instructor tenta re-corrigir respostas de schema automaticamente
        )
        return response
    except instructor.exceptions.InstructorRetryException as e:
        logger.error("Falha na validação do schema do Instructor após retentativas", error=str(e))
        raise AppError(code="llm_extraction_failed", message="Falha ao extrair dados estruturados de IA.")
```

---

## 3. Padrão de Roteamento de Fallback (LLM Router)

```python
class LLMRouterService:
    def __init__(self, primary_client: instructor.AsyncInstructor, fallback_client: instructor.AsyncInstructor):
        self.primary_client = primary_client
        self.fallback_client = fallback_client

    async def generate_structured(self, response_model: type[BaseModel], messages: list[dict]) -> BaseModel:
        try:
            # Tentar Provedor Primário (Gemini 2.5 Flash / Claude 3.5 Sonnet) com Timeout de 2.5s
            return await asyncio.wait_for(
                self.primary_client.chat.completions.create(
                    response_model=response_model,
                    messages=messages,
                ),
                timeout=2.5
            )
        except (asyncio.TimeoutError, Exception) as err:
            logger.warning("Falha no provedor primário de LLM, acionando fallback", error=str(err))
            # Executar Provedor de Reserva (GPT-4o-mini / Groq Llama-3.3)
            return await self.fallback_client.chat.completions.create(
                response_model=response_model,
                messages=messages,
            )
```

---

## 4. Anti-Patterns (NUNCA faça)

```
[X] Usar re.search(r"\{.*\}", text) para extrair JSON   -> Use SEMPRE Instructor
[X] Ignorar Field(description=...) nos schemas        -> Descrições orientam a LLM
[X] Passar histórico bruto de 100 mensagens no prompt  -> Use janela deslizante (max 6-12 turnos)
[X] Não tratar exceção InstructorRetryException       -> Capture e registre no log estruturado
[X] Instanciar client de LLM em escopo de módulo       -> Injete via app.state ou dependency
```

---

## 5. Checklist de Validação

- [ ] Todos os atributos do modelo Pydantic possuem `Field(description=...)`
- [ ] O modelo herda de `pydantic.BaseModel`
- [ ] O client do Instructor usa `AsyncInstructor`
- [ ] Há limite de `max_retries=2` e tratamento de exceção
- [ ] A chamada inclui `organization_id` no log estruturado
