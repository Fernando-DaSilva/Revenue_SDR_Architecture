---
name: pytest-tenant-isolation
description: |
  Padroes de testes pytest para o Revenue SDR OS. Carregue esta skill
  sempre que for criar testes, especialmente testes de tenant isolation.
version: 1.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# pytest — Padroes do Revenue SDR OS

## Principio basico

```
Testes de tenant isolation sao CRITICOS. Multi-tenant leak = LGPD violation.
Toda feature nova TEM que ter testes de isolation.
pytest deve passar 100% antes de qualquer commit.
```

---

## Estrutura de tests

```
tests/
+-- conftest.py                 # fixtures compartilhadas
+-- test_auth.py                # auth basico
+-- test_<feature>.py           # CRUD de feature
+-- test_<feature>_isolation.py # CRITICO: tenant isolation
+-- test_themes.py              # white-label CSS
+-- test_api.py                 # health, docs, OpenAPI
```

---

## conftest.py (fixtures compartilhadas)

```python
# tests/conftest.py
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

# Config ANTES de importar app
os.environ["DATABASE_URL"] = "sqlite:///./revenue_sdr_os.db"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-chars-12345"
os.environ["APP_ENV"] = "development"

# Adiciona raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.auth.security import hash_password
from app.database import engine as app_engine
from app.main import app
from app.models.organization import Organization
from app.models.user import User


@pytest.fixture(autouse=True)
def reset_db():
    """Limpa banco antes de cada teste (isolamento total)."""
    SQLModel.metadata.drop_all(app_engine)
    SQLModel.metadata.create_all(app_engine)
    yield


@pytest.fixture
def seed_two_orgs():
    """Cria 2 orgs com 1 user cada (Org A admin + Org B admin)."""
    with Session(app_engine) as db:
        org_a = Organization(
            name="Org A",
            slug="org-a",
            theme_primary_color="#FF0000",  # vermelho
            plan="trial",
        )
        org_b = Organization(
            name="Org B",
            slug="org-b",
            theme_primary_color="#00FF00",  # verde
            plan="trial",
        )
        db.add(org_a)
        db.add(org_b)
        db.commit()
        db.refresh(org_a)
        db.refresh(org_b)

        user_a = User(
            organization_id=org_a.id,
            email="a@org-a.com",
            name="User A",
            password_hash=hash_password("senha123"),
            role="admin",
        )
        user_b = User(
            organization_id=org_b.id,
            email="b@org-b.com",
            name="User B",
            password_hash=hash_password("senha123"),
            role="admin",
        )
        db.add(user_a)
        db.add(user_b)
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)

        return org_a, org_b, user_a, user_b


@pytest.fixture
def client():
    """TestClient do FastAPI."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers_org_a(seed_two_orgs, client):
    """Headers autenticados como user da Org A."""
    org_a, org_b, user_a, user_b = seed_two_orgs
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user_a.email, "password": "senha123"},
        headers={"X-Tenant-Slug": "org-a"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {
        "X-Tenant-Slug": "org-a",
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture
def auth_headers_org_b(seed_two_orgs, client):
    """Headers autenticados como user da Org B."""
    org_a, org_b, user_a, user_b = seed_two_orgs
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user_b.email, "password": "senha123"},
        headers={"X-Tenant-Slug": "org-b"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {
        "X-Tenant-Slug": "org-b",
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture
def auth_headers_inactive_user(seed_two_orgs, client):
    """Headers de user inativo."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    # Desativa user_a
    with Session(app_engine) as db:
        u = db.get(User, user_a.id)
        u.is_active = False
        db.add(u)
        db.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": user_a.email, "password": "senha123"},
        headers={"X-Tenant-Slug": "org-a"},
    )
    # Login falha para user inativo
    return response  # response 403
```

---

## Tipos de testes

### 1. Tenant isolation (CRITICOS)

**REGRA**: para cada endpoint novo, escrever **pelo menos 5 testes de isolation**:

