---
sprint: 02
task: 05-create-memories-api
---

# Prompt 02.05 — API de Memories (Memory Brain)

> Spec da task T8 da Sprint 02.
> Padroes: `.skills/fastapi-multi-tenant.md` (v2.0).

---

## Contexto

Leads API pronta (T4-T7). Agora o CRUD de memories de um lead —
sub-recurso de `/api/v1/leads/{lead_id}/memories`.

Arquivos: schemas em `app/leads/schemas.py`, regras em
`app/leads/service.py` (`MemoryService`) ou `app/leads/memories_service.py`,
rotas em `app/leads/api.py` (mesmo router de leads — sub-recurso).

---

## Schemas

```python
class MemoryCreate(BaseModel):
    category: MemoryCategory                 # enum validado
    key: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=10000)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: MemorySource = MemorySource.MANUAL

class MemoryUpdate(BaseModel):
    category: MemoryCategory | None = None
    key: str | None = Field(default=None, min_length=1, max_length=100)
    value: str | None = Field(default=None, min_length=1, max_length=10000)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

class MemoryResponse(BaseModel):
    id: str
    lead_id: str
    organization_id: str
    category: str
    key: str
    value: str
    confidence: float
    source: str
    created_at: datetime
    updated_at: datetime
```

## Endpoints (sub-recurso de leads)

| Metodo | Path | Descricao | Notas |
|---|---|---|---|
| GET | `/api/v1/leads/{lead_id}/memories` | Lista memories do lead | `?category=`; `Page[MemoryResponse]`; lead resolvido no tenant (404 cross-tenant) |
| POST | `/api/v1/leads/{lead_id}/memories` | Adiciona memory | 201; evento `memory_added` na timeline do lead; atualiza `last_interaction_at` do lead |
| PATCH | `/api/v1/leads/{lead_id}/memories/{mem_id}` | Atualiza memory | 404 se memory nao e do lead |
| DELETE | `/api/v1/leads/{lead_id}/memories/{mem_id}` | Remove memory | hard delete OK aqui (memory nao e entidade LGPD-raiz); OU soft — decidir e documentar |

Regras:
- **Cadeia de tenant**: memory.lead_id == lead_id da URL E
  lead.organization_id == org do contexto. Quebra = 404 generico.
- `confidence`: 1.0 = humano explicitou; < 1.0 = IA detectou (Sprint 4).
- `source`: `manual` default nesta sprint; `conversation_detected` sera
  usado pelo Memory Extractor (placeholder T4, sem IA real ainda).

## Memory Extractor (PLACEHOLDER — sem IA nesta sprint)

`app/leads/memory_extractor.py`: interface estavel para a Sprint 4.

```python
def extract_from_text(text: str) -> list[MemoryCandidate]:
    """
    Placeholder rule-based (regex de datas/valores simples).
    Sprint 4 substitui por LLM. Retorna candidatos com confidence < 1.0.
    """
```

## Validacao

```bash
curl -X POST localhost:8000/api/v1/leads/{lead_id}/memories \
  -H "X-Tenant-Slug: clinica-bela" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category":"financial","key":"dia_salario","value":"dia 5"}'

curl "localhost:8000/api/v1/leads/{lead_id}/memories?category=financial" \
  -H "X-Tenant-Slug: clinica-bela" -H "Authorization: Bearer $TOKEN"

curl localhost:8000/api/v1/leads/{lead_id}/timeline ...  # contem memory_added
```

## Checklist

```
[ ] Cadeia de tenant validada (memory pertence ao lead do tenant)
[ ] Evento memory_added na timeline + last_interaction_at do lead
[ ] confidence entre 0.0 e 1.0 (schema)
[ ] Filtro ?category= funcional
[ ] 404 generico em qualquer quebra da cadeia (lead/mem/tenant)
[ ] Memory extractor placeholder com interface estavel
[ ] Testes: CRUD + cadeia cross-tenant + evento na timeline
[ ] ruff limpo
```
