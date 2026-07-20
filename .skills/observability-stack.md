---
name: observability-stack
description: |
  Stack de observabilidade para o Revenue SDR OS. Carregue esta skill quando
  for adicionar Prometheus, Grafana, logs estruturados, ou alertas.
version: 1.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# Observabilidade — Padroes do Revenue SDR OS

## Principio basico

```
"Nunca operar no escuro."

Toda VPS cliente tem metricas + logs + alertas desde o dia 1.
Platform Console agrega metricas de TODAS as VPS.
4 camadas de monitoramento:
  1. Infraestrutura (CPU, RAM, disco, SSL)
  2. Aplicacao FastAPI (latencia, erros, throughput)
  3. Integracoes externas (WhatsApp, OpenAI)
  4. Eventos de negocio (leads, vendas)
```

---

## Stack escolhida

```
+--------------------+----------------------+
| Componente         | Escolha              |
+--------------------+----------------------+
| Metricas           | Prometheus           |
| Visualizacao       | Grafana              |
| Logs               | Loki (v2) / JSON    |
| Tracing            | OpenTelemetry (v2)   |
| Notificacoes       | Alertmanager + TG    |
+--------------------+----------------------+
```

Custo: $0 de licenca (open source). Custo de infra: ~$10/mes.

---

## Prometheus metrics (app/monitoring/metrics.py)

```python
"""
Metricas Prometheus expostas em /metrics.

Sprint 5+: instrumentar aplicacao.
"""
from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    generate_latest, CONTENT_TYPE_LATEST,
)
from fastapi import APIRouter, Response

# === Infraestrutura (coletado por node_exporter, NAO aqui) ===
# CPU, RAM, disco, rede — vem do node_exporter

# === Aplicacao ===

# Latencia por endpoint (histograma)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Latencia de requests HTTP",
    labelnames=["method", "endpoint", "status"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# Total de requests
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total de requests HTTP",
    labelnames=["method", "endpoint", "status"],
)

# Erros 4xx/5xx
REQUEST_ERRORS = Counter(
    "http_request_errors_total",
    "Total de erros HTTP",
    labelnames=["method", "endpoint", "status"],
)

# Requests em andamento
REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Requests atualmente em processamento",
    labelnames=["method", "endpoint"],
)

# === Aplicacao especifica ===

# DB queries lentas
DB_QUERY_LATENCY = Histogram(
    "db_query_duration_seconds",
    "Latencia de queries no banco",
    labelnames=["model", "operation"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
)

# SSE connections ativas
SSE_CONNECTIONS_ACTIVE = Gauge(
    "sse_connections_active",
    "Conexoes SSE ativas",
    labelnames=["type"],  # conversation / organization
)

# Eventos SSE publicados
SSE_EVENTS_PUBLISHED = Counter(
    "sse_events_published_total",
    "Total de eventos SSE publicados",
    labelnames=["type", "event_type"],
)

# === Integracoes externas ===

# WhatsApp (Z-API) — chamadas
WHATSAPP_API_CALLS = Counter(
    "whatsapp_api_calls_total",
    "Total de chamadas a API do WhatsApp",
    labelnames=["operation", "status"],  # operation: send_message | get_status; status: success | error
)

WHATSAPP_API_LATENCY = Histogram(
    "whatsapp_api_duration_seconds",
    "Latencia de chamadas a API do WhatsApp",
    labelnames=["operation"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
)

# OpenAI — tokens e custo
OPENAI_TOKENS = Counter(
    "openai_tokens_total",
    "Total de tokens consumidos pela OpenAI",
    labelnames=["model", "operation"],  # operation: chat | embedding
)

OPENAI_API_COST = Counter(
    "openai_api_cost_dollars_total",
    "Custo total estimado em USD",
    labelnames=["model"],
)

OPENAI_API_LATENCY = Histogram(
    "openai_api_duration_seconds",
    "Latencia de chamadas a API da OpenAI",
    labelnames=["model", "operation"],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
)

# === Eventos de negocio ===

# Leads
LEADS_CREATED = Counter(
    "leads_created_total",
    "Total de leads criados",
    labelnames=["source"],  # whatsapp | site | import | etc
)

# Conversas
CONVERSATIONS_ACTIVE = Gauge(
    "conversations_active",
    "Conversas ativas (mode=ai)",
)

CONVERSATIONS_BY_MODE = Counter(
    "conversations_by_mode_total",
    "Total de transicoes de mode",
    labelnames=["from_mode", "to_mode"],  # ai | human | paused
)

# Vendas (quando implementado)
SALES_CLOSED = Counter(
    "sales_closed_total",
    "Total de vendas fechadas",
    labelnames=["vertical", "channel"],
)


# === FastAPI middleware ===

def setup_metrics_middleware(app):
    """Adiciona middleware que instrumenta todos os requests."""

    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        # Skip /metrics endpoint (evitar recursao)
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        endpoint = request.url.path

        # Incrementa in-progress
        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()

        # Mede latencia
        with REQUEST_LATENCY.labels(method=method, endpoint=endpoint, status="pending").time():
            try:
                response = await call_next(request)
                status_code = response.status_code
            except Exception as e:
                status_code = 500
                REQUEST_ERRORS.labels(method=method, endpoint=endpoint, status="500").inc()
                raise
            finally:
                REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()

        # Conta request
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code),
        ).inc()

        # Conta erro se 4xx/5xx
        if status_code >= 400:
            REQUEST_ERRORS.labels(
                method=method,
                endpoint=endpoint,
                status=str(status_code),
            ).inc()

        return response


# === Endpoint /metrics ===

metrics_router = APIRouter()


@metrics_router.get("/metrics")
async def metrics():
    """Endpoint de metricas Prometheus."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
```

