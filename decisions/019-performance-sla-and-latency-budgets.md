# ADR-019 — Performance SLAs, Latency Budgets, and High-Throughput Optimization

> **Status**: Aceito  
> **Data**: Agosto de 2026  
> **Contexto**: O Revenue SDR OS precisa garantir atendimento comercial instantâneo via WhatsApp (Z-API), renderização hypermedia ultrarrápida (HTMX/Alpine) e processamento assíncrono fluido de áudio e inteligência artificial, mantendo consumo de memória enxuto no ambiente de VPS dedicada.

---

## 1. Visão de Performance e SLAs

Para entregar uma experiência comercial impecável, o sistema estabelece **Limites Máximos de Latência (SLAs no P95)** para cada camada de processamento:

| Camada / Operação | SLA Alvo (P95) | Mecanismo de Garantia |
|---|---|---|
| **Query Banco Local (Turso/libSQL)** | **$< 10\text{ ms}$** | SQLite em memória/arquivo local `.db` com índices compostos `(organization_id, id)` |
| **Resposta de Rota HTTP (API / HTMX)** | **$< 50\text{ ms}$** | FastAPI com rotas finas assíncronas + Jinja2 pre-compiled templates |
| **Evento SSE Server-Sent Events** | **$< 100\text{ ms}$** | Broker de mensagens in-memory assíncrono com fan-out leve |
| **Ingestão Webhook Zap (Z-API)** | **$< 300\text{ ms}$** | Handshake HTTP 200 OK imediato + delegação do payload para worker ARQ |
| **Transcrição de Áudio (Whisper)** | **$< 1,500\text{ ms}$** | Chamada otimizada Groq Whisper Large v3 / OpenAI API |
| **Resposta Completa Agente SDR (LLM)** | **$< 1,200\text{ ms}$** | Prompt Caching nativo + roteamento para modelos rápidos (Gemini 1.5 Flash) |

---

## 2. Decisões Técnicas de Performance

### 2.1 Indexação de Banco de Dados e Leitura Local (Hot Storage)
- O Turso (libSQL) opera localmente na VPS via arquivo `.db` isolado.
- Todas as tabelas possuem índices cobrindo as chaves de busca mais frequentes:
  - `idx_leads_org_phone` em `(organization_id, phone)`
  - `idx_conversations_org_lead` em `(organization_id, lead_id)`
  - `idx_messages_conv_created` em `(conversation_id, created_at DESC)`
- Queries analíticas pesadas são vetadas no banco local do atendimento ao vivo; o histórico consolida no PostgreSQL / Supabase DW em background (ADR-015).

### 2.2 Otimização de Assets e Server-Side Rendering
- Assets CSS (Tailwind + DaisyUI) e JS (HTMX + Alpine.js) são **vendored localmente** e comprimidos via `gzip/brotli` no middleware estático.
- Troca de temas do White-Label realizada estritamente via injeção de variáveis CSS no `<html data-theme="...">`, garantindo tempo de troca de tema $< 1\text{ ms}$ sem re-renderizar JavaScript.

### 2.3 Gestão FinOps e Otimização de LLMs
- **Prompt Caching**: Utilização de chaves de cache em system prompts e bases RAG, reduzindo o tempo de pré-enchimento em até 80%.
- **Compressão de Janela de Contexto**: Manutenção de histórico recente em janela deslizante (últimos 6 turnos) combinada a atributos estruturados extraídos pelo Memory Brain.
- **Roteamento Inteligente (Multi-Tier LLM Router)**:
  - Tarefas de extração/classificação: Modelos super-rápidos e econômicos (Gemini 1.5 Flash-Lite).
  - Conversa ativa: Gemini 1.5 Flash (Standard) ou Claude 3.5 Sonnet (High Stakes).

---

## 3. Consequências

- **Vantagens**:
  - Atendimento comercial em tempo real sem atrasos visíveis para o lead.
  - Baixo consumo de CPU/RAM nas VPSs dedicadas dos clientes.
  - Custos operacionais previstos e otimizados via FinOps.

- **Mitigações & Cuidados**:
  - Nenhum I/O de rede síncrono ou chamada externa pode ser executada dentro do fluxo primário de ingestão do webhook sem timeout rigoroso.
