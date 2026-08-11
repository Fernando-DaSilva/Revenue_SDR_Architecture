# ADR-038: Arquitetura Híbrida de Autenticação e Autorização Multi-Tenant (Supabase Auth + Zero-Trust RBAC no FastAPI)

**Status:** Aprovado  
**Data:** 2026-08-11  
**Decisores:** Engenheiro de Segurança Principal, Arquiteto de Sistemas Backend, Engenheiro Lead Frontend & UX, Líder de DevOps & FinOps  
**Tags:** `auth`, `authorization`, `rbac`, `multi-tenant`, `supabase`, `fastapi`, `jwt`, `rls`, `clerk`

---

## 1. Contexto e Problema

O **Revenue SDR OS** opera como um sistema comercial autônomo e de alta velocidade para prospecção, atendimento e qualificação de leads via WhatsApp e canais digitais. O sistema atende duas interfaces primárias:
1. **Admin OS (`01_SDR_Prototype`)**: Dashboard de gestão, configuração de playbooks, métricas de equipe e administração comercial, construído com renderização no servidor (Jinja2/HTMX) e componentes Alpine.js locais vendored (ADR-011, ADR-013).
2. **Zap Copilot (`02_ZAP_Prototype`)**: Sub-aplicação micro-app standalone em grid 3 colunas para operadores SDR e vendedores, priorizando atendimento em tempo real, alternância de modo (Copilot IA vs SDR Humano), players de áudio Whisper e atualização via WebSockets/SSE (ADR-017).

Com a migração para a arquitetura de **PostgreSQL Unificado no Supabase (ADR-036 e ADR-037)**, tornou-se imperativo definir formalmente a estratégia e os provedores de **Autenticação (AuthN)** e **Autorização (AuthZ)** do sistema.

### Comparativo de Alternativas Avaliadas: Clerk vs. Supabase Auth vs. FastAPI Auth Nativo

| Dimensão Técnica | **Clerk (Third-Party SaaS)** | **Supabase Auth (Provedor Nativo)** | **FastAPI Auth Nativo (Argon2id/PyJWT)** |
|---|---|---|---|
| **Integração com Supabase RLS** | Complexa (exige sincronização de chaves de assinatura JWT e webhooks contínuos) | **Nativa (100% direta)**: `auth.uid()` e `auth.jwt()` integrados à engine PostgreSQL | Requer injeção manual via variáveis de sessão (`app.current_organization_id`) |
| **Compatibilidade SSR (HTMX / Jinja2)** | Baixa (orientado a SDKs React/Next.js client-side) | **Alta**: suporta transporte duplo (HttpOnly Cookies `rsdros_session` + Bearer Headers) | **Alta**: controle total do middleware e cookies |
| **Micro-App Zap Copilot (`02_ZAP_Prototype`)** | Requer SDK pesado JS ou wrapper iframe | **Ideal**: JWT Bearer ultra-leve consumido diretamente por `app.js` | **Ideal**: JWT Bearer ultra-leve |
| **Segurança Supabase Storage & Realtime** | Exige regras customizadas complexas via webhook sync | **Nativa**: Buckets de áudio/mídia do WhatsApp e CDC Realtime usam a mesma Auth | Exige tokens adicionais para acessar Supabase Storage |
| **Modelagem Multi-Tenant (Organizations)** | Padrão Clerk Orgs (preso a dados na nuvem da Clerk) | **Customizável**: `user_organizations` + Custom Access Token Hooks no Postgres | **Customizável**: tabela SQLModel local `organization_id` (ADR-018) |
| **Custos FinOps & Escala** | Elevado (cobrança por MAU que escala rapidamente com SDRs) | **Zero custo adicional**: Incluído na plataforma gerenciada Supabase (ADR-037) | Zero custo adicional (computação VPS) |
| **Soberania de Dados & LGPD** | Dados de credenciais e membros em servidores de terceiros | **Dados 100% no PostgreSQL** do projeto no Supabase | Dados 100% no PostgreSQL |
| **Resiliência & White-Label Custom Domains** | Custom domains pagos por tenant no plano enterprise | **Nativo**: Suporta SMTP próprio, custom domain e OAuth customizado por tenant | **Nativo**: Suporte completo no backend |