---

## Logger estruturado (app/monitoring/logging.py)

```python
"""
Logging estruturado em JSON.

Todos os logs sao JSON (facilita parsing por Loki/Elasticsearch/etc).
"""
import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formatter que emite logs em JSON estruturado."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Adiciona campos extras (correlation_id, user_id, etc)
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "asctime", "taskName"
            }:
                log_data[key] = value

        # Adiciona exception se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


def setup_logging(level: str = "INFO"):
    """Configura logging estruturado."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Reduz ruido
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root


# Helper para usar em qualquer lugar
logger = logging.getLogger(__name__)


# === Exemplo de uso ===
#
# from app.monitoring.logging import logger
#
# logger.info("Lead created", extra={
#     "tenant_id": org.id,
#     "lead_id": lead.id,
#     "source": "whatsapp",
# })
#
# logger.error("WhatsApp API failed", extra={
#     "tenant_id": org.id,
#     "instance_id": msg.instance_id,
#     "error": str(e),
#     "duration_ms": 1234,
# }, exc_info=True)
```

---

## Wire no app (app/main.py)

```python
# app/main.py (adicionar)
from app.monitoring.metrics import setup_metrics_middleware, metrics_router
from app.monitoring.logging import setup_logging

# Logging (antes de criar app)
setup_logging(level=settings.log_level)

# Setup middleware de metricas
setup_metrics_middleware(app)

# Endpoint /metrics
app.include_router(metrics_router)
```

---

## Prometheus config (deploy/prometheus.yml)

```yaml
# deploy/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

# Storage local (MVP)
storage:
  tsdb:
    path: /prometheus/data
    retention.time: 30d

scrape_configs:
  # Metricas da Platform Console
  - job_name: 'platform-console'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: /metrics

  # Metricas de cada VPS cliente (via pushgateway)
  - job_name: 'pushgateway'
    static_configs:
      - targets: ['localhost:9091']

# Alertmanager
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']
```

---

## Grafana dashboards (provisioning/dashboards/*.yml)

### Dashboard 1: Overview Geral

```json
{
  "dashboard": {
    "title": "Revenue SDR OS - Overview",
    "panels": [
      {
        "title": "Requests per Second (by tenant)",
        "type": "graph",
        "targets": [{
          "expr": "sum(rate(http_requests_total[5m])) by (tenant_id)",
          "legendFormat": "{{tenant_id}}"
        }]
      },
      {
        "title": "Latencia p95 (by endpoint)",
        "type": "graph",
        "targets": [{
          "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint))",
          "legendFormat": "{{endpoint}}"
        }]
      },
      {
        "title": "Error Rate (4xx + 5xx)",
        "type": "graph",
        "targets": [{
          "expr": "sum(rate(http_request_errors_total[5m])) / sum(rate(http_requests_total[5m]))",
          "legendFormat": "error rate"
        }]
      },
      {
        "title": "Active SSE Connections",
        "type": "stat",
        "targets": [{
          "expr": "sum(sse_connections_active)"
        }]
      },
      {
        "title": "OpenAI Cost (USD/dia)",
        "type": "stat",
        "targets": [{
          "expr": "sum(increase(openai_api_cost_dollars_total[24h]))"
        }]
      },
      {
        "title": "Leads Created (by source)",
        "type": "pie",
        "targets": [{
          "expr": "sum by (source) (increase(leads_created_total[24h]))"
        }]
      }
    ]
  }
}
```

### Dashboard 2: Per-VPS Drilldown

