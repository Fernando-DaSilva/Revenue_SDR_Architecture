---
sprint: 02
task: 03-create-merge-service
---

# Prompt 02.03 — Lead Merge (deteccao de duplicatas + merge conservador)

> Spec da task T3 da Sprint 02. Logica central do Lead Brain.

---

## Skills a carregar

```
1. .skills/revenue-sdr-os-architect.md
2. .skills/fastapi-multi-tenant.md
3. .skills/pytest-tenant-isolation.md
```

---

## Contexto

Models prontos (`app/leads/models.py`). Agora implementar a logica de
**Lead Brain**: ao criar lead com telefone/email que ja existe no MESMO
tenant, nao duplicar — fazer merge conservador no lead existente.

Arquivo: `app/leads/merge.py` (pacote do dominio, NAO `app/services/`).

---

## Regras de negocio (DECISAO D1 — confirmar com o usuario antes)

Proposta vigente (default desta spec):

1. **Match exato** por telefone normalizado OU email normalizado
   (lowercase/trim), dentro do tenant, ignorando `status='deletado'`.
2. **Merge conservador**: preenche SOMENTE campos vazios do lead
   existente (nunca sobrescreve dado ja preenchido).
3. **Auditavel**: registra `LeadTimelineEvent(event_type='merged')` com
   payload `{source_lead_data, matched_by}` e atualiza
   `last_interaction_at`.
4. **Retorna o lead existente** unificado (a API sinaliza que houve
   merge — ver T4: header `X-Merged: true` ou campo na resposta).

Alternativa (se o usuario escolher): `409 Conflict` com o candidato e
endpoint explicito `POST /leads/{id}/merge`. Nao implementar as duas.

---

## Implementacao de referencia

```python
"""
Lead Merge — Lead Brain.

Deteccao de duplicatas por telefone/email dentro do tenant e merge
CONSERVADOR: so preenche campos vazios, nunca sobrescreve.
Toda operacao e auditada na timeline do lead.
"""

from sqlmodel import Session, or_, select

from app.db.base import utc_now
from app.leads.models import Lead, LeadEventType, LeadStatus, LeadTimelineEvent


def normalize_phone(phone: str | None) -> str | None:
    """Mantem so digitos e '+'. None/vazio -> None."""
    if not phone:
        return None
    digits = "".join(c for c in phone if c.isdigit() or c == "+")
    return digits or None


def normalize_email(email: str | None) -> str | None:
    """Lowercase + strip. None/vazio -> None."""
    if not email:
        return None
    normalized = email.strip().lower()
    return normalized or None


class LeadMerger:
    def __init__(self, session: Session):
        self.session = session

    def find_duplicate(
        self,
        *,
        organization_id: str,
        phone: str | None = None,
        email: str | None = None,
        exclude_lead_id: str | None = None,
    ) -> Lead | None:
        """Busca duplicata ativa no tenant por telefone OU email normalizados."""
        phone = normalize_phone(phone)
        email = normalize_email(email)
        conditions = []
        if phone:
            conditions.append(Lead.phone == phone)
        if email:
            conditions.append(Lead.email == email)
        if not conditions:
            return None

        statement = select(Lead).where(
            Lead.organization_id == organization_id,
            Lead.status != LeadStatus.DELETADO,
            or_(*conditions),
        )
        if exclude_lead_id:
            statement = statement.where(Lead.id != exclude_lead_id)
        return self.session.exec(statement).first()

    def merge_into(self, *, existing: Lead, incoming: Lead) -> Lead:
        """
        Merge conservador de `incoming` em `existing`.
        Preenche so campos vazios; registra evento 'merged'.
        """
        mergeable = [
            "name", "phone", "email", "document",
            "source", "assigned_user_id",
        ]
        filled: dict[str, object] = {}
        for field in mergeable:
            current = getattr(existing, field)
            new_value = getattr(incoming, field)
            if (current is None or current == "") and new_value:
                setattr(existing, field, new_value)
                filled[field] = new_value

        # tags: uniao sem duplicar
        new_tags = [t for t in incoming.tags if t not in existing.tags]
        if new_tags:
            existing.tags = [*existing.tags, *new_tags]
            filled["tags_added"] = new_tags

        # custom_fields: so chaves ausentes
        new_keys = {k: v for k, v in incoming.custom_fields.items()
                    if k not in existing.custom_fields}
        if new_keys:
            existing.custom_fields = {**existing.custom_fields, **new_keys}
            filled["custom_fields_added"] = list(new_keys)

        existing.last_interaction_at = utc_now()
        self.session.add(existing)

        event = LeadTimelineEvent(
            organization_id=existing.organization_id,
            lead_id=existing.id,
            event_type=LeadEventType.MERGED,
            payload={
                "matched_by": "phone_or_email",
                "incoming_source": incoming.source,
                "filled_fields": filled,
            },
            actor_user_id=None,  # sistema
        )
        self.session.add(event)
        self.session.commit()
        self.session.refresh(existing)
        return existing
```

---

## Cenarios de teste (tests/test_leads_merge.py)

```
[ ] Criar lead com telefone duplicado (mesmo tenant) -> merge, nao duplica
[ ] Match por email duplicado -> merge
[ ] Telefone com formatacao diferente ("+55 11 9..." vs "55119...") -> match
[ ] Merge NAO sobrescreve campos preenchidos (conservador)
[ ] Merge preenche campos vazios (email/document ausentes)
[ ] Merge faz uniao de tags sem duplicar
[ ] Evento 'merged' registrado na timeline com payload correto
[ ] Mesmo telefone em tenant DIFERENTE -> cria lead novo (sem merge)
[ ] Telefone duplicado em lead 'deletado' -> cria novo (nao revive)
[ ] exclude_lead_id impede match consigo mesmo (para updates futuros)
```

## Checklist

```
[ ] app/leads/merge.py com LeadMerger + normalizadores
[ ] Match so dentro do tenant (organization_id na query)
[ ] Ignora leads 'deletado'
[ ] Merge conservador + uniao de tags/custom_fields
[ ] Evento 'merged' na timeline (append-only)
[ ] 10+ cenarios de teste passando
[ ] ruff limpo
```

---

*"Um lead, uma pessoa — nao importa de onde ele venha."*
