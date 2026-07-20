# Sprint 00 — Arquitetura e Gestao

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 00 — ARQUITETURA E GESTAO                                  |
|   Status:  BASE CONCLUIDA (continua evoluindo com o projeto)        |
|   Owner:   Arquitetura (Fernando + agente de arquitetura)           |
|   Quando:  Continuo (nao tem fim — evolui com o projeto)            |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Objetivo

Construir e manter a fundacao de GESTAO do projeto: docs centrais, skills,
prompts (specs), templates e ADRs. Codigo do produto NAO vive aqui.

---

## Entregaveis

```
[OK] Estrutura de pastas (Sprints/, .skills/, prompts/, templates/)
[OK] README.md (indice geral)
[OK] FOUNDATION.md v2.0 (visao do produto consolidada)
[OK] ARCHITECTURE.md v2.0 (arquitetura vigente + 12 ADRs)
[OK] ROADMAP.md v2.0 (sprints 01-10 com status real)
[OK] AGENTS.md v2.0 (manual para agentes, alinhado a v0.2.0)
[OK] .skills/ (9 skills; 5 principais atualizadas para v0.2.0)
[OK] Sprints/01 (concluida — inclui nota da reescrita v0.2.0)
[OK] Sprints/02 spec + 8 prompts alinhados a v0.2.0
[OK] prompts/01-create-api-endpoint.md + templates/fastapi-route.py
[--] ADRs formais em decisions/ (consolidados em ARCHITECTURE.md por ora)
[--] Sprint docs 03-10 detalhadas (criar quando a sprint anterior fechar)
```

---

## Como este sprint se encaixa no projeto

```
Sprint 00 (este) -> define COMO construir (docs, skills, specs)
Sprint 01 [OK]  -> fundacao profissional (v0.2.0: auth, tenancy, white-label)
Sprint 02 [>>] -> Lead Brain + Memory Brain (spec pronta)
Sprint 03+     -> features do produto (conversas, IA, WhatsApp, omnichannel)
```

---

## Workflow vigente

1. **Arquitetura** mantem FOUNDATION/ARCHITECTURE/ROADMAP + skills + specs
2. **Fernando** aprova decisoes (ADRs novos ou revertidos)
3. **Agente de codificacao** implementa no repo `~/AGENCIA/SDR/` seguindo
   as specs e invariantes
4. **Revisao** via pytest/ruff/CI + review humana
5. **Decisoes novas** viram ADR em ARCHITECTURE.md

---

*"Arquitetura e' a arte de tomar decisoes faceis de reverter."*