```python
# tests/test_<feature>_isolation.py

def test_list_<feature>_only_returns_own_org(client, seed_two_orgs, auth_headers_org_a):
    """Lista retorna APENAS do proprio tenant."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    # Setup: cria items em ambas orgs
    item_a = client.post(
        "/api/v1/<feature>",
        json={"name": "Item A"},
        headers=auth_headers_org_a,
    ).json()

    item_b = client.post(
        "/api/v1/<feature>",
        json={"name": "Item B"},
        headers=auth_headers_org_b,
    ).json()

    # Test: lista como Org A
    response = client.get("/api/v1/<feature>", headers=auth_headers_org_a)
    assert response.status_code == 200
    items = response.json()
    item_ids = [i["id"] for i in items]

    assert item_a["id"] in item_ids
    assert item_b["id"] not in item_ids  # NAO vaza


def test_get_<feature>_cross_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """GET cross-tenant retorna 404 (NAO vaza existencia)."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    item_b = client.post(
        "/api/v1/<feature>",
        json={"name": "Item B"},
        headers=auth_headers_org_b,
    ).json()

    # Tenta acessar como Org A
    response = client.get(f"/api/v1/<feature>/{item_b['id']}", headers=auth_headers_org_a)
    assert response.status_code == 404


def test_patch_<feature>_cross_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """PATCH cross-tenant NAO altera item de outro tenant."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    item_b = client.post(
        "/api/v1/<feature>",
        json={"name": "Item B", "status": "novo"},
        headers=auth_headers_org_b,
    ).json()

    # Tenta alterar como Org A
    response = client.patch(
        f"/api/v1/<feature>/{item_b['id']}",
        json={"status": "vendido"},
        headers=auth_headers_org_a,
    )
    assert response.status_code == 404

    # Item NAO foi alterado
    verify = client.get(f"/api/v1/<feature>/{item_b['id']}", headers=auth_headers_org_b)
    assert verify.json()["status"] == "novo"


def test_delete_<feature>_cross_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """DELETE cross-tenant NAO deleta item de outro tenant."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    item_b = client.post(
        "/api/v1/<feature>",
        json={"name": "Item B"},
        headers=auth_headers_org_b,
    ).json()

    response = client.delete(f"/api/v1/<feature>/{item_b['id']}", headers=auth_headers_org_a)
    assert response.status_code == 404

    # Item NAO foi deletado
    verify = client.get(f"/api/v1/<feature>/{item_b['id']}", headers=auth_headers_org_b)
    assert verify.status_code == 200


def test_create_<feature>_with_cross_tenant_<key>_does_not_merge(client, seed_two_orgs, auth_headers_org_a, auth_headers_org_b):
    """Criar com mesmo identificador em OUTRO tenant NAO faz merge."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    # Item em Org A com phone X
    item_a = client.post(
        "/api/v1/<feature>",
        json={"name": "Item A", "phone": "+5511999999999"},
        headers=auth_headers_org_a,
    ).json()

    # Item em Org B com mesmo phone
    item_b = client.post(
        "/api/v1/<feature>",
        json={"name": "Item B", "phone": "+5511999999999"},
        headers=auth_headers_org_b,
    ).json()

    # IDs diferentes
    assert item_a["id"] != item_b["id"]

    # Ambos existem isoladamente
    verify_a = client.get(f"/api/v1/<feature>/{item_a['id']}", headers=auth_headers_org_a)
    verify_b = client.get(f"/api/v1/<feature>/{item_b['id']}", headers=auth_headers_org_b)

    assert verify_a.json()["name"] == "Item A"
    assert verify_b.json() == {} or verify_b.json()["name"] == "Item B"
```

### 2. CRUD basico

```python
# tests/test_<feature>.py

def test_create_<feature>_with_minimal_data(client, auth_headers_org_a):
    """Cria <feature> com dados minimos."""
    response = client.post(
        "/api/v1/<feature>",
        json={"name": "Test"},
        headers=auth_headers_org_a,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
    assert "id" in data
    assert data["id"].startswith("<feature>_")  # prefix correto


def test_create_<feature>_with_invalid_data_returns_422(client, auth_headers_org_a):
    """Validacao Pydantic retorna 422."""
    response = client.post(
        "/api/v1/<feature>",
        json={},  # sem name (obrigatorio)
        headers=auth_headers_org_a,
    )
    assert response.status_code == 422


def test_list_<feature>_paginated(client, auth_headers_org_a):
    """Paginacao funciona."""
    # Criar 5 items
    for i in range(5):
        client.post(
            "/api/v1/<feature>",
            json={"name": f"Item {i}"},
            headers=auth_headers_org_a,
        )

    # Listar com limit=2
    response = client.get("/api/v1/<feature>?limit=2", headers=auth_headers_org_a)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Listar com skip=2
    response = client.get("/api/v1/<feature>?skip=2&limit=2", headers=auth_headers_org_a)
    assert len(response.json()) == 2


def test_get_<feature>_by_id(client, auth_headers_org_a):
    """GET por ID retorna item correto."""
    item = client.post(
        "/api/v1/<feature>",
        json={"name": "Test"},
        headers=auth_headers_org_a,
    ).json()

    response = client.get(f"/api/v1/<feature>/{item['id']}", headers=auth_headers_org_a)
    assert response.status_code == 200
    assert response.json()["id"] == item["id"]


def test_patch_<feature>_partial_update(client, auth_headers_org_a):
    """PATCH atualiza apenas campos enviados."""
    item = client.post(
        "/api/v1/<feature>",
        json={"name": "Original", "status": "novo"},
        headers=auth_headers_org_a,
    ).json()

    response = client.patch(
        f"/api/v1/<feature>/{item['id']}",
        json={"status": "atualizado"},  # so atualiza status
        headers=auth_headers_org_a,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "atualizado"
    assert data["name"] == "Original"  # NAO alterou


def test_delete_<feature>_soft_delete(client, auth_headers_org_a):
    """DELETE faz soft delete (NAO remove do banco)."""
    item = client.post(
        "/api/v1/<feature>",
        json={"name": "To Delete"},
        headers=auth_headers_org_a,
    ).json()

    response = client.delete(
        f"/api/v1/<feature>/{item['id']}",
        headers=auth_headers_org_a,
    )
    assert response.status_code == 204

    # GET retorna 404 (soft deleted)
    get_response = client.get(
        f"/api/v1/<feature>/{item['id']}",
        headers=auth_headers_org_a,
    )
    assert get_response.status_code == 404

    # Item NAO aparece em listagem
    list_response = client.get("/api/v1/<feature>", headers=auth_headers_org_a)
    item_ids = [i["id"] for i in list_response.json()]
    assert item["id"] not in item_ids
```

