---
sprint: 02
task: 04-create-leads-api
---

# Prompt 02.04 — API de Leads (CRUD + timeline)

> Spec das tasks T4-T7 da Sprint 02.
> Padroes de rota/service/schema: `.skills/fastapi-multi-tenant.md` (v2.0).

---

## Contexto

Models (T1) e merge (T3) prontos. Criar o pacote de API + service de
leads: `app/leads/service.py`, `app/leads/schemas.py`, `app/leads/api.py`.
Registrar o router no agregador `app/api/__init__.py`.

---

## Schemas (`app/leads/schemas.py`) — VALIDACAO vive aqui

```python
class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    document: str | None = Field(default=None, max_length=50)
    source: LeadSource                       # enum validado
    source_detail: dict = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list, max_length=50)
    custom_fields: dict = Field(default_factory=dict)
    assigned_user_id: str | None = None
    # NUNCA organization_id aqui — vem do contexto

class LeadUpdate(BaseModel):                 # todos opcionais (PATCH)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    phone: str | None = None
    email: EmailStr | None = None
    document: str | None = None
    source: LeadSource | None = None
    status: LeadStatus | None = None
    tags: list[str] | None = None
    custom_fields: dict | None = None
    assigned_user_id: str | None = None

class LeadResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    phone: str | None
    email: str | None
    document: str | None
    source: str
    status: str
    tags: list[str]
    custom_fields: dict
    assigned_user_id: str | None
    last_interaction_at: datetime | None
    created_at: datetime
    updated_at: datetime
    merged: bool = False                     # True quando POST resultou em merge

class TimelineEventResponse(BaseModel):
    id: str
    event_type: str
    payload: dict
    actor_user_id: str | None
    created_at: datetime
```

## Endpoints (`app/leads/api.py` — `/api/v1/leads`)

| Metodo | Path | Descricao | Notas |
|---|---|---|---|
| GET | `""` | Lista paginada + busca | `Page[LeadResponse]`; `?q=` filtra name/phone/email (ILIKE); `?status=`; nunca retorna `deletado` |
| POST | `""` | Cria lead | 201; se duplicata -> `LeadMerger.merge_into` + `merged=true` na resposta; evento `created` ou `merged` na timeline |
| GET | `/{lead_id}` | Detalhe | 404 generico cross-tenant |
| PATCH | `/{lead_id}` | Atualiza | evento `updated` (+ `status_changed` se mudou status) na timeline |
| DELETE | `/{lead_id}` | Soft delete | `status='deletado'`; idempotente (segundo DELETE = 404); evento na timeline |
| GET | `/{lead_id}/timeline` | Timeline | `Page[TimelineEventResponse]` ordenado por `created_at` desc |

Regras:
- Rota fina -> `LeadService` (`app/leads/service.py`) -> models
- `organization_id` SEMPRE de `CurrentOrganization`; user de `CurrentUser`
- Erros: `NotFoundError` (404/cross-tenant), `ConflictError` se necessario
- `last_interaction_at` atualiza em create/merge/update
- `actor_user_id = user.id` nos eventos gerados por acao humana

## Service (`app/leads/service.py`)

```python
class LeadService:
    def __init__(self, session: Session): ...

    def create(self, *, organization_id, data: LeadCreate, actor_user_id) -> tuple[Lead, bool]:
        """Retorna (lead, merged). Usa LeadMerger antes de inserir."""

    def get_in_organization(self, *, organization_id, lead_id) -> Lead | None: ...
    def list_in_organization(self, *, organization_id, q, status, offset, limit) -> tuple[list[Lead], int]: ...
    def update(self, *, lead, data: LeadUpdate, actor_user_id) -> Lead: ...
    def soft_delete(self, *, lead, actor_user_id) -> None: ...
    def timeline(self, *, lead_id, offset, limit) -> tuple[list[LeadTimelineEvent], int]: ...
    def _log_event(self, *, lead, event_type, payload, actor_user_id) -> None: ...
```

## Validacao

```bash
curl -X POST localhost:8000/api/v1/leads -H "X-Tenant-Slug: clinica-bela" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Joao Silva","phone":"+5511999990001","source":"whatsapp"}'

curl "localhost:8000/api/v1/leads?q=joao&status=novo" -H "X-Tenant-Slug: clinica-bela" -H "Authorization: Bearer $TOKEN"
curl localhost:8000/api/v1/leads/{id}/timeline -H "X-Tenant-Slug: clinica-bela" -H "Authorization: Bearer $TOKEN"
# Duplicata: repetir o POST com mesmo telefone -> merged=true, mesmo id
```

## Checklist

```
[ ] Schemas com validacao (EmailStr, enums, tamanhos)
[ ] Toda query filtra organization_id; deletados fora das listagens
[ ] POST com duplicata faz merge (merged=true) — sem duplicar
[ ] Eventos na timeline: created, updated, status_changed, merged, deleted
[ ] Paginacao Page/PageParams em list e timeline
[ ] Busca ?q= em name/phone/email (escapar %/_ do ILIKE)
[ ] 404 generico cross-tenant em get/patch/delete
[ ] Router registrado em app/api/__init__.py; /docs mostra endpoints
[ ] ruff limpo
```
