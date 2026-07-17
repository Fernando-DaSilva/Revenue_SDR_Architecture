---
sprint: 02
task: 03-create-merge-service
---

# Prompt 02.03 — Criar Lead Merge Service

> **Copy-paste este prompt inteiro pra um agente de IA.**

---

## Skills a carregar

```
1. .skills/revenue-sdr-os-architect.md
2. .skills/fastapi-multi-tenant.md
3. .skills/pytest-tenant-isolation.md
```

---

## Contexto

Ja existem os models Lead, LeadMemory, LeadTimelineEvent.
Agora voce precisa implementar a **logica de Lead Brain**: detectar leads duplicados e fazer merge automatico.

Repo: `~/AGENCIA/SDR/`

---

## Objetivo

Quando alguem tenta criar um lead com telefone/email que ja existe no mesmo tenant, o sistema:
1. Detecta a duplicata
2. Faz merge automatico (preenche dados faltantes no lead existente)
3. Loga evento de merge no timeline
4. Retorna o lead existente (unificado)

---

## Tasks

### T1: Criar `app/services/__init__.py`

```python
"""Business logic services."""
```

### T2: Criar `app/services/lead_merge.py`

```python
"""
Lead Merge Service — Lead Brain.

Detecta leads duplicados (mesmo telefone/email no mesmo tenant)
e faz merge automatico.
"""
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select, or_

from app.models.lead import Lead, LeadTimelineEvent, _new_event_id


def find_existing_lead(
    db: Session,
    organization_id: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    exclude_lead_id: Optional[str] = None,
) -> Optional[Lead]:
    """
    Busca lead existente no mesmo tenant por telefone OU email.

    Args:
        db: Sessao do banco
        organization_id: Tenant
        phone: Telefone normalizado (com codigo pais)
        email: Email normalizado (lowercase)
        exclude_lead_id: Ignorar este lead (usado em updates)

    Returns:
        Lead encontrado ou None
    """
    if not phone and not email:
        return None

    conditions = []
    if phone:
        conditions.append(Lead.phone == phone)
    if email:
        conditions.append(Lead.email == email.lower().strip() if email else None)

    if not conditions:
        return None

    statement = select(Lead).where(
        Lead.organization_id == organization_id,
        Lead.status != "deletado",  # NAO merge com deletados
        or_(*conditions),
    )
    if exclude_lead_id:
        statement = statement.where(Lead.id != exclude_lead_id)

    return db.exec(statement).first()


def merge_lead_data(existing: Lead, new_data: dict) -> Lead:
    """
    Faz merge de dados novos no lead existente.
    Preenche apenas campos vazios (NAO sobrescreve dados existentes).

    Returns:
        Lead atualizado
    """
    updated = False
    for field, new_value in new_data.items():
        if not hasattr(existing, field):
            continue

        current_value = getattr(existing, field)
        # Preenche apenas se current for None/vazio
        if current_value is None or current_value == "":
            setattr(existing, field, new_value)
            updated = True
        # Caso especial: source_detail (JSON) — merge keys
        elif field == "source_detail" and new_value and current_value == "{}":
            setattr(existing, field, new_value)
            updated = True

    if updated:
        existing.updated_at = datetime.utcnow()
        existing.last_interaction_at = datetime.utcnow()

    return existing


def log_merge_event(
    db: Session,
    organization_id: str,
    existing_lead_id: str,
    new_lead_id: str,
    merged_fields: list[str],
    actor_user_id: Optional[str] = None,
) -> LeadTimelineEvent:
    """Loga evento de merge no timeline do lead existente."""
    import json

    event = LeadTimelineEvent(
        id=_new_event_id(),
        organization_id=organization_id,
        lead_id=existing_lead_id,
        event_type="merged",
        payload=json.dumps({
            "merged_with": new_lead_id,
            "merged_fields": merged_fields,
        }),
        actor_user_id=actor_user_id,
    )
    db.add(event)
    return event
```

### T3: Testar manualmente

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate

python << 'EOF'
from sqlmodel import Session
from app.database import engine
from app.services.lead_merge import find_existing_lead, merge_lead_data
from app.models import Organization, Lead

# Setup
with Session(engine) as db:
    # Pega Org A
    org = db.exec(select(Organization).where(Organization.slug == "clinica-bela")).first()
    print(f"Org: {org.name}")

    # Busca lead existente por telefone
    existing = find_existing_lead(db, organization_id=org.id, phone="+5511999999999")
    print(f"Found: {existing}")
EOF
```

---

## Criterios de aceitacao

```python
# Em test_lead_merge.py

def test_find_by_phone_returns_existing():
    """Lead com mesmo telefone no mesmo tenant e' encontrado."""
    # Criar org + lead + buscar por telefone → retorna o lead

def test_find_by_email_returns_existing():
    """Lead com mesmo email no mesmo tenant e' encontrado."""
    # Criar org + lead + buscar por email → retorna o lead

def test_find_returns_none_when_no_match():
    """Lead com telefone/email diferente NAO e' encontrado."""

def test_find_excludes_deleted_leads():
    """Leads com status='deletado' NAO sao encontrados para merge."""

def test_find_excludes_self_when_updating():
    """Ao atualizar lead X, NAO retorna X mesmo como match."""

def test_find_only_same_tenant():
    """Lead com mesmo telefone em OUTRO tenant NAO e' encontrado."""

def test_merge_fills_empty_fields():
    """Merge preenche apenas campos vazios, NAO sobrescreve."""

def test_merge_updates_timestamp():
    """Merge atualiza updated_at e last_interaction_at."""

def test_log_merge_creates_event():
    """Log cria evento de timeline com merged_with e merged_fields."""
```

---

## Checklist

```
[ ] app/services/__init__.py criado
[ ] app/services/lead_merge.py criado com 3 funcoes
[ ] find_existing_lead filtra por tenant e exclui deletados
[ ] merge_lead_data NAO sobrescreve campos existentes
[ ] log_merge_event cria evento de timeline com payload JSON
[ ] Testes em tests/test_lead_merge.py cobrem todos cenarios
[ ] pytest tests/test_lead_merge.py -v passa
[ ] Multi-tenant test: lead de outro tenant NAO e' encontrado
[ ] Codigo segue patterns das skills
```

---

*"Merge inteligente e' a alma do Lead Brain."*