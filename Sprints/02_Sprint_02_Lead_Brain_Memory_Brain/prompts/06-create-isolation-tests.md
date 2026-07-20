---
sprint: 02
task: 06-create-isolation-tests
---

# Prompt 02.06 — Testes de Isolamento (Sprint 02)

> Spec da task T11. Padroes: `.skills/pytest-tenant-isolation.md` (v2.0).
> Estes testes sao CRITICOS — multi-tenant leak = violacao de LGPD.

---

## Contexto

APIs de leads/memories/timeline prontas. Criar:

- `tests/test_leads_isolation.py` (ou secao em `tests/test_leads_api.py`)
- Fixtures novas no `tests/conftest.py`: `seed_leads` (1 lead por org,
  com memories e eventos)

## Fixture a adicionar no conftest

```python
@pytest.fixture()
def seed_leads(session, seed_two_orgs) -> SimpleNamespace:
    """1 lead (com memory + evento) por tenant."""
    # lead_a em org_a, lead_b em org_b; retorna SimpleNamespace
```

## Casos OBRIGATORIOS (por endpoint de dominio)

### Listagem

```
[ ] GET /api/v1/leads com credencial de A: so leads de A (assert IDs)
[ ] GET /api/v1/leads?q= com termo que bate em lead de B: nao retorna B
[ ] GET /api/v1/leads?status= nao vaza status de B
[ ] GET /api/v1/leads/{id_a}/memories: so memories do lead A
[ ] GET /api/v1/leads/{id_a}/timeline: so eventos do lead A
```

### Acesso por ID (cross-tenant = 404 generico)

```
[ ] GET   /api/v1/leads/{id_de_B} com credencial de A -> 404 + error.code "not_found"
[ ] PATCH /api/v1/leads/{id_de_B} com credencial de A -> 404
[ ] DELETE /api/v1/leads/{id_de_B} com credencial de A -> 404
[ ] GET /api/v1/leads/{id_de_B}/memories com credencial de A -> 404
[ ] POST /api/v1/leads/{id_de_B}/memories com credencial de A -> 404
[ ] PATCH /api/v1/leads/{id_de_B}/memories/{mem_de_B} com A -> 404
```

### Escrita cross-tenant

```
[ ] POST /api/v1/leads com organization_id DE B no payload -> cria em A
    (org do contexto; payload malicioso ignorado)
[ ] POST /api/v1/leads/{id_a}/memories com lead de A e credencial de A -> 201;
    mesma chamada com credencial de B -> 404
[ ] PATCH status de lead de B -> 404 (nao altera)
```

### Token/JWT cross-tenant

```
[ ] Bearer emitido no tenant B usado com header X-Tenant-Slug: org-a -> 401
    (token nao opera fora do tenant de origem)
```

### Merge cross-tenant

```
[ ] Lead de A tem telefone X. Criar lead em B com telefone X -> CRIA NOVO
    em B (merge NUNCA cruza tenants)
```

### Soft delete

```
[ ] DELETE lead A -> lista de A nao mostra mais; GET direto -> 404
[ ] Lead deletado em A nao bloqueia criacao de lead com mesmo telefone em A
    (merge ignora deletados)
```

## Validacao

```bash
pytest tests/test_leads_isolation.py -v     # todos passam
pytest                                       # suite completa verde
ruff check tests/
```

## Checklist

```
[ ] >= 15 casos de isolamento cobrindo list/get/create/update/delete
[ ] Sub-recursos (memories, timeline) cobertos na cadeia de tenant
[ ] Assert no envelope: response.json()["error"]["code"]
[ ] client.cookies.clear() nos testes de Bearer
[ ] Merge nunca cruza tenant
[ ] Suite completa verde (nao so os novos)
```
