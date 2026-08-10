# ADR-034: Harness de Execução Autônoma de Agentes de IA e Gating de Segurança no CI/CD

**Status**: Aceito (2026-08-10)  
**Contexto**: A aceleração das sprints para o formato de Micro-Sprints Horárias exige que Agentes de IA (AI Coding Agents) atuem com alta autonomia. Sem guardiões automáticos, o desenvolvimento ultra-rápido corre risco de introduzir vazamentos cross-tenant, regressões de esquema de banco de dados, falhas de segurança OWASP ou código não tipado.

---

## Decisão

1. **Protocolo de Automação de Agentes (AI Agent Autonomous Execution Loop)**:
   - Todo Agente de IA responsável pela codificação deve operar sob o **Loop de Validação Triplo**:
     1. **Prompt Spec Input**: Recebe contrato estrito em JSON/Markdown com schemas Pydantic e regras Zero-Trust.
     2. **Code Generation & Layering**: Implementa estritamente na ordem Model $\rightarrow$ Service $\rightarrow$ Schema $\rightarrow$ Router $\rightarrow$ Web UI.
     3. **Automated Verification Harness**: Executa suíte local de validação antes do commit (`pytest -k tenant`, `ruff check`, `alembic upgrade head -> downgrade -1 -> upgrade head`).

2. **Gating de Segurança DevSecOps por Commit**:
   - Todo commit de micro-sprint passa por verificação automática de segredos (trufflehog/gitleaks), checagem de bibliotecas vulneráveis (pip-audit) e auditoria de AST Python para garantir inclusão de `organization_id` em queries SQLModel.

---

## Consequências

- **Positivas**:
  - Zero tolerância para vazamento de dados entre organizações (Zero-Trust Multi-Tenancy).
  - Autonomia total para agentes produzirem PRs limpos e funcionais sem intervenção humana manual constante.
- **Mitigações de Risco**:
  - Se a suíte de testes falhar, a micro-sprint é automaticamente descartada ou revertida pelo pipeline CI.
