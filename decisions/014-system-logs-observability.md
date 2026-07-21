# ADR-014 — Logs Estruturados e Observabilidade (JSON, Tracing)

- **Status:** Aceito (Sprint 00 / Implementação na Sprint 05)
- **Data:** 2026-07-21

## Contexto e Problema

Para operar o **Revenue SDR OS** em produção (especialmente na arquitetura de múltiplas VPS ou instâncias SaaS com dezenas de tenants), identificar problemas, gargalos de performance e erros exige uma estratégia de log madura. Atualmente o sistema usa saídas padrão ou `print()`, o que dificulta a ingestão, parse e busca em ferramentas agregadoras de log (ELK, Datadog, Loki, CloudWatch) e inviabiliza o rastreamento (tracing) ponta-a-ponta de requisições web.

Além do backend, precisamos rastrear o comportamento do usuário e erros críticos que ocorrem no *Client-side (Frontend)* e durante o trânsito nos *Middlewares* (camada de multi-tenancy e HTTP).

## Decisão

Implementar um padrão de **Logs Estruturados em JSON** (Structured Logging) para toda a aplicação e estabelecer um fluxo de **Tracing (Rastreamento Contextual)**, seguindo estas diretrizes:

### 1. Formato Universal (JSON Lines)
Todo output de log oficial do sistema (stdout/stderr) deve ser emitido obrigatoriamente no formato JSON Lines (`{"level": "...", "message": "...", "context": {...}}`).
- **Biblioteca sugerida:** `structlog` no Python (Backend).

### 2. Tracing e Contexto Obrigatório
Toda entrada de log gerada no ciclo de vida de um request HTTP deve propagar metadados fundamentais (Correlation IDs):
- `request_id`: UUID único gerado no Middleware para identificar o ciclo de vida daquela chamada (permitindo rastrear desde o Middleware, Service, BD, até resposta LLM).
- `tenant_id` (ou `organization_id`): ID do tenant contextualizado.
- `user_id`: Se autenticado, o ID do usuário disparando a ação.
- `timestamp`: Sempre em formato ISO-8601 UTC.

### 3. As Três Camadas de Logs

#### A. Logs de Frontend (Client-side)
- Erros de JavaScript (`window.onerror`), alertas de quebra de componentes Alpine.js/HTMX e métricas chaves de Web Vitals (CWV) deverão ser capturadas e enviadas de forma coalescida via beacon.
- **Implementação:** Criação de um endpoint no backend `POST /api/v1/logs/client` projetado para ingerir silenciosamente esses dados e emiti-los no console JSON do servidor, incluindo metadados (User-Agent, URL, Resolução).

#### B. Logs de Middleware (HTTP Access Logs)
- O `TenantResolutionMiddleware` (ou um middleware específico de Logger) interceptará cada request e emitirá um evento `http_request_finished`.
- **Payload:** Método HTTP, Path, Status Code, duração em milissegundos (latency), IP de origem e `tenant_id` inferido.

#### C. Logs de Backend e Domínio
- Exceções e erros tratados (especialmente as geradas por `AppError`) deverão gerar logs de `ERROR` com a stacktrace incorporada no campo `exception`.
- **Logs Especiais:** Operações críticas (ex: chamadas externas de LLM, queries lentas de BD, processamento de webhooks do Z-API) devem emitir logs INFO explícitos contendo tempo de execução, tokens consumidos e identificadores do provedor.
- **Audit Logs:** Eventos de manipulação de leads sensíveis ou alterações de permissões de tenant serão parte destes logs estruturados, classificados com a chave especial `event_type: "audit"`.

## Consequências

- **Positivas:** 
  - Consultas simplificadas no provedor de observabilidade (ex: `tenant_id=XYZ AND status_code>=500`).
  - Preparação e compatibilidade nativa para adoção futura do ecossistema **Grafana (Loki)**, permitindo unificar e cruzar logs estruturados com métricas do Prometheus em painéis (Dashboards) avançados de análise.
  - Depuração rápida rastreando toda a cascata de um `request_id`.
  - Insights de negócios e performance combinando dados técnicos de LLM (tokens) com logs de operação.
- **Negativas:** 
  - Maior verbosidade da saída no console durante o desenvolvimento local. (Recomenda-se configurar a ferramenta de log para renderizar JSON bonificado/legível quando `ENVIRONMENT=development`).
  - O endpoint `/api/v1/logs/client` precisará de *rate-limiting* estrito e payload cap para prevenir ataques de negação de serviço e sobrecarga de escrita.

## Implementação

Esta infraestrutura documental faz parte da Sprint 00, enquanto a **implementação da biblioteca, do endpoint `/api/v1/logs/client` e das injeções de middleware** acontecerão nativamente na **Sprint 05**, juntamente à métricas do Prometheus.
