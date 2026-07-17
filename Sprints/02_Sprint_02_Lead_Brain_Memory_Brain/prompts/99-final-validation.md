---
sprint: 02
task: 99-final-validation
---

# Prompt 02.99 — Validacao Final da Sprint 02

> **Rode este prompt quando TODAS as tasks (T1-T12) estiverem concluidas.**

---

## Validacao automatica completa

### 1. Setup limpo

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate

# Backup do banco atual
cp revenue_sdr_os.db revenue_sdr_os.db.backup 2>/dev/null

# Drop banco pra testar migration limpa
rm revenue_sdr_os.db
alembic upgrade head
python scripts/seed.py
```

### 2. Servidor sobe

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level warning &
sleep 3
curl http://127.0.0.1:8000/api/v1/health/
# Esperado: {"status":"ok","version":"0.1.0","service":"revenue-sdr-os"}
```

### 3. Todos os testes passam

```bash
cd ~/AGENCIA/SDR
source .venv/bin/activate

pytest -v --tb=short
# TODOS devem passar (Sprint 1 + Sprint 2)
# Esperado: 30+ testes passando
```

### 4. Tenant isolation passa (CRITICO)

```bash
pytest tests/test_lead_isolation.py -v --tb=short
# TODOS os 11 testes devem passar
```

### 5. End-to-end manual (curl)

```bash
# Login
TOKEN_A=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"email":"admin@clinica-bela.com","password":"senha123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

TOKEN_B=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: imob-center" \
  -d '{"email":"admin@imob-center.com","password":"senha123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Criar lead em A
LEAD_A=$(curl -s -X POST http://127.0.0.1:8000/api/v1/leads \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"name":"Joao A","phone":"+5511999991111","source":"whatsapp"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Adicionar memory
curl -s -X POST http://127.0.0.1:8000/api/v1/leads/$LEAD_A/memories \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: clinica-bela" \
  -d '{"category":"objection","key":"preco","value":"Acha caro"}'

# Tentar acessar como B (deve dar 404)
curl -s -w "\nHTTP %{http_code}\n" \
  http://127.0.0.1:8000/api/v1/leads/$LEAD_A \
  -H "Authorization: Bearer $TOKEN_B" \
  -H "X-Tenant-Slug: imob-center"

# Tentar merge cross-tenant (cria novo, NAO faz merge)
curl -s -X POST http://127.0.0.1:8000/api/v1/leads \
  -H "Authorization: Bearer $TOKEN_B" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Slug: imob-center" \
  -d '{"name":"Joao B","phone":"+5511999991111","source":"site"}' \
  | python -c "import sys,json; d=json.load(sys.stdin); print(f'B criou lead NOVO: {d[\"id\"]}')"

# Timeline
curl -s http://127.0.0.1:8000/api/v1/leads/$LEAD_A/timeline \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "X-Tenant-Slug: clinica-bela" \
  | python3 -m json.tool
```

### 6. UI no navegador (verificar visualmente)

Adicione ao `/etc/hosts`:
```
127.0.0.1   clinica-bela.localhost
127.0.0.1   imob-center.localhost
```

Acesse:
- http://clinica-bela.localhost:8000/login → login com admin@clinica-bela.com / senha123
- Lista de leads deve aparecer (vazia se acabou de criar)
- Criar novo lead via UI
- Ver detalhe + memories + timeline

### 7. OpenAPI spec regenerada

```bash
curl http://127.0.0.1:8000/openapi.json | python -m json.tool | grep -E "(/leads|/memories)" | head -10
# Deve mostrar: /api/v1/leads, /api/v1/leads/{lead_id}/memories, etc
```

### 8. Lint (se ruff configurado)

```bash
ruff check app/ tests/
ruff format --check app/ tests/
```

---

## Checklist FINAL (Definition of Done)

```
[ ] Setup limpo funciona (rm db + alembic upgrade + seed)
[ ] Servidor sobe sem warnings
[ ] Health check retorna 200
[ ] pytest -v passa 100%
[ ] pytest tests/test_lead_isolation.py -v passa 11/11
[ ] End-to-end curl funciona:
    [ ] Login em 2 tenants funciona
    [ ] CRUD de lead funciona
    [ ] Merge automatico funciona
    [ ] Memories CRUD funciona
    [ ] Timeline retorna eventos
    [ ] Cross-tenant retorna 404
[ ] UI no navegador funciona
[ ] OpenAPI spec mostra novos endpoints
[ ] Nenhum secret hardcoded
[ ] Codigo segue patterns das skills
```

---

## Se algo falhou

1. Verifique logs do servidor: `tail -f revenue_sdr_os.log` (ou logs no terminal)
2. Rode pytest especifico: `pytest tests/test_leads.py::test_xxx -v --tb=long`
3. Verifique a migration: `sqlite3 revenue_sdr_os.db ".schema leads"`
4. Rode ruff: `ruff check app/api/v1/leads.py`

---

## Commit + push

Quando TUDO passar:

```bash
cd ~/AGENCIA/SDR
git add .
git status

# Deve mostrar:
# - app/models/lead.py (novo)
# - app/api/v1/leads.py (novo)
# - app/api/v1/memories.py (novo)
# - app/services/lead_merge.py (novo)
# - alembic/versions/XXXX_add_leads.py (novo)
# - tests/test_leads.py (novo)
# - tests/test_lead_isolation.py (novo)
# - tests/test_lead_merge.py (novo)
# - tests/test_memories.py (novo)
# - app/api/v1/__init__.py (modificado)
# - app/models/__init__.py (modificado)
# - alembic/env.py (modificado)

git commit -m "feat: Sprint 02 — Lead Brain + Memory Brain

- Models: Lead, LeadMemory, LeadTimelineEvent
- API CRUD de leads com merge automatico (Lead Brain)
- API CRUD de memories com bulk endpoint (Memory Brain)
- Service lead_merge.py (find_existing_lead, merge_lead_data, log_merge_event)
- Migration Alembic
- 11 testes de tenant isolation (CRITICOS)
- 15+ testes de CRUD

Refs: Sprints/02_Sprint_02_Lead_Brain_Memory_Brain"

git push origin main
```

---

## Reporte ao usuario

```
Sprint 02 completa!

Entregues:
  [OK] 3 models novos (Lead, LeadMemory, LeadTimelineEvent)
  [OK] Migration Alembic (round-trip testado)
  [OK] Service de merge automatico
  [OK] API CRUD de leads (6 endpoints)
  [OK] API CRUD de memories (5 endpoints)
  [OK] 11 testes de tenant isolation (100% passing)
  [OK] UI lista de leads (em HTMX)
  [OK] UI detalhe do lead (em HTMX)

Testes: 30+ passing (Sprint 1 + Sprint 2)
Tenant isolation: 11/11 critical tests passing
PR: <link do GitHub>

Proxima sprint: Sprint 03 — Conversations + Opportunity Brain
```

---

*"Sprint 02 done. Lead Brain esta vivo."*