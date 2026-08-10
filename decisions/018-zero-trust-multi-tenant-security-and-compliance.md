# ADR-018 — Zero-Trust Multi-Tenant Security, Auth Hardening, and LGPD Compliance

> **Status**: Aceito  
> **Data**: Agosto de 2026  
> **Contexto**: O Revenue SDR OS lida com dados comerciais sensíveis, históricos de conversas em canais como WhatsApp, e credenciais de tenants. O modelo de infraestrutura On-Premise-as-a-Service exige garantia de isolamento absoluto entre tenants e conformidade nativa com a LGPD.

---

## 1. Contexto e Desafio de Segurança

Em arquiteturas multi-tenant e On-Premise-as-a-Service:
1. **Risco de Cross-Tenant Leakage**: Erros em queries SQL sem filtro por tenant podem expor conversas e dados comerciais de um cliente para outro.
2. **Vulnerabilidades de Autenticação Legadas**: Bibliotecas de senhas desatualizadas (ex: passlib) ou de tokens JWT com falhas conhecidas (ex: python-jose CVE-2024-33663/64) representam riscos críticos.
3. **Conformidade LGPD**: Leads têm o direito de requerer anonimização ou exclusão de dados, enquanto o sistema precisa manter logs de auditoria imutáveis sem violar regras de privacidade.
4. **Vazamento de Metadados via Erros**: Respostas de erro HTTP 403 Forbidden ou "Access Denied" revelam a existência de registros de outros tenants.

---

## 2. Decisões de Arquitetura de Segurança

### 2.1 Isolamento Zero-Trust com ContextVar no ASGI Middleware
- Toda requisição HTTP passa pelo `TenantResolutionMiddleware`, que valida a identidade da `Organization` através de subdomínio, `custom_domain`, ou header seguro.
- O `organization_id` resolvido é injetado em uma `ContextVar` imutável no escopo da requisição.
- Toda query no banco de dados via `SQLModel` / `SQLAlchemy` utiliza obrigatoriamente um mixin `TenantMixin` que exige e valida a presença de `organization_id`.
- Tentativas de acesso cross-tenant por ID retornam um **404 Not Found genérico**, impedindo que atacantes confirmem a existência de IDs em outras organizações.

### 2.2 Autenticação Hardened e Gestão de Sessões
- **Criptografia de Senhas**: Adoção estrita de **Argon2id** via `pwdlib` (atendendo às diretrizes mais recentes da OWASP).
- **Tokens de Sessão**: Utilização de **PyJWT (HS256)** gerando tokens criptografados com claims obrigatórios: `sub` (ID do usuário), `org` (ID do tenant), `type=session` e um `jti` (JWT ID UUID unique) para controle de revogação.
- **Armazenamento Seguro de Tokens**: Transporte duplo via Cookie HttpOnly `rsdros_session` (com `SameSite=Lax` e `Secure` em produção) para navegação hypermedia HTMX, e header `Authorization: Bearer` para APIs de clientes/integrações.

### 2.3 Gestão de Dados e Compliance LGPD
- **Soft Delete**: A exclusão de registros comerciais de leads ou conversas marca `status='deletado'` e oculta os registros das buscas de rotina.
- **Anonimização de Leads**: Quando solicitado pelo titular, os dados pessoais (nome, telefone, e-mail) são sobrescritos com hashes irreversíveis mantendo os IDs imutáveis para integridade referencial da timeline de eventos.
- **Headers de Segurança e CSP**: Injeção automática via `SecurityHeadersMiddleware` dos cabeçalhos OWASP:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Content-Security-Policy: script-src 'self' 'unsafe-eval'` (assets JS localmente vendored).

---

## 3. Consequências

- **Vantagens**:
  - Isolamento matemático e de processo entre organizações.
  - Zero exposição de metadados em respostas de erro.
  - Alinhamento total com as exigências de privacidade da LGPD.
  - Proteção contra os vetores de ataque OWASP Top 10 API Security.

- **Mitigações & Cuidados**:
  - Toda nova query ou service criado DEVE conter o filtro explícito de `organization_id` validado pela suíte de testes de isolamento (`tests/test_tenant_isolation.py`).
