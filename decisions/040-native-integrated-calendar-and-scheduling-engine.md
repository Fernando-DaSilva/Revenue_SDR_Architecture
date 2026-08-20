# ADR-040: Sistema Interno Integrado de Calendário, Gestão de Agendamentos e Sincronização Multi-Provedor

* **Status**: Aceito (Sprint 00 / Implementação na Sprint 05)
* **Data**: 2026-08-13
* **Autores**: Fernando Da Silva & SDR Software Team

---

## 1. Contexto e Problema

O objetivo central do Revenue SDR OS é gerar receita através da promessa: *"O cliente não compra Zap ou IA; ele compra agenda cheia."*

Apenas integrar externamente via API (ex: chamadas pontuais de ferramenta da IA ao Google Calendar) é insuficiente para uma operação comercial robusta. A plataforma necessita de uma **ferramenta interna completa de calendário e agendamento de reuniões** (no estilo Google Calendar / Cal.com), onde a equipe comercial e os gestores possam:
1. Visualizar e gerenciar o fluxo completo de eventos e reuniões em um **Dashboard específico de Eventos e Agendamentos**.
2. Definir janelas de disponibilidade de SDRs e Closers (hosts), tipos de reuniões (`meeting_types`), tempos de preparação/buffer e regras de reagendamento.
3. Controlar internamente os status da reunião (`scheduled`, `confirmed`, `completed`, `rescheduled`, `no_show`, `canceled`).
4. Manter **sincronização bidirecional e exportação** com ferramentas externas como Google Calendar (OAuth2), Cal.com (API/Webhooks) e ferramentas compatíveis com o padrão iCalendar RFC 5545 (`.ics`).

---

## 2. Decisão Arquitetural

Decidimos integrar o **Sistema Interno de Calendário e Agendamentos (Internal Calendar & Scheduling Core)** nativamente na arquitetura do produto, expandindo o escopo da **Sprint 05**.

### 2.1. Arquitetura em Camadas do Sistema de Calendário

```
+-----------------------------------------------------------------------+
|                Jinja2 / HTMX / Alpine.js UI Layer                    |
|   [ Dashboard de Eventos e Reuniões (`commandCenterTab: 'calendar'`) ]  |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    Core Calendar & Scheduling Service                 |
|   - Slot Finder & Host Availability Matching Engine                  |
|   - Meeting Lifecycle State Machine & Double-Booking Prevention       |
|   - Internal Event Store & iCalendar RFC 5545 Generator (.ics)        |
+-----------------------------------------------------------------------+
                                   |
        +--------------------------+--------------------------+
        |                                                     |
        v                                                     v
+------------------------------------+   +------------------------------------+
|   Sync Adapters (External Sync)    |   |     AI Sales Brain Tools           |
|  - GoogleCalendarAdapter (OAuth2)  |   |  - `@tool search_available_slots`  |
|  - CalComAdapter (REST & Webhook)  |   |  - `@tool book_meeting`            |
|  - ICalendarAdapter (.ics Export)  |   |  - `@tool reschedule_meeting`      |
+------------------------------------+   +------------------------------------+
```

### 2.2. Modelo de Dados Relacional (SQLModel / Supabase PostgreSQL ADR-037)

```sql
-- Tipos de Reunião (ex: Demonstração 30min, Diagnóstico 45min)
CREATE TABLE meeting_types (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    name VARCHAR(100) NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 30,
    buffer_minutes INTEGER NOT NULL DEFAULT 15,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Janelas de Disponibilidade dos Vendedores/Hosts
CREATE TABLE host_availabilities (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    day_of_week INTEGER NOT NULL, -- 0=Domingo, 1=Segunda, ..., 6=Sábado
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Eventos / Reuniões Agendadas (Store Interno Raiz)
CREATE TABLE calendar_events (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    lead_id VARCHAR NOT NULL,
    host_user_id VARCHAR NOT NULL,
    meeting_type_id VARCHAR,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'scheduled', -- scheduled, confirmed, completed, rescheduled, no_show, canceled
    location_url VARCHAR(500), -- Zoom, Google Meet, WhatsApp Call link
    ics_uid VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES leads(id),
    FOREIGN KEY (host_user_id) REFERENCES users(id),
    FOREIGN KEY (meeting_type_id) REFERENCES meeting_types(id)
);

-- Mapeamento de Sincronização Externa (Google Calendar, Cal.com, .ics)
CREATE TABLE external_calendar_syncs (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    provider VARCHAR(50) NOT NULL, -- google_calendar, cal_com, ics_feed
    external_calendar_id VARCHAR(255),
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    sync_token TEXT,
    last_synced_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 2.3. Funcionalidades do Dashboard de Eventos e Reuniões UI

O protótipo `01_SDR_Prototype` e o frontend HTMX receberão a aba dedicada `commandCenterTab: 'calendar'`:
1. **Visualização Multivisão**: Alternância instantânea entre visões Dia, Semana, Mês e Lista/Agenda.
2. **Filtro por Host / Vendedor**: Seleção individual ou da equipe inteira para análise de ocupação de agenda.
3. **Modal de Ações Rápidas**: Agendar reunião manualmente, marcar *No-Show*, reagendar com envio de notificação automática ao lead ou cancelar.
4. **Feed de Assinatura iCalendar (.ics)**: Geração de URL segura com token por usuário/tenant para subscrição direta no Apple Calendar, Google Calendar ou Outlook.

---

## 3. Consequências

### Positivas
- **Independência Operacional**: O cliente pode gerenciar todas as reuniões e compromissos diretamente no SDR OS sem obrigatoriedade de ferramentas terceiras pagas.
- **Sincronização Flexível**: Suporte nativo a Google Calendar, Cal.com e arquivos/feeds `.ics`.
- **Rastreabilidade de Vendas**: Métricas nativas de conversão de agendamento $\rightarrow$ presença $\rightarrow$ fechamento diretamente no Manager Brain.

### Mitigações
- **Resolução de Conflitos de Agendamento**: Cálculo estrito de interseção de horários (`start_time < existing.end_time AND end_time > existing.start_time`) para garantir prevenção de double-booking.
