# Architecture Decision Records (ADRs)

Este diretório contém os registros de decisões arquiteturais importantes do projeto Revenue SDR OS.

## Lista de Decisões

* **ADR-001** — HTMX + Alpine.js, NÃO React/Vue/Next (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-002** — SQLite (WAL) primeiro, NÃO Postgres no MVP (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-003** — Z-API para Zap no MVP (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-004** — VPS dedicada por cliente, NÃO SaaS compartilhado (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-005** — SSE, NÃO WebSocket (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-006** — Argon2id + PyJWT, NÃO passlib/python-jose (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-007** — App factory + service layer (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-008** — Envelope de erros único (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-009** — Tenant por middleware ASGI puro + ContextVar (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-010** — Alembic desde o dia zero (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-011** — Assets frontend vendored, NÃO CDN (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-012** — Validação nos schemas, NÃO nos table models (definido em [ARCHITECTURE.md](../ARCHITECTURE.md))
* **ADR-013** — [Customização de Idiomas por Tela/Usuário e Presets de Cores no White-Label](013-white-label-localization-and-presets.md)
* **ADR-014** — [Logs Estruturados e Observabilidade](014-system-logs-observability.md)
* **ADR-015** — [Arquivamento de Dados e Exportação Analítica (ETL / DW)](015-data-archiving-and-analytics-export.md)
* **ADR-016** — [Adoção do Turso (libSQL) com Suporte a Embedded Replicas e Fallback Local](016-turso-libsql-database-evolution.md)
* **ADR-017** — [Standalone Zap SDR Micro-App, Grid de Painéis 3 Colunas e Protocolo de Auto-Sync em Background](017-standalone-zap-micro-app-sync-protocol.md)


