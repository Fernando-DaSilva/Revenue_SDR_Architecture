# ADR-039: Motor de Follow-up Multi-Cenário Automatizado e Recuperação de Objeções

* **Status**: Aceito (Sprint 00 / Implementação na Sprint 03 & Sprint 04)
* **Data**: 2026-08-13
* **Autores**: Fernando Da Silva & SDR Software Team

---

## 1. Contexto e Problema

No processo de vendas de alta performance executado por SDRs (Sales Development Representatives), grande parte das oportunidades de conversão é perdida por falta de acompanhamento consistente ou abandono do lead após uma objeção inicial. 

Os cenários de acompanhamento variam drasticamente:
1. **Tratamento e Recuperação de Objeções**: O lead apresenta uma objeção em um determinado dia (ex: "sem orçamento no momento", "preciso falar com meu sócio", "estou ocupado esta semana"). O SDR precisa reagendar uma tentativa de contato para $N$ dias no futuro.
2. **Reengajamento e Re-venda para Clientes/Leads Frios**: O lead interrompeu o contato ou é um ex-cliente e necessita de um fluxo automatizado de reaquecimento após semanas/meses.
3. **Lembretes de Agenda & Pré/Pós-Reunião**: Confirmações automáticas pré-reunião, lembretes de tópicos específicos acordados na agenda e acompanhamento pós-reunião (ex: no-show ou envio de proposta).

A arquitetura original possuía uma `Cadence Engine` estática e sequencial. Era necessário evoluí-la para um **Motor de Follow-up Multi-Cenário Automatizado** integrado à `Memory Brain` e aos workers assíncronos (`Taskiq`).

---

## 2. Decisão Arquitetural

Decidimos evoluir a `Cadence Engine` para o **Motor de Follow-up Multi-Cenário Automatizado**, com os seguintes componentes centrais:

### 2.1. Arquitetura Baseada em Eventos e Triggers Dinâmicos

O motor escuta eventos registrados na tabela central de eventos (`events`) e memórias extraídas pela `Memory Brain`:
- `objection_detected`: Quando a IA ou o vendedor registra uma objeção com tag (ex: `price`, `timing`, `decision_maker`). O motor busca a regra correspondente em `follow_up_rules` e programa um job assíncrono via `Taskiq`.
- `winback_timer_expired`: Acionado para leads inativos há $X$ dias sem interação.
- `agenda_reminder_due`: Acionado pré ou pós-agendamento de reunião.

### 2.2. Modelo de Dados Relacional (SQLModel / Alembic)

Serão criadas duas novas tabelas com suporte a multi-tenancy Zero-Trust (ADR-018) no Supabase Managed PostgreSQL (ADR-037):

```sql
CREATE TABLE follow_up_rules (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    scenario_type VARCHAR(50) NOT NULL, -- objection_recovery, winback, agenda_reminder, custom
    objection_tag VARCHAR(50),          -- price, timing, competitor, silent
    delay_hours INTEGER NOT NULL DEFAULT 24,
    target_channel VARCHAR(50) NOT NULL DEFAULT 'zap', -- zap, email, instagram
    template_id VARCHAR,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE follow_up_schedules (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,
    rule_id VARCHAR NOT NULL,
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, executed, canceled, skipped
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id),
    FOREIGN KEY (rule_id) REFERENCES follow_up_rules(id)
);
```

### 2.3. Resiliência, Idempotência e Conformidade WhatsApp (Meta 24h)

1. **Idempotência**: Cada job no `Taskiq` utiliza chave determinística `job_key = f"followup:{tenant_id}:{lead_id}:{rule_id}:{execution_date}"` (ADR-021).
2. **Propagação de Tenant**: O job utiliza `TenantTaskiqMiddleware` para hidratar a `ContextVar` do tenant antes da execução do envio (ADR-030).
3. **Guardrail da Janela de 24h da Meta (ADR-032)**:
   - Se o tempo desde o último `inbound_message` do lead for $> 24\text{ horas}$, o motor **bloqueia o texto livre da IA** e força o envio de uma mensagem de template homologada (**Meta HSM Template**).
   - Se o lead responder à HSM, a conversa reabre e a IA retoma o diálogo personalizado de re-venda.

---

## 3. Consequências

### Positivas
- **Controle Total de Follow-up**: Garantia de zero perda de leads por falta de acompanhamento ("Nunca mais perca um lead").
- **Automatização de Objeções**: Capacidade de converter objeções temporárias em vendas futuras agendadas.
- **Conformidade Nascida Nativa**: Proteção contra bloqueios no WhatsApp respeitando a janela da Meta e rate limiting com jitter (ADR-032).

### Mitigações
- **Monitoramento de Agendamentos**: Painel visual de cadências e acompanhamentos pendentes integrado ao Command Center (`01_SDR_Prototype`).
