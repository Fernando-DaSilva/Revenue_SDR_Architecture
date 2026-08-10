---
name: ai-agent-coding-guidelines
description: |
  Carregue esta skill sempre que for atuar como um Agente de IA para escrever, refatorar
  ou testar código no projeto Revenue SDR OS, garantindo conformidade total com a arquitetura e guardiões.
version: 1.0.0
author: Hermes (arquiteto)
license: Proprietary
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
metadata:
  hermes:
    tags: [ai-agents, coding-guidelines, guardrails, architecture-compliance, verification]
---

# Skill: Guardiões e Diretrizes de Codificação para Agentes de IA

## 1. Princípio Fundamental

Como **Agente de IA de Codificação**, você está construindo o **Revenue SDR OS**.
Você DEVE respeitar rigorosamente a separação de camadas, o isolamento multi-tenant Zero-Trust e a matriz de testes automatizados.

---

## 2. As Camadas Obrigatórias de Código (Domain Package Layout)

Cada funcionalidade de negócio vive dentro de seu pacote em `app/<dominio>/`:

```
app/<dominio>/
+-- models.py       # Tabela SQLModel com TenantMixin (organization_id FK NOT NULL)
+-- schemas.py      # Schemas Pydantic v2 (validação estrita de entrada/saída)
+-- service.py      # Camada de Serviço (regras + queries obrigatoriamente por org_id)
+-- api.py          # Rota FastAPI fina (apenas desempacota request e chama service)
```

---

## 3. As 5 Regras de Ouro de Segurança Multi-Tenant

1. **Filtro Mandatório**: Toda query em `service.py` DEVE ter `.where(Model.organization_id == current_org.id)`.
2. **ContextVar Context**: O `organization_id` vem SEMPRE do contexto `get_current_organization()`, NUNCA de parâmetros ou payload enviadas pelo cliente.
3. **Retorno 404 Genérico**: Tentativa de acesso a recurso de outro tenant DEVE retornar `404 Not Found` (NUNCA `403 Forbidden` para não vazar a existência do dado).
4. **JWT Verification**: Assegurar que o claim `org` do token JWT bate com o tenant resolvido no request.
5. **Teste de Isolamento Cross-Tenant**: Escrever no mínimo 2 testes de isolamento cruzado em `tests/` para cada novo endpoint criado.

---

## 4. O Harness de Validação PRÉ-COMMIT (Obrigatório para Agentes)

Antes de reportar a tarefa como concluída, execute o pipeline de verificação:

```bash
# 1. Linting e Formatação
ruff check app/ tests/ scripts/ alembic/
ruff format --check app/ tests/ scripts/

# 2. Suíte de Testes com Cobertura
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=85

# 3. Migration Round-Trip (se alterou models.py)
alembic upgrade head && alembic downgrade -1 && alembic upgrade head
```

---

## 5. Anti-Patterns Fatais (NUNCA cometa)

```
[X] Query SQLModel sem filtro de organization_id   -> Quebra fatal do isolamento multi-tenant!
[X] Escrever SQL bruto ou query na rota api.py     -> Coloque a query no service.py
[X] Lançar HTTPException(400, "...") solta         -> Use AppError e subclasses
[X] Colocar validações pydantic no Model           -> Coloque no Schema Pydantic
[X] Importar bibliotecas não declaradas            -> Verifique o pyproject.toml
```

---

## 6. Checklist Final do Agente

- [ ] Código separado rigorosamente nas 4 camadas (`models`, `schemas`, `service`, `api`)
- [ ] Todas as queries no `service.py` filtram por `organization_id`
- [ ] Erros utilizam subclasses de `AppError` com o envelope de erro padrão
- [ ] O harness de verificação (`pytest`, `ruff`, `alembic`) foi executado e passou 100%
