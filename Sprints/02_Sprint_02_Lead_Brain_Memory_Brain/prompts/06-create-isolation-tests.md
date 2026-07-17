---
sprint: 02
task: 06-create-isolation-tests
---

# Prompt 02.06 — Criar Testes de Tenant Isolation (CRITICO)

> **Copy-paste este prompt inteiro pra um agente de IA.**

---

## Skills a carregar

```
1. .skills/revenue-sdr-os-architect.md
2. .skills/pytest-tenant-isolation.md
```

---

## Contexto

Ja existem:
- Models: Lead, LeadMemory, LeadTimelineEvent
- APIs: /leads, /leads/{id}/memories
- Service: lead_merge
- conftest.py com fixtures (seed_two_orgs, auth_headers_org_a, auth_headers_org_b, client)

Voce precisa criar testes que **garantem que dados de uma org NAO vazem pra outra**.

Repo: `~/AGENCIA/SDR/`

---

## Tasks

### T1: Criar `tests/test_lead_isolation.py`

```python
"""
Testes CRITICOS de tenant isolation para Leads.

GARANTE:
  - Lead de Org A NAO aparece em queries de Org B
  - Cross-tenant GET /leads/{id} retorna 404
  - Cross-tenant POST /leads nao faz merge com lead de outro tenant
  - Memories de lead de outro tenant NAO sao acessiveis
  - Timeline de lead de outro tenant NAO e' acessivel
"""
import pytest
from sqlmodel import Session

from app.database import engine as app_engine
from app.models.lead import Lead, LeadMemory, LeadTimelineEvent
from app.models.organization import Organization


# --- Leads API ---

def test_list_leads_only_returns_own_org(client, seed_two_orgs, auth_headers_org_a):
    """Lista de leads retorna APENAS do proprio tenant."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    # Cria 1 lead em cada org
    response_a = client.post(
        "/api/v1/leads",
        json={"name": "Lead A", "phone": "+5511111111111", "source": "whatsapp"},
        headers=auth_headers_org_a,
    )
    assert response_a.status_code == 201
    lead_a_id = response_a.json()["id"]

    response_b = client.post(
        "/api/v1/leads",
        json={"name": "Lead B", "phone": "+5511222222222", "source": "whatsapp"},
        headers=auth_headers_org_b,
    )
    assert response_b.status_code == 201
    lead_b_id = response_b.json()["id"]

    # Lista como Org A
    response = client.get("/api/v1/leads", headers=auth_headers_org_a)
    assert response.status_code == 200
    leads = response.json()
    lead_ids = [l["id"] for l in leads]

    # So Lead A aparece
    assert lead_a_id in lead_ids
    assert lead_b_id not in lead_ids


def test_get_lead_cross_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """GET lead de outro tenant retorna 404 (NAO vaza existencia)."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    # Cria lead em Org B
    response_b = client.post(
        "/api/v1/leads",
        json={"name": "Lead B Secret", "phone": "+5511333333333", "source": "whatsapp"},
        headers=auth_headers_org_b,
    )
    lead_b_id = response_b.json()["id"]

    # Tenta acessar como Org A
    response = client.get(f"/api/v1/leads/{lead_b_id}", headers=auth_headers_org_a)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_patch_lead_cross_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """PATCH cross-tenant retorna 404."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    response_b = client.post(
        "/api/v1/leads",
        json={"name": "Lead B", "phone": "+5511444444444", "source": "whatsapp"},
        headers=auth_headers_org_b,
    )
    lead_b_id = response_b.json()["id"]

    # Tenta atualizar como Org A
    response = client.patch(
        f"/api/v1/leads/{lead_b_id}",
        json={"status": "venda"},  # tentar marcar como vendido
        headers=auth_headers_org_a,
    )
    assert response.status_code == 404

    # Lead B NAO foi alterado
    response_b_verify = client.get(f"/api/v1/leads/{lead_b_id}", headers=auth_headers_org_b)
    assert response_b_verify.json()["status"] == "novo"


def test_delete_lead_cross_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """DELETE cross-tenant retorna 404 (NAO deleta lead de outro tenant)."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    response_b = client.post(
        "/api/v1/leads",
        json={"name": "Lead B", "phone": "+5511555555555", "source": "whatsapp"},
        headers=auth_headers_org_b,
    )
    lead_b_id = response_b.json()["id"]

    # Tenta deletar como Org A
    response = client.delete(f"/api/v1/leads/{lead_b_id}", headers=auth_headers_org_a)
    assert response.status_code == 404

    # Lead B NAO foi deletado
    response_b_verify = client.get(f"/api/v1/leads/{lead_b_id}", headers=auth_headers_org_b)
    assert response_b_verify.status_code == 200


def test_create_lead_with_cross_tenant_phone_does_not_merge(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """Criar lead com telefone de OUTRO tenant NAO faz merge (cria duplicado)."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    # Lead em Org A com telefone X
    response_a = client.post(
        "/api/v1/leads",
        json={"name": "Lead A1", "phone": "+5511666666666", "source": "whatsapp"},
        headers=auth_headers_org_a,
    )
    lead_a_id = response_a.json()["id"]

    # Tentar criar lead em Org B com MESMO telefone X
    # Deve criar NOVO lead (NAO merge com Org A)
    response_b = client.post(
        "/api/v1/leads",
        json={"name": "Lead B1", "phone": "+5511666666666", "source": "site"},
        headers=auth_headers_org_b,
    )
    assert response_b.status_code == 201

    lead_b_id = response_b.json()["id"]

    # IDs devem ser diferentes
    assert lead_a_id != lead_b_id

    # Ambos existem isoladamente
    verify_a = client.get(f"/api/v1/leads/{lead_a_id}", headers=auth_headers_org_a)
    verify_b = client.get(f"/api/v1/leads/{lead_b_id}", headers=auth_headers_org_b)

    assert verify_a.json()["name"] == "Lead A1"
    assert verify_b.json()["name"] == "Lead B1"


# --- Memories API ---

def test_list_memories_cross_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """GET memories de lead de outro tenant retorna 404."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    # Lead + memory em Org B
    lead_b_response = client.post(
        "/api/v1/leads",
        json={"name": "Lead B", "phone": "+5511777777777", "source": "whatsapp"},
        headers=auth_headers_org_b,
    )
    lead_b_id = lead_b_response.json()["id"]

    client.post(
        f"/api/v1/leads/{lead_b_id}/memories",
        json={"category": "personal", "key": "test", "value": "secret"},
        headers=auth_headers_org_b,
    )

    # Tenta listar memories como Org A
    response = client.get(
        f"/api/v1/leads/{lead_b_id}/memories",
        headers=auth_headers_org_a,
    )
    assert response.status_code == 404


def test_create_memory_cross_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """POST memory em lead de outro tenant retorna 404."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    lead_b_response = client.post(
        "/api/v1/leads",
        json={"name": "Lead B", "phone": "+5511888888888", "source": "whatsapp"},
        headers=auth_headers_org_b,
    )
    lead_b_id = lead_b_response.json()["id"]

    # Tenta adicionar memory como Org A
    response = client.post(
        f"/api/v1/leads/{lead_b_id}/memories",
        json={"category": "personal", "key": "hack", "value": "injection"},
        headers=auth_headers_org_a,
    )
    assert response.status_code == 404

    # NAO criou memory
    verify = client.get(
        f"/api/v1/leads/{lead_b_id}/memories",
        headers=auth_headers_org_b,
    )
    memories = verify.json()
    assert len(memories) == 0  # nenhuma memory


def test_update_memory_cross_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """PATCH memory cross-tenant retorna 404."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    # Lead + memory em Org B
    lead_b = client.post(
        "/api/v1/leads",
        json={"name": "Lead B", "phone": "+5511999990000", "source": "whatsapp"},
        headers=auth_headers_org_b,
    ).json()

    mem_b = client.post(
        f"/api/v1/leads/{lead_b['id']}/memories",
        json={"category": "personal", "key": "test", "value": "original"},
        headers=auth_headers_org_b,
    ).json()

    # Tenta atualizar como Org A
    response = client.patch(
        f"/api/v1/leads/{lead_b['id']}/memories/{mem_b['id']}",
        json={"value": "tampered"},
        headers=auth_headers_org_a,
    )
    assert response.status_code == 404

    # Value NAO foi alterado
    verify = client.get(
        f"/api/v1/leads/{lead_b['id']}/memories",
        headers=auth_headers_org_b,
    )
    assert verify.json()[0]["value"] == "original"


# --- Timeline API ---

def test_timeline_cross_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """GET timeline de lead de outro tenant retorna 404."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    lead_b = client.post(
        "/api/v1/leads",
        json={"name": "Lead B", "phone": "+5511999991111", "source": "whatsapp"},
        headers=auth_headers_org_b,
    ).json()

    # Tenta acessar timeline como Org A
    response = client.get(
        f"/api/v1/leads/{lead_b['id']}/timeline",
        headers=auth_headers_org_a,
    )
    assert response.status_code == 404


# --- Lead Merge isolation ---

def test_merge_does_not_cross_tenants(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """Lead Merge Service NAO merge entre tenants diferentes."""
    from app.services.lead_merge import find_existing_lead

    org_a, org_b, user_a, user_b = seed_two_orgs

    # Cria leads em ambas orgs com mesmo telefone
    lead_a = client.post(
        "/api/v1/leads",
        json={"name": "Joao A", "phone": "+5511999992222", "source": "whatsapp"},
        headers=auth_headers_org_a,
    ).json()

    lead_b = client.post(
        "/api/v1/leads",
        json={"name": "Joao B", "phone": "+5511999992222", "source": "site"},
        headers=auth_headers_org_b,
    ).json()

    # Service NAO deve encontrar cross-tenant
    with Session(app_engine) as db:
        found = find_existing_lead(
            db,
            organization_id=org_a.id,
            phone="+5511999992222",
        )
        assert found is not None
        assert found.id == lead_a["id"]
        assert found.organization_id == org_a.id  # NAO org_b

        # Inverso
        found_b = find_existing_lead(
            db,
            organization_id=org_b.id,
            phone="+5511999992222",
        )
        assert found_b is not None
        assert found_b.id == lead_b["id"]
        assert found_b.organization_id == org_b.id


# --- Soft delete isolation ---

def test_soft_deleted_lead_not_in_lists(client, seed_two_orgs, auth_headers_org_a):
    """Lead com status='deletado' NAO aparece em listagens."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    # Cria e deleta
    lead = client.post(
        "/api/v1/leads",
        json={"name": "To Delete", "phone": "+5511999993333", "source": "whatsapp"},
        headers=auth_headers_org_a,
    ).json()

    client.delete(f"/api/v1/leads/{lead['id']}", headers=auth_headers_org_a)

    # NAO aparece em listagem
    response = client.get("/api/v1/leads", headers=auth_headers_org_a)
    lead_ids = [l["id"] for l in response.json()]
    assert lead["id"] not in lead_ids

    # GET direto retorna 404
    get_response = client.get(f"/api/v1/leads/{lead['id']}", headers=auth_headers_org_a)
    assert get_response.status_code == 404
```

