---
sprint: 02
task: 99-final-validation
---

# Prompt 02.99 — Validacao Final da Sprint 02

> Rodar DEPOIS de todas as tasks (T1-T12). Tudo precisa passar antes
> do commit/push.

---

## 1. Suite de testes

```bash
cd ~/AGENCIA/SDR && source .venv/bin/activate
pytest                          # 100% verde (suite toda, nao so os novos)
pytest --cov=app --cov-report=term-missing tests/
```

## 2. Lint + formatacao

```bash
ruff check app/ tests/ scripts/ alembic/
ruff format --check app/ tests/ scripts/
```

## 3. Migration round-trip

```bash
alembic upgrade head
alembic downgrade -1
alembic upgrade head
sqlite3 revenue_sdr_os.db ".tables"   # organizations users leads lead_memories lead_timeline_events alembic_version
```

## 4. Servidor sobe + OpenAPI

```bash
./start &                       # ou: uvicorn app.main:app --port 8000 &
sleep 3
curl -s localhost:8000/api/v1/health/ | python -m json.tool
curl -s localhost:8000/openapi.json | python -c "import json,sys; paths=json.load(sys.stdin)['paths']; print([p for p in paths if 'leads' in p])"
```

Esperado ver: `/api/v1/leads`, `/api/v1/leads/{lead_id}`,
`/api/v1/leads/{lead_id}/memories`, `/api/v1/leads/{lead_id}/timeline`.

## 5. Smoke test funcional (2 tenants)

```bash
# Login nos 2 tenants
TOKEN_A=$(curl -s -X POST localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" -H "X-Tenant-Slug: clinica-bela" \
  -d '{"email":"admin@clinica-bela.com","password":"senha123"}' | python -c "import json,sys;print(json.load(sys.stdin)['access_token'])")
TOKEN_B=$(curl -s -X POST localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" -H "X-Tenant-Slug: imob-center" \
  -d '{"email":"admin@imob-center.com","password":"senha123"}' | python -c "import json,sys;print(json.load(sys.stdin)['access_token'])")

# Criar lead em A
curl -s -X POST localhost:8000/api/v1/leads \
  -H "Content-Type: application/json" -H "X-Tenant-Slug: clinica-bela" \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{"name":"Joao Teste","phone":"+5511999990001","source":"whatsapp"}'

# Duplicata em A -> merge (merged=true, mesmo id)
# Mesmo telefone em B -> cria NOVO em B (sem merge cross-tenant)
# Listar em B -> NAO contem o lead de A
# GET lead de A com TOKEN_B -> 404
# Memory + timeline em A -> funcionam e aparecem na timeline
```

## 6. UI (browser)

```
[ ] http://clinica-bela.localhost:8000/leads -> lista com tema rosa
[ ] http://imob-center.localhost:8000/leads -> lista com tema verde
[ ] Busca filtra; detalhe mostra memories + timeline
[ ] Cada tenant ve SO seus leads
```

## 7. Definition of Done (do spec da sprint)

Rever `../README.md` secao "Criterios de aceitacao" — todos os itens
funcionais e tecnicos marcados.

## 8. Commit

```bash
git status                      # so arquivos da sprint
git add -A
git commit -m "feat: adiciona Lead Brain + Memory Brain (Sprint 2)"
git push origin feature/sprint-02-lead-brain   # ou main, conforme fluxo
```

## Checklist final

```
[ ] pytest 100% verde + cobertura sem buracos nas novas linhas
[ ] ruff check + format limpos
[ ] Migration round-trip OK
[ ] OpenAPI com os endpoints novos
[ ] Smoke funcional com 2 tenants OK (merge + isolamento)
[ ] UI dos 2 tenants OK
[ ] DoD do spec da sprint completo
[ ] Commit em Conventional Commits PT-BR
```
