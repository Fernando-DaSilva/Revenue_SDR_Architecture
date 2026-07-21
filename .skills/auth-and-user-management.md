---
name: auth-and-user-management
description: |
  Instruções para o Coder implementar autenticação (sign-up, login, forget-password)
  e administração de usuários no Revenue SDR OS de forma segura e multi-tenant.
version: 1.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# Guia do Coder: Autenticação, Redefinição e Gestão de Usuários Multi-Tenant

Carregue esta skill sempre que for criar, modificar ou testar fluxos de autenticação, login, logout, recuperação de senhas ou gerenciamento de usuários.

---

## 1. Princípios de Segurança e Isolamento

```
1. Senhas são SEMPRE tratadas com Argon2id (via pwdlib).
2. O JWT contém o organization_id (claim 'org') e o user_id (claim 'sub').
3. O middleware resolve a organização do request. A dependência CurrentUser deve
   garantir que JWT.org == request.state.organization.id.
4. Qualquer tentativa de login cruzado (cross-tenant) deve retornar 401 sem revelar a existência.
5. Soft Delete: Usuários inativados recebem status = "inactive". Nunca DELETE fisicamente da tabela.
```

---

## 2. Receitas de Código (Templates de Implementação)

### A. Dependência de Autenticação (`app/auth/dependencies.py`)

Garante que o token seja validado e pertença à organização ativa no contexto do request.

```python
from fastapi import Request, Depends
from app.core.errors import AuthenticationError, NotFoundError
from app.auth.service import AuthService
from app.db.session import DbSession
from app.users.models import User

async def get_current_user(
    request: Request,
    session: DbSession,
) -> User:
    """Extrai session do cookie ou Bearer token, valida tenant context."""
    # 1. Obter token do Cookie (precedência) ou do Header Authorization
    token = request.cookies.get("rsdros_session")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise AuthenticationError("Not authenticated")

    # 2. Decodificar JWT
    auth_service = AuthService(session)
    payload = auth_service.decode_jwt(token)  # levanta AuthenticationError se expirado/inválido
    
    user_id = payload.get("sub")
    token_org_id = payload.get("org")

    # 3. Validar se o Tenant da URL/Contexto bate com o do Token
    current_org = request.state.organization
    if not current_org or token_org_id != current_org.id:
        raise AuthenticationError("Token organization mismatch")

    # 4. Obter usuário dentro do Tenant ativo
    user = auth_service.get_user_by_id_and_org(user_id=user_id, org_id=current_org.id)
    if not user or user.status == "inactive":
        raise AuthenticationError("User not found or inactive")

    return user
```

### B. Login com Autenticação Dupla (`app/auth/api.py`)

Entrega o token JWT tanto na resposta JSON quanto em um Cookie HttpOnly seguro para navegação browser.

```python
from fastapi import APIRouter, Response, Depends, status
from app.core.errors import AuthenticationError
from app.db.session import DbSession
from app.auth.schemas import LoginRequest, LoginResponse
from app.auth.service import AuthService
from app.auth.dependencies import CurrentOrganization

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    session: DbSession,
    organization: CurrentOrganization,
):
    """Executa login isolado por tenant."""
    auth_service = AuthService(session)
    
    # Busca usuário filtrando estritamente por organization_id do contexto
    user = auth_service.authenticate_user(
        email=payload.email,
        password=payload.password,
        organization_id=organization.id
    )
    if not user:
        raise AuthenticationError("Authentication failed")

    token = auth_service.create_access_token(user_id=user.id, org_id=organization.id)

    # Configura o cookie seguro HttpOnly
    response.set_cookie(
        key="rsdros_session",
        value=token,
        httponly=True,
        secure=True,  # Deve ser True em produção (configurado dinamicamente via settings)
        samesite="lax",
        path="/",
    )

    return LoginResponse(access_token=token, token_type="bearer", user=user)
```

### C. Redirecionamento de Sessão Expirada com HTMX

HTMX faz requisições assíncronas via AJAX. Se a sessão expirar, o navegador não redirecionará automaticamente se receber um status `302` tradicional. O Coder deve usar o header `HX-Redirect` nas rotas do browser se a requisição for HTMX.

```python
# app/core/middleware.py ou dependência web
from fastapi import Request, Response
from fastapi.responses import RedirectResponse

def handle_web_auth_failure(request: Request, exc: Exception):
    """Trata falha de autenticação em rotas HTML de forma amigável para HTMX."""
    login_url = "/auth/login"
    
    # Se a requisição veio do HTMX, retorna redirecionamento via Header
    if request.headers.get("HX-Request"):
        return Response(headers={"HX-Redirect": login_url})
    
    # Requisição tradicional do navegador
    return RedirectResponse(login_url)
```

---

## 3. Gestão de Usuários (Administração por Tenant)

As seguintes invariantes devem ser seguidas nas tabelas e queries de Usuários:

1. **Unique Email per Tenant**:
   O model `User` deve definir uma UniqueConstraint composta:
   ```python
   class User(TenantMixin, table=True):
       __tablename__ = "users"
       # ...
       email: str = Field(nullable=False)
       status: str = Field(default="active")  # active, inactive
       preferred_locale: str = Field(default="pt-BR")
       role: str = Field(default="sdr")       # admin, manager, sdr

       # Unique constraint de email isolada por tenant
       __table_args__ = (
           UniqueConstraint("organization_id", "email", name="uq_users_org_email"),
       )
   ```

2. **Queries Isoladas (Service)**:
   ```python
   def get_user_in_org(self, user_id: str, organization_id: str):
       # Sempre force o filtro de organization_id. Retorne None se não pertencer.
       statement = select(User).where(
           User.id == user_id,
           User.organization_id == organization_id
       )
       return self.session.exec(statement).first()
   ```

3. **Soft Delete**:
   ```python
   def deactivate_user(self, user_id: str, organization_id: str) -> bool:
       user = self.get_user_in_org(user_id, organization_id)
       if not user:
           return False
       user.status = "inactive"
       self.session.add(user)
       self.session.commit()
       return True
   ```

---

## 4. Estratégia de Testes do Coder

Toda alteração de auth e usuários deve incluir testes em `tests/` que validem:

1. **Login isolado**: Usuário do `tenant_a` não pode logar em `tenant_b.localhost:8000/api/v1/auth/login`.
2. **Uso de Token Alheio**: Chamar endpoints de `tenant_b` portando um JWT de `tenant_a` deve resultar em `401 Unauthorized`.
3. **Prevenção de Enumeração de Email**: O endpoint de `forget-password` deve retornar `200 OK` com a mesma mensagem de sucesso, mesmo se o e-mail não estiver cadastrado.
4. **Proteção de Role (RBAC)**: Testar se um usuário com papel `Role.SDR` recebe `403 Forbidden` (via `PermissionDeniedError`) ao tentar acessar `/api/v1/users` para listar os usuários do tenant.
5. **Soft Delete**: Validar que após um "delete" no usuário, seu status no banco vira `inactive` e ele não consegue mais se autenticar (retorna `401` no login ou uso de token antigo).