---

## 2. Decisão da Equipe de Engenharia

Adotar a **Arquitetura Híbrida de Autenticação e Autorização Multi-Tenant**, combinando **Supabase Auth** como Identity Provider (IdP) e Provedor de Segurança de Dados, com o **FastAPI Zero-Trust Security Gateway** para aplicação de RBAC/ABAC granular.

### Pilares da Arquitetura Aprovada:

1. **Supabase Auth como Identity & Core Token Provider**:
   - O Supabase Auth gerencia identidades (`auth.users`), emissão de JWTs e autenticação social (Google OAuth / SAML Enterprise).
   - Um **PostgreSQL Auth Hook (`custom_access_token_hook`)** no Supabase injeta automaticamente os claims do tenant (`org_id`), papel do usuário (`role`) e permissões ativas (`permissions`) no token JWT no momento do login.

2. **FastAPI Zero-Trust Gateway & Middleware (`TenantResolutionMiddleware` + `AuthService`)**:
   - Valida o token JWT (extraído prioritariamente do cookie HttpOnly `rsdros_session` no Jinja2/HTMX ou do header `Authorization: Bearer` em APIs e no `02_ZAP_Prototype`).
   - Verifica rigorosamente se o claim `org_id` do JWT corresponde à `Organization` resolvida para o request (`ContextVar` `current_organization`). Em caso de incompatibilidade ou tentativa de cross-tenant access, retorna **404 Not Found genérico** (ADR-018).

3. **Supabase PostgreSQL Row-Level Security (RLS) em Profundidade**:
   - Todas as tabelas operacionais possuem `ENABLE ROW LEVEL SECURITY;`.
   - As políticas RLS no Postgres garantem isolamento no nível do banco de dados validando:
     ```sql
     (organization_id = (current_setting('app.current_organization_id', true))::uuid)
     OR
     (organization_id = ((auth.jwt() ->> 'org')::uuid))
     ```

4. **Matriz Granular de Autorização (RBAC / ABAC)**:
   - Papéis definidos: `SUPER_ADMIN` (Gestão de Infra/VPS), `ADMIN` (Dono do Tenant/Configurações), `MANAGER` (Líder de Vendas/Playbooks), `SDR_OPERATOR` (Vendedor/Operador do Zap Copilot), `VIEWER` (Auditor/Leitura).
   - O controle de acesso por rota e por componente UI é guiado por decorators de permissão no FastAPI (`@require_permission(...)`) e helpers no Jinja2/Alpine.js.

5. **Propagação de Tenancy em Workers Assíncronos (Taskiq)**:
   - Mantida a obrigatoriedade do `TenantTaskiqMiddleware` (ADR-030) para serializar `organization_id`, `user_id` e claims de autorização nos workers em background.

---

## 3. Consequências

### Positivas:
- **Integração Total com a Stack Supabase**: RLS, Storage de áudios (WhatsApp/Whisper) e Supabase Realtime utilizam um único modelo unificado de segurança.
- **Experiência Perfeita em Ambos os Protótipos**:
  - `01_SDR_Prototype`: Navegação fluida via cookies HttpOnly com personalização White-Label (ADR-013).
  - `02_ZAP_Prototype`: Operação instantânea no Zap Copilot via token Bearer sem retrabalho de autenticação.
- **Eficiência Financeira (FinOps)**: Elimina mensalidades variáveis de provedores externos como Clerk.
- **Conformidade LGPD & Soberania**: Credenciais e hashes de senhas sob total controle do projeto no PostgreSQL Supabase.

### Negativas / Mitigações:
- **Configuração Inicial do Auth Hook no Supabase**: Requer a criação do script SQL do `custom_access_token_hook` na inicialização do banco. *Mitigado*: O script faz parte da migration inicial do Alembic/Supabase CLI (`supabase migration`).
