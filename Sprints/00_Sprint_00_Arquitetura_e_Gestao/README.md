# Sprint 00 — Arquitetura e Gestao

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 00 — ARQUITETURA E GESTAO                                  |
|   Status:  FINALIZADA / PRONTA PARA SPRINT 01                       |
|   Owner:   Arquitetura (Fernando + agente de arquitetura)           |
|   Quando:  Finalizada                                               |
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
[OK] Sprint docs 03-10 detalhadas (Especificações de alto nível definidas)
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

1. **Arquitetura e Design** mantem FOUNDATION/ARCHITECTURE/ROADMAP + skills + specs + **Wireframes em Código**.
2. **Fernando** aprova decisoes (ADRs novos, UI/UX, fluxos).
3. **Design de Interface** (via Agente de IA em `01_SDR_Prototype`) prototipa as telas baseadas nas specs ANTES do início do desenvolvimento backend.
4. **Agente de codificacao full-stack** implementa no repo `~/AGENCIA/SDR/` seguindo as specs, invariantes e o protótipo visual aprovado no frontend.
5. **Revisao** via pytest/ruff/CI + review visual da UI.
6. **Decisoes novas** viram ADR em ARCHITECTURE.md.

---

*"Arquitetura e' a arte de tomar decisoes faceis de reverter."*