```json
{
  "dashboard": {
    "title": "VPS Cliente - Drilldown",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [{"expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)"}]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [{"expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"}]
      },
      {
        "title": "Disk Usage",
        "type": "graph",
        "targets": [{"expr": "(1 - (node_filesystem_avail_bytes{mountpoint='/'} / node_filesystem_size_bytes{mountpoint='/'})) * 100"}]
      },
      {
        "title": "SSL Expiry (days)",
        "type": "stat",
        "targets": [{"expr": "probe_ssl_earliest_cert_expiry - time()"}]
      }
    ]
  }
}
```

### Dashboard 3: Aplicacao (FastAPI)

```json
{
  "dashboard": {
    "title": "FastAPI Metrics",
    "panels": [
      {
        "title": "Latencia p50/p95/p99 por endpoint",
        "type": "graph",
        "targets": [
          {"expr": "histogram_quantile(0.50, ...)", "legendFormat": "p50"},
          {"expr": "histogram_quantile(0.95, ...)", "legendFormat": "p95"},
          {"expr": "histogram_quantile(0.99, ...)", "legendFormat": "p99"}
        ]
      },
      {
        "title": "Top 10 Endpoints Mais Lentos",
        "type": "table",
        "targets": [{
          "expr": "topk(10, histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)))"
        }]
      },
      {
        "title": "DB Query Latencia p95",
        "type": "graph",
        "targets": [{
          "expr": "histogram_quantile(0.95, sum(rate(db_query_duration_seconds_bucket[5m])) by (le, model))"
        }]
      }
    ]
  }
}
```

---

## Alertas Prometheus (deploy/prometheus/alerts.yml)

```yaml
groups:
- name: critical_alerts
  rules:
  # VPS down
  - alert: VPS_Down
    expr: up{job="vps-cliente"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "VPS {{ $labels.instance }} down por mais de 5min"

  # Disco > 85%
  - alert: Disk_Almost_Full
    expr: (1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100 > 85
    for: 10m
    labels:
      severity: warning

  # SSL expira em < 14 dias
  - alert: SSL_Expiring_Soon
    expr: probe_ssl_earliest_cert_expiry - time() < 86400 * 14
    labels:
      severity: warning

  # Erro 5xx > 1%
  - alert: High_Error_Rate
    expr: |
      sum(rate(http_request_errors_total{status=~"5.."}[5m]))
      / sum(rate(http_requests_total[5m]))
      > 0.01
    for: 10m
    labels:
      severity: critical

  # Custo OpenAI > $10/dia por tenant
  - alert: OpenAI_Cost_High
    expr: sum by(tenant_id) (increase(openai_api_cost_dollars_total[24h])) > 10
    labels:
      severity: warning

  # Backup falhou
  - alert: Backup_Failed
    expr: increase(backup_last_success_timestamp_seconds[24h]) > 86400
    labels:
      severity: critical
```

---

## Anti-patterns (NUNCA faca)

```python
# ERRADO: log sem structured fields
logger.info(f"User {user.id} from org {org.id} created lead {lead.id}")

# CERTO: structured logging
logger.info("Lead created", extra={
    "tenant_id": org.id,
    "user_id": user.id,
    "lead_id": lead.id,
    "source": lead.source,
})


# ERRADO: contador sem labels
REQUESTS = Counter("requests_total")

# CERTO: labels para slicing
REQUESTS = Counter("requests_total", "Total", labelnames=["method", "endpoint", "status"])


# ERRADO: medir tempo com time.time()
start = time.time()
result = db.query(...)
DURATION.labels(...).observe(time.time() - start)

# CERTO: usar context manager (cleanup automatico)
with DURATION.labels(...).time():
    result = db.query(...)


# ERRADO: nao versionar metricas (breaking changes sem aviso)
REQUESTS = Counter("requests", "v1")
# depois
REQUESTS = Counter("http_requests_total", "v2")  # NOME mudou!
# Grafana quebra, alertas quebram, etc.


# CERTO: adicionar labels novos, nunca renomear
REQUESTS = Counter("http_requests_total", "Total", labelnames=["method", "endpoint", "status", "tenant_id"])
```

---

## Checklist

```
[ ] Prometheus client exposto em /metrics
[ ] Middleware instrumenta todos os requests (latencia, count, errors)
[ ] Metricas de negocio: leads_created, conversations_active, sales_closed
[ ] Metricas de IA: tokens, custo, latencia
[ ] Logger estruturado em JSON
[ ] Logs com correlation_id (trace 1 request)
[ ] Grafana dashboards provisionados
[ ] Alertas criticos: VPS down, disco cheio, SSL expirando, erros > 1%
[ ] Pushgateway configurado (VPS clientes empurram metricas)
[ ] Multi-tenant: metricas labeladas por tenant_id
[ ] Documentacao de como adicionar novas metricas
```

---

*"Metricas sao a unica forma de saber se o sistema esta vivo."*