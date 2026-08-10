# ADR-033: Engenharia de Micro-Sprints Horárias e Entrega Contínua Hyper-Acelerada

**Status**: Aceito (2026-08-10)  
**Contexto**: O plano de desenvolvimento tradicional do Revenue SDR OS previa 22 semanas divididas em sprints quinzenais de 14 dias. Contudo, em ambientes altamente automatizados impulsionados por Agentes de IA sêniores, sprints de semanas geram latência de feedback, acoplamento de pull requests e estagnação de validação. Para construir o produto em tempo recorde de **2 meses (60 dias)**, é necessário transformar a cadência de entrega de dias/semanas para **Micro-Sprints Horárias (1h a 4h por micro-funcionalidade)**.

---

## Decisão

1. **Ciclos de Micro-Sprints Horárias (1h - 4h)**:
   - Toda funcionalidade ou épico é descomposto em unidades atômicas executáveis em 1 a 4 horas.
   - Cada Micro-Sprint possui contrato estrito de entrada (Prompt Spec / Schema Pydantic), conjunto de testes automatizados e critérios de aceite inequívocos.

2. **Janelas de Entrega Sub-Horárias**:
   - Integração contínua (CI/CD) dispara a cada commit de micro-sprint.
   - Testes de isolamento multi-tenant, validação de linting `ruff`, migrações Alembic batch round-trip e suíte unitária devem rodar em **$< 60\text{ segundos}$**.

3. **Matriz de Execução em 8 Semanas (60 Dias)**:
   - Todo o escopo das Sprints 02 a 10 é redistribuído em 8 Semanas corridas (Mês 1: Sprints 02-05; Mês 2: Sprints 06-10).

---

## Consequências

- **Positivas**:
  - Velocidade de desenvolvimento aumentada em 5x a 10x.
  - Feedback imediato de quebras arquiteturais ou de segurança.
  - Capacidade real de entregar o Revenue SDR OS completo em 60 dias.
- **Mitigações de Risco**:
  - Exige harness de testes automatizados ultra-rápido para evitar gargalo no CI.
  - Requer especificação rigorosa baseada em OpenAPI 3.1 e Pydantic v2 antes de iniciar qualquer micro-sprint.
