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

## Decisões Críticas

- **Segurança de IP**: Playbooks podem ser caros (Propriedade Intelectual do criador). Como garantir que os prompts base e bases RAG não sejam facilmente extraídos pelos tenants compradores? (Ocultar prompt na UI, mostrando apenas variáveis customizáveis).
- **Agnóstico de IA**: O playbook deve focar nas diretrizes comportamentais de vendas e contorno de objeções, e não em modelos específicos (OpenAI, Anthropic), permitindo que a infraestrutura subjacente troque o LLM se necessário.
