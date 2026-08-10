# ADR-035: Topologia de Engenharia em Streams Paralelas para Desenvolvimento em 2 Meses

**Status**: Aceito (2026-08-10)  
**Contexto**: A entrega do Revenue SDR OS em tempo recorde de 2 meses (60 dias) exige eliminar gargalos sequenciais. Em cronogramas tradicionais, o backend aguarda o modelo de dados, a IA aguarda as APIs de conversa, e o frontend aguarda os webhooks de mensagens. Para atingir a meta de 60 dias, é indispensável estabelecer **5 Streams Paralelas de Engenharia**.

---

## Decisão

1. **5 Streams Paralelas Desacopladas por Contratos**:
   - **Stream 1: Core Engine & Data Persistence**: Modelos SQLModel, Turso/libSQL local DB, migrations Alembic batch, Taskiq background queue com `TenantTaskiqMiddleware`.
   - **Stream 2: AI Multi-Agent Systems & LangGraph**: Grafos de estado (`StateGraph`), checkpointers `AsyncSqliteSaver`, Instructor Pydantic schemas, RAG híbrido (`sqlite-vec` + `pgvector`), roteador multi-tier de LLMs com teto de 900ms.
   - **Stream 3: Messaging Engine & Omnichannel Integration**: Abstração `ZapProvider` (Z-API WhatsApp), Meta 24h Window HSM Template validator, SSE broker real-time, transcrição Whisper.
   - **Stream 4: Frontend & UX Deconstruction**: Desconstrução do HTML monolítico de 1.1MB em Jinja2 templates, HTMX requisições parciais, Alpine.js micro-interações, Tailwind CSS + DaisyUI, ZAP Copilot micro-app.
   - **Stream 5: DevSecOps, SRE & Platform Automation**: Single-tenant VPS orchestrator (systemd), MyraOS Console, pipeline CI/CD sub-minuto, monitoramento LangSmith e audit LGPD.

2. **Interface First & Mocks Contratuais**:
   - Cada stream avança de forma independente utilizando OpenAPI 3.1 mocks e stubs tipados Pydantic v2.

---

## Consequências

- **Positivas**:
  - Eliminação de bloqueios inter-equipes/inter-agentes.
  - Execução simultânea dos componentes das Sprints 02 a 10 ao longo de 8 semanas.
- **Mitigações de Risco**:
  - Exige sincronização diária de contratos de interface (schemas Pydantic) e validação de integração no final de cada micro-sprint horária.
