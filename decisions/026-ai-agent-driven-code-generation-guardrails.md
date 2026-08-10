# ADR-026: Guardiões de Engenharia para Codificação via Agentes de IA (AI-Agent Driven Development)

* **Status**: Aprovado
* **Data**: Agosto 2026
* **Autores**: Equipe de Engenharia de Software e Qualidade (Revenue SDR OS)

---

## 1. Contexto e Problema

O **Revenue SDR OS** foi projetado desde a fundação para ter seu código-fonte desenvolvido, estendido e mantido por **Agentes de IA de Codificação** (ex: Antigravity Agents, Claude Code, Codex, OpenCode).

Sem um conjunto rigoroso de **Guardiões de Engenharia**, contratos de interface legíveis por máquina e procedimentos de verificação determinísticos, Agentes de IA tendem a introduzir problemas recorrentes:
1. **Quebra do Isolamento Multi-Tenant**: Esquecer de adicionar `.where(Model.organization_id == current_org.id)` em consultas novas.
2. **Vazamento de Camadas (Layer Pollution)**: Inserir queries brutas SQL ou SQLModel diretamente nas rotas da API FastAPI ou nas páginas HTMX em vez da camada `service.py`.
3. **Inconsistência de Schema**: Modificar os modelos de tabela SQLModel sem autorar a migração equivalente do Alembic em modo batch (`render_as_batch=True`).
4. **Erros de Validação Desconhecidos**: Usar `HTTPException` solta em vez da hierarquia `AppError`, alterando a estrutura padrão do envelope JSON de erros.
5. **Geração de Código Fantasma (Hallucinated Dependencies)**: Importar bibliotecas terceiras não especificadas no `pyproject.toml` ou `package.json`.

---

## 2. Decisão Arquitetural

Instituir o **Framework de Guardiões para Agentes de Codificação de IA (AI Coding Agent Protocol)**. Todo código gerado por um agente deve obrigatoriamente se conformar com as regras de contrato, validação em tempo de compilação/teste e verificação em pipeline.

### O Fluxo de Execução Obrigatório do Agente de IA:

```
+-----------------------------------------------------------------------------------+
| 1. CARREGAMENTO DE CONTEXTO E SKILLS                                              |
|  - Carregar `.skills/revenue-sdr-os-architect.md` + skills da tarefa               |
|  - Ler o contrato do arquivo AGENTS.md e ADRs relevantes                          |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 2. DESENVOLVIMENTO EM CAMADAS (STRICT DOMAIN LAYER SEPARATION)                    |
|  - Passo A: Model (SQLModel com TenantMixin) -> alembic revision (Batch Mode)     |
|  - Passo B: Service (regras de negócio + queries obrigatoriamente por org_id)     |
|  - Passo C: Schemas Pydantic (validação estrita de entrada/saída)                 |
|  - Passo D: Rotas API / Páginas HTMX (rotas finas delegando para o Service)       |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 3. HARNESS DE VERIFICAÇÃO AUTOMÁTICA (PRE-COMMIT CHECK)                           |
|  - Executar pytest (>85% cobertura geral + 100% isolamento multi-tenant)          |
|  - Executar ruff check & ruff format --check                                      |
|  - Executar Alembic Round-Trip (upgrade head -> downgrade -1 -> upgrade head)    |
+-----------------------------------------------------------------------------------+
```

---

## 3. Os 10 Mandamentos Inegociáveis dos Agentes de IA

| # | Mandamento | Por que é Crítico |
|---|---|---|
| 1 | **Tenant Filtering Absoluto** | NENHUMA query de banco pode ser executada sem `.where(Model.organization_id == org_id)`. |
| 2 | **ContextVar para Tenant ID** | O `organization_id` vem estritamente do `ContextVar` do middleware ASGI, NUNCA do payload da API. |
| 3 | **Retorno 404 em Cross-Tenant** | Tentativas de acessar dados de outro tenant devem retornar `404 Not Found` genérico (NUNCA 403 Forbidden). |
| 4 | **Rotas Finas / Services Robustos** | Regras de negócio e chamadas ORM vivem no `service.py`. A rota FastAPI apenas desempacota o request e chama o serviço. |
| 5 | **Envelope Padrão de Erro** | Todo erro deve lançar subclasses de `AppError` para retornar o envelope `{"error": {"code": ..., "message": ..., "details": ...}}`. |
| 6 | **Schema via Alembic Batch** | NENHUMA alteração de tabela ocorre sem script Alembic testado com `render_as_batch=True`. |
| 7 | **Prefixos Obrigatórios nos IDs** | Todo ID deve usar a função `prefixed_id("lead")`, `prefixed_id("conv")`, etc. |
| 8 | **Sem Dependências Não Aprovadas** | Não instalar libs sem verificar o `pyproject.toml`. Usar a stack fixa da ADR-001/002/006. |
| 9 | **Validação em Schemas, Não no Model** | `SQLModel table=True` não valida entrada. A validação fica nos schemas Pydantic. |
| 10 | **Verificação Completa Antes do Commit** | O agente DEVE rodar e passar 100% no `pytest`, `ruff` e `alembic` antes de sinalizar conclusão ao usuário. |

---

## 4. Harness de Validação para Agentes (Automated Verification Script)

Os Agentes de IA devem utilizar o script de verificação integrado `./scripts/verify.sh` ou executar os comandos abaixo antes de concluir qualquer tarefa:

```bash
#!/usr/bin/env bash
set -e

echo "=== 1. Análise Estática e Linting (Ruff) ==="
ruff check app/ tests/ scripts/ alembic/
ruff format --check app/ tests/ scripts/

echo "=== 2. Suíte de Testes e Isolamento Multi-Tenant ==="
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=85

echo "=== 3. Validação Round-Trip de Migrações Alembic ==="
alembic upgrade head
alembic downgrade -1
alembic upgrade head

echo "=== 4. Smoke Test de Saúde da Aplicação ==="
python -c "from app.main import create_app; app = create_app(); print('App factory OK')"

echo "✅ VERIFICAÇÃO CONCLUÍDA COM SUCESSO!"
```

---

## 5. Consequências

* **Desenvolvimento de Alta Velocidade e Zero Defeitos**: Os agentes de IA entregam código alinhado 100% à arquitetura existente sem introduzir regressões.
* **Repositório Auto-Documentado e Predictable**: O código mantém padrão estético e estrutural idêntico, independentemente de qual agente de IA o gerou.