### 3. Auth basico

```python
# tests/test_auth.py

def test_login_with_correct_credentials(client, seed_two_orgs):
    """Login com credenciais corretas retorna token."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    response = client.post(
        "/api/v1/auth/login",
        json={"email": user_a.email, "password": "senha123"},
        headers={"X-Tenant-Slug": "org-a"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_cross_tenant_blocked(client, seed_two_orgs):
    """User de Org A NAO consegue logar via Org B."""
    org_a, org_b, user_a, user_b = seed_two_orgs

    response = client.post(
        "/api/v1/auth/login",
        json={"email": user_a.email, "password": "senha123"},
        headers={"X-Tenant-Slug": "org-b"},  # tentando via Org B
    )
    assert response.status_code == 401


def test_get_me_requires_auth(client):
    """GET /me sem token retorna 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_with_invalid_token_returns_401(client):
    """GET /me com token invalido retorna 401."""
    response = client.get(
        "/api/v1/auth/me",
        cookies={"rsdros_session": "token-invalido"},
    )
    assert response.status_code == 401
```

---

## Convencoes

### Naming

```python
# Tests descrevem o comportamento esperado
def test_<action>_<expected_result>(client, fixtures...):
    """Docstring explicando o teste."""

# Bom: "test_get_lead_cross_tenant_returns_404"
# Ruim: "test_get_lead" (vago)
```

### Docstrings

```python
def test_list_leads_only_returns_own_org(client, seed_two_orgs, auth_headers_org_a):
    """Lista de leads retorna APENAS do proprio tenant.

    Setup:
      - 2 orgs com 1 user cada
      - 1 lead em cada org

    Expected:
      - GET /leads como Org A retorna APENAS lead de Org A
      - Lead de Org B NAO aparece (NAO vaza)
    """
```

### Estrutura AAA (Arrange-Act-Assert)

```python
def test_patch_lead_partial_update(client, auth_headers_org_a):
    # Arrange: setup
    item = client.post(
        "/api/v1/leads",
        json={"name": "Original", "status": "novo"},
        headers=auth_headers_org_a,
    ).json()

    # Act: executar acao
    response = client.patch(
        f"/api/v1/leads/{item['id']}",
        json={"status": "atualizado"},
        headers=auth_headers_org_a,
    )

    # Assert: verificar resultado
    assert response.status_code == 200
    assert response.json()["status"] == "atualizado"
    assert response.json()["name"] == "Original"  # NAO alterou
```

---

## Rodar testes

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate

# Roda tudo
pytest -v

# Roda so tenant isolation de leads
pytest tests/test_lead_isolation.py -v

# Roda um teste especifico
pytest tests/test_leads.py::test_create_lead_with_minimal_data -v

# Com coverage
pytest --cov=app --cov-report=term-missing tests/

# Stop no primeiro erro
pytest -x -v
```

---

## Anti-patterns (NUNCA faca)

```python
# ERRADO: usar sqlite em memoria (nao testa migrations)
@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    # ... problema: migrations nao sao testadas


# ERRADO: nao testar cross-tenant
def test_create_lead(client, auth_headers_org_a):
    # so testa happy path, NAO testa isolation
    response = client.post("/api/v1/leads", json={...})
    assert response.status_code == 201
# FALTA: test_create_lead_with_cross_tenant_phone_does_not_merge


# ERRADO: hardcoded IDs
def test_get_lead(client):
    response = client.get("/api/v1/leads/lead_abc123")  # ID hardcoded!
    assert response.status_code == 200


# ERRADO: setup fragil
def test_X(client):
    # Assume que tem um lead com ID "X" no banco
    # Mas teste roda isolado, NAO tem esse lead!
    response = client.get("/api/v1/leads/X")
    assert response.status_code == 200  # falha
```

---

## Checklist

```
[ ] Reset DB antes de cada teste (autouse fixture)
[ ] Fixtures seed_two_orgs, auth_headers_org_a/b funcionais
[ ] Cada endpoint novo tem >= 5 testes de tenant isolation
[ ] Cada endpoint tem >= 3 testes de CRUD basico
[ ] Tests usam AAA (Arrange-Act-Assert)
[ ] Docstrings explicam o teste
[ ] Sem IDs hardcoded (sempre criar no setup)
[ ] pytest -v passa 100% antes de commit
[ ] Coverage > 80% em app/
[ ] tests/test_<feature>_isolation.py para cada feature
```

---

*"Tenant isolation test is the cheapest insurance you can buy."*