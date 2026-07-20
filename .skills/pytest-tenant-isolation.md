---
name: pytest-tenant-isolation
description: |
  Padroes de testes pytest para o Revenue SDR OS. Carregue esta skill
  sempre que for criar testes, especialmente testes de tenant isolation.
version: 2.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# pytest — Padroes do Revenue SDR OS (v2.0)

## Principio basico

```
Testes de tenant isolation sao CRITICOS. Multi-tenant leak = LGPD violation.
Toda feature nova TEM teste de isolamento cross-tenant.
pytest 100% verde antes de qualquer commit.

REGRA DE OURO: testes NUNCA tocam o banco de desenvolvimento.
Cada teste sobe uma app nova com SQLite EM MEMORIA (StaticPool).
```

---

## Por que este padrao (licao da v0.1.0)

A v0.1.0 fazia `os.environ["DATABASE_URL"] = "...revenue_sdr_os.db"` no
conftest e `drop_all/create_all` no engine global — **apagava o banco de
dev a cada run** e ainda mascarava bugs de auth. O padrao abaixo elimina
isso: a engine e injetada na app factory, isolada por teste.

## conftest.py (padrao vigente — tests/conftest.py)

```python
"""Fixtures: app isolada por teste, banco SQLite em memoria."""
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session

from app.core.config import Settings
from app.core.security import hash_password
from app.db.engine import create_db_engine
from app.main import create_app
from app.organizations.models import Organization
from app.users.models import Role, User

TEST_SECRET_KEY = "test-secret-key-with-at-least-32-characters"
TEST_PASSWORD = "senha123"


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(
        secret_key=TEST_SECRET_KEY,
        database_url="sqlite://",
        app_env="development",
        default_tenant_slug=None,
    )


@pytest.fixture()
def db_engine():
    """SQLite em memoria (StaticPool), fresco por teste."""
    engine = create_db_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def session(db_engine):
    with Session(db_engine) as s:
        yield s


@pytest.fixture()
def app(settings, db_engine):
    """App da factory com a engine de teste INJETADA."""
    return create_app(settings, db_engine=db_engine)


@pytest.fixture()
def client(app):
    with TestClient(app) as c:   # lifespan roda -> app.state.db_engine pronto
        yield c


@pytest.fixture()
def seed_two_orgs(session) -> SimpleNamespace:
    """2 tenants com 1 admin cada (mesma senha)."""
    # ... cria org_a/org_b + user_a/user_b, retorna SimpleNamespace
```

Fixtures de auth prontas: `auth_headers_org_a` / `auth_headers_org_b`
(Bearer real obtido via `POST /api/v1/auth/login`).

## Testando auth corretamente

```python
def test_me_with_bearer(client, seed_two_orgs, auth_headers_org_a):
    client.cookies.clear()   # PROVA que o Bearer autentica (nao o cookie)
    response = client.get("/api/v1/auth/me", headers=auth_headers_org_a)
    assert response.status_code == 200


def test_me_with_cookie(client, seed_two_orgs):
    client.post("/api/v1/auth/login", json={...}, headers={"X-Tenant-Slug": "org-a"})
    response = client.get("/api/v1/auth/me", headers={"X-Tenant-Slug": "org-a"})
    assert response.status_code == 200
```

## Testes de tenant isolation (padrao obrigatorio)

Para CADA endpoint de dominio, cobrir no minimo:

```python
def test_list_returns_only_own_tenant(client, seed_two_orgs, auth_headers_org_a):
    response = client.get("/api/v1/<features>", headers=auth_headers_org_a)
    ids = [i["id"] for i in response.json()["items"]]
    assert feature_a.id in ids
    assert feature_b.id not in ids          # <- o assert que importa


def test_get_from_other_tenant_returns_404(client, seed_two_orgs, auth_headers_org_a):
    response = client.get(f"/api/v1/<features>/{feature_b.id}", headers=auth_headers_org_a)
    assert response.status_code == 404       # generico, NAO 403
    assert response.json()["error"]["code"] == "not_found"


def test_token_from_another_tenant_is_rejected(client, seed_two_orgs, auth_headers_org_b):
    client.cookies.clear()
    headers = {**auth_headers_org_b, "X-Tenant-Slug": "org-a"}   # token B no tenant A
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401


def test_create_ignores_organization_id_do_payload(client, seed_two_orgs, auth_headers_org_a):
    payload = {"name": "X", "organization_id": seed_two_orgs.org_b.id}  # malicioso
    response = client.post("/api/v1/<features>", json=payload, headers=auth_headers_org_a)
    assert response.json()["organization_id"] == seed_two_orgs.org_a.id  # do contexto
```

## Estrutura de arquivos de teste

```
tests/
+-- conftest.py
+-- test_health.py
+-- test_auth_api.py
+-- test_users_api.py
+-- test_organization_api.py
+-- test_tenancy.py          # resolucao de tenant (header, subdomain, custom_domain)
+-- test_themes.py           # white-label
+-- test_web_pages.py        # paginas HTML (login, dashboard)
+-- test_security.py         # headers, hashing, JWT, constraints
+-- test_<feature>_api.py    # CRUD da feature
+-- test_<feature>_isolation.py  # ou secao de isolation no proprio test_<feature>_api.py
```

## Convencoes

- **AAA**: Arrange (setup) / Act (chamada) / Assert (verificacao), docstring
  curta dizendo o QUE esta garantindo.
- Assert no **envelope de erro**: `response.json()["error"]["code"]`.
- IDs/objetos do seed via fixture (`seed_two_orgs`), nunca hardcoded.
- Teste de migration: round-trip `alembic upgrade/downgrade/upgrade`
  validado manualmente antes do commit (nao automatizado).

## Anti-patterns (NUNCA)

```
[X] os.environ["DATABASE_URL"] = "...revenue_sdr_os.db"   -> em memoria!
[X] drop_all/create_all no engine global                  -> engine por teste
[X] Depender do cookie do jar sem querer                  -> client.cookies.clear()
[X] Assert so de status code                              -> assert no corpo/envelope
[X] Fixture mutavel compartilhada entre testes            -> fixtures por funcao
[X] Teste que so passa se outro rodar antes               -> isolamento total
```

## Checklist

```
[ ] CRUD: >=3 testes por endpoint (happy path + erro)
[ ] Isolation: list filtrada, get cross-tenant 404, token cross-tenant 401
[ ] Auth: Bearer (cookies.clear()) E cookie cobertos
[ ] Envelope de erro assertado (error.code)
[ ] pytest 100% verde; ruff check/format limpos
```
