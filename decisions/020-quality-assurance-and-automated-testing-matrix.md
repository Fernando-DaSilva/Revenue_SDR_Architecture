# ADR-020 — Quality Assurance, Testing Matrix, and Visual Quality Control

> **Status**: Aceito  
> **Data**: Agosto de 2026  
> **Contexto**: Para garantir que cada alteração no código mantenha a qualidade total da aplicação, estabilidade de banco de dados, isolamento de tenants e fidelidade visual dos protótipos (`01_SDR_Prototype` e `02_ZAP_Prototype`), institui-se uma matriz de qualidade obrigatória.

---

## 1. Princípios e Metas de Qualidade

1. **Test-First & Zero Regression**: Nenhuma funcionalidade nova é mergeada sem testes unitários e de integração automatizados.
2. **Qualidade Visual de Nível Prototípico**: O frontend hypermedia (HTMX/Alpine/DaisyUI) deve respeitar 100% o design system, espaçamentos, micro-interações e suporte White-Label validados nos protótipos `01_SDR_Prototype` e `02_ZAP_Prototype`.
3. **Isolamento de Tenancy sem Exceções**: A suíte de testes de isolamento de tenants é executada como portão de qualidade impeditivo no CI/CD.

---

## 2. Estrutura da Matriz de Testes

| Categoria de Teste | Ferramenta / Arquivo | Cobertura Alvo | Função |
|---|---|---|---|
| **Isolamento Multi-Tenant** | `pytest tests/test_tenant_isolation.py` | **100% dos endpoints/models** | Garante que nenhuma query ou rota retorne dados de outra `organization_id`. |
| **Testes de Serviço & Domínio** | `pytest tests/unit/` | **> 85% do código Python** | Testa regras de negócio, calculadoras de score DHS, transições de cadência e extração de memória. |
| **Migrations de Banco (Alembic)** | Script CI de Validação | **100% das migrations** | Executa a sequência `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` para garantir reversibilidade. |
| **Integridade de APIs & Erros** | `pytest tests/integration/` | **100% das rotas FastAPI** | Valida contrato do envelope unificado de erro `{"error": {code, message, details}}`. |
| **Visual Quality Control (QA Visual)** | Prompt de Checagem Visual (`prompts/16_...`) | **Todas as telas do produto** | Valida hierarquia visual, responsividade, DaisyUI e os 5 presets do Theme Studio. |

---

## 3. Workflow de Qualidade em CI/CD

Todo desenvolvedor ou agente autônomo DEVE validar a seguinte sequência antes de autorizar o merge:

```bash
# 1. Análise Estática e Linting de Código
ruff check app/ tests/ scripts/ alembic/
ruff format --check app/ tests/ scripts/

# 2. Execução da Suíte Completa de Testes Automáticos
pytest --cov=app --cov-report=term-missing

# 3. Validação Round-Trip de Migrations de Banco
alembic upgrade head && alembic downgrade -1 && alembic upgrade head

# 4. Verificação de Saúde e Boot da Aplicação
./start &
curl http://127.0.0.1:8000/api/v1/health/
```

---

## 4. Consequências

- **Vantagens**:
  - Código limpo, testado e imune a vazamentos multi-tenant.
  - Migrações de banco confiáveis sem risco de lock ou corrupção de schema em produção.
  - Fidelidade visual constante alinhada aos protótipos de alta fidelidade.
