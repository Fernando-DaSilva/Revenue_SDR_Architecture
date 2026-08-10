# ADR-031: Protocolo de Reidratação de Leads Inativos do Cold Storage (Supabase/PostgreSQL) para o Hot Storage (Turso/libSQL)

* **Status**: Aprovado
* **Data**: Agosto 2026
* **Autores**: Equipe de Arquitetura e Engenharia Backend (Revenue SDR OS)

---

## 1. Contexto e Problema

Conforme estabelecido no **ADR-015 (Data Archiving)**, o Revenue SDR OS adota um modelo de **Storage Tiering (Hot/Cold)**:
- **Hot Storage (Turso / libSQL local)**: Mantém os dados ativos de atendimento com resposta em menos de 10ms.
- **Cold Storage / DW (PostgreSQL / Supabase)**: Recebe réplicas e conversas consolidadas com mais de 30 dias para análise e economia de espaço na VPS.

### A Lacuna Crítica Identificada no Audit (Section I.1)
Se um lead inativo há mais de 30 ou 60 dias voltar a enviar uma mensagem no WhatsApp, o arquivo local do Turso na VPS não possuirá mais seu histórico recente nem suas memórias contextuais (preferências, objeções superadas, histórico de compras).

Sem um **Protocolo de Reidratação Automática**, o Agente SDR de IA trataria um lead recorrente como um contato totalmente novo (*cold lead*), destruindo a personalização do atendimento e violando o Pilar 1 da plataforma ("Memória persistente do relacionamento").

---

## 2. Decisão Arquitetural

Instituir o **Protocolo de Reidratação de Leads Inativos** no `LeadService` (`app/services/rehydration_service.py`), acionado automaticamente durante a ingestão de webhooks antes da execução do Agente SDR de IA.

### A. Fluxo de Execução do Protocolo de Reidratação

```
Inbound Webhook (Z-API / WhatsApp)
  |
  v
LeadService.get_or_hydrate_lead(phone_number, org_id)
  |
  +--> [1] Lead existe no Turso Hot Storage?
  |      |-- SIM (Ativo) -> Retorna lead imediatamente.
  |      +-- NÃO / Arquivado -> Inicia Protocolo de Reidratação
  v
[2] Query no PostgreSQL Cold Storage DW (Supabase)
  | Fetch: perfil do lead, atributos do Memory Brain, 
  |        últimas 10 mensagens de histórico conversacional.
  v
[3] Gravação no Turso Local Hot Storage
  | Re-insere Lead record (com status `active` e `archived_at=None`)
  | Re-insere Memórias e Atributos de Contexto
  | Re-insere Últimas 10 Mensagens na tabela `messages`
  v
[4] Execução do LangGraph SDR Agent
  | O agente responde ao lead com 100% de contexto recuperado (< 1.2s SLA)
```

### B. Padronização Estrita de Modelos de Embedding e Dimensões (Evitando Model Drift)

Para garantir a coerência do RAG Híbrido (ADR-022):
- O **Hot RAG (`sqlite-vec` no Turso)** e o **Cold RAG (`pgvector` no PostgreSQL)** DEVEM obrigatoriamente utilizar o mesmo modelo de embedding e dimensionalidade: `text-embedding-3-small` da OpenAI fixado em **1536 dimensões** (ou `bge-small-en-v1.5` em 384d no modo local).
- Atualizações de modelos de embedding no Data Warehouse exigem um job de migração de vetores no Turso local via Taskiq para evitar distorção nas distâncias de Cosseno.

---

## 3. Código de Referência de Implementação

```python
# app/services/rehydration_service.py
from sqlmodel import Session, select
from app.models.lead import Lead
from app.models.message import Message
from app.models.memory import LeadMemory
from app.db.cold_storage import cold_dw_engine
from app.core.logging import logger

class RehydrationService:
    """
    Recupera contexto e histórico de leads inativos (>30 dias) do PostgreSQL DW
    e reidrata o Turso Hot Storage local na VPS do cliente.
    """

    async def hydrate_lead_from_cold_storage(
        self, session: Session, organization_id: str, phone_number: str
    ) -> Lead | None:
        logger.info(
            "Triggering Lead Rehydration Protocol from Cold Storage",
            phone=phone_number,
            org_id=organization_id,
        )

        # 1. Fetch Lead & Context from DW
        with Session(cold_dw_engine) as dw_session:
            dw_lead = dw_session.exec(
                select(Lead).where(
                    Lead.organization_id == organization_id,
                    Lead.phone == phone_number,
                )
            ).first()

            if not dw_lead:
                return None

            memories = dw_session.exec(
                select(LeadMemory).where(
                    LeadMemory.organization_id == organization_id,
                    LeadMemory.lead_id == dw_lead.id,
                )
            ).all()

            recent_messages = dw_session.exec(
                select(Message)
                .where(
                    Message.organization_id == organization_id,
                    Message.lead_id == dw_lead.id,
                )
                .order_by(Message.created_at.desc())
                .limit(10)
            ).all()

        # 2. Re-hydrate local Turso DB
        dw_lead.archived_at = None
        session.add(dw_lead)

        for mem in memories:
            session.merge(mem)

        for msg in reversed(recent_messages):
            session.merge(msg)

        session.commit()
        session.refresh(dw_lead)

        logger.info(
            "Lead successfully re-hydrated into Hot Storage",
            lead_id=str(dw_lead.id),
            memories_count=len(memories),
            messages_count=len(recent_messages),
        )

        return dw_lead
```

---

## 4. Consequências

* **Positivas**:
  - Leads inativos que retornam após 30, 60 ou 180 dias são atendidos com histórico completo de preferências e objeções.
  - Zero estouro de memória no banco local da VPS (dados continuam sendo arquivados após 30 dias de inatividade).
  - Alinhamento total do RAG Híbrido sem falhas de Cosine Similarity.
* **Negativas / Riscos**:
  - A primeira requisição de um lead vindo do Cold Storage pode adicionar um overhead de 100ms a 200ms de latência para a consulta no Supabase DW (executada de forma assíncrona dentro da fila do Taskiq sem bloquear webhooks).

---

## 5. Invariantes para Agentes de Codificação (AI Coding Guardrails)

1. **SEMPRE** verificar se um lead arquivado requer reidratação antes de invocar a pipeline do LangGraph SDR Agent.
2. **NUNCA** alterar as dimensões do vetor no Cold Storage (`pgvector`) sem atualizar sincronicamente o schema do `sqlite-vec` no Turso.
3. **SEMPRE** limitar a reidratação inicial às **10 mensagens mais recentes** e memórias ativas para não inflar a janela de contexto de tokens do LLM desnecessariamente.
