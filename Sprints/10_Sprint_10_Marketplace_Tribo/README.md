# Sprint 10 — Playbooks Verticais + Marketplace da Tribo

```
+----------------------------------------------------------------------+
|                                                                      |
|   SPRINT 10 — PLAYBOOKS VERTICAIS + MARKETPLACE                     |
|   Status:  DOCUMENTADA                                              |
|   Owner:   Agente de codificacao / Tribo de Negócios                 |
|   Quando:  Apos conclusao da Sprint 09                               |
|   Repo:    ~/AGENCIA/SDR/                                            |
|   Branch:  feature/sprint-10-marketplace                             |
|                                                                      |
+----------------------------------------------------------------------+
```

---

## Visão Geral

O passo final (e inicial da escalabilidade de receita) do Revenue SDR OS. Permitir que especialistas em vendas de nichos específicos (Imobiliário, Odontológico, Consórcios, B2B SaaS) criem e vendam suas próprias matrizes de IA.
1. **Playbooks Verticais**: Templates pré-prontos que definem a Persona da IA (Prompt Base), a base de conhecimento (RAG files) e a cadência de follow-up específica para um nicho.
2. **Marketplace (Tribo)**: Uma vitrine na plataforma MyraOS onde Tenants podem instalar "Pacote Corretor Imobiliário PRO por Fernando".

---

## Schema Previsto (Alembic)

### Tabela: playbooks
```sql
CREATE TABLE playbooks (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL, -- quem criou
    title VARCHAR(200) NOT NULL,
    description TEXT,
    industry VARCHAR(100) NOT NULL,
    persona_prompt TEXT NOT NULL,
    cadence_schema JSON NOT NULL, -- Definição de passos (Dia 1: msg, Dia 3: email)
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    price FLOAT NOT NULL DEFAULT 0.0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

### Tabela: tenant_playbooks (Instalações)
```sql
CREATE TABLE tenant_playbooks (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL, -- quem instalou
    playbook_id VARCHAR NOT NULL, -- o que foi instalado
    installed_at DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (playbook_id) REFERENCES playbooks(id)
);
```

---

## Endpoints e Serviços

- **Marketplace API**: `GET /api/v1/marketplace/playbooks` (Acessa o hub central da MyraOS para buscar playbooks públicos).
- **Instalação**: `POST /api/v1/marketplace/playbooks/{id}/install` (Puxa o playbook e o injeta no AI Sales Brain do Tenant).

---

---

## Alinhamento com Prototipos (`01_SDR_Prototype` e `02_ZAP_Prototype`)

- **01_SDR_Prototype**:
  - Cadences & Agentes Engine (`activeTab: 'cadences'`): vitrine e seletor de playbooks por nicho comercial.
  - Theme Studio & Color Presets: injeção de temas e identidades visuais adequadas ao nicho do playbook instalado.
- **02_ZAP_Prototype**:
  - Atualização dinâmica das sugestões RAG e persona do atendente IA no Standalone Zap Micro-App ao alternar playbooks.

---

## SLAs de Performance (P95) e Requisitos de Qualidade & Segurança

- **Performance SLAs (ADR-019)**:
  - Busca de Playbooks no Marketplace: **$< 50\text{ ms}$**
  - Instalação e injeção de Playbook no AI Sales Brain: **$< 200\text{ ms}$**
- **Segurança Zero-Trust (ADR-018)**:
  - Proteção de Propriedade Intelectual (IP): ocultar prompts de sistema brutos na UI, expondo apenas variáveis parametrizáveis.
  - Isolamento estrito por `organization_id` nos playbooks privados do tenant.
- **Garantia de Qualidade (ADR-020)**:
  - Cobertura de testes unitários do Marketplace e carregador de Playbooks **> 85%**.
  - **100% de cobertura nos testes de isolamento de playbooks** (`tests/test_playbook_isolation.py`).
  - Migration Alembic das tabelas `playbooks` e `tenant_playbooks` testadas via round-trip.

---

## Criterios de Aceitacao (Definition of Done)

```
[ ] Listagem de Playbooks públicos no Marketplace (GET /api/v1/marketplace/playbooks)
[ ] Instalação de Playbook (POST /api/v1/marketplace/playbooks/{id}/install) injetando Persona e RAG no tenant
[ ] Proteção de IP esconde o prompt base mantendo apenas parâmetros editáveis
[ ] Cross-tenant isolation 100% aprovado em pytest
```