### T2: Validacao

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate

# Roda so os testes de isolation de leads
pytest tests/test_lead_isolation.py -v

# Esperado: TODOS passam

# Roda TODOS os testes
pytest -v

# Esperado: 
# - Sprint 1 tests que ja passavam continuam passando
# - Novos tests de Lead isolation passam
# - Nenhum test regrediu
```

---

## Checklist (TODOS DEVEM SER [x])

```
[ ] test_list_leads_only_returns_own_org
[ ] test_get_lead_cross_tenant_returns_404
[ ] test_patch_lead_cross_tenant_returns_404
[ ] test_delete_lead_cross_tenant_returns_404
[ ] test_create_lead_with_cross_tenant_phone_does_not_merge
[ ] test_list_memories_cross_tenant_returns_404
[ ] test_create_memory_cross_tenant_returns_404
[ ] test_update_memory_cross_tenant_returns_404
[ ] test_timeline_cross_tenant_returns_404
[ ] test_merge_does_not_cross_tenants
[ ] test_soft_deleted_lead_not_in_lists

[ ] pytest tests/test_lead_isolation.py -v passa 100%
[ ] pytest -v passa (nenhum test regrediu)
[ ] Nenhum test tem cross-tenant leak
```

---

*"Tenant isolation NAO e' feature — e' requisito basico."*