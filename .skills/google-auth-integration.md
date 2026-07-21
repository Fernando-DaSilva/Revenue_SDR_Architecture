---
name: google-auth-integration
description: |
  Instruções para o Coder implementar autenticação opcional com Google (Sign-up/Login)
  integrada ao fluxo JWT multi-tenant e isolamento do Revenue SDR OS.
version: 1.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# Guia do Coder: Integração de Google Sign-up e Login Multi-Tenant

Carregue esta skill sempre que for implementar ou testar fluxos de autenticação (Sign-up de novos Tenants ou Login em Tenants existentes) utilizando contas Google de forma integrada ao sistema.

---

## 1. Princípios de Integração e Segurança

```
1. Decodificação e Validação: O backend deve SEMPRE validar a assinatura do ID Token
   do Google recebido do frontend utilizando as chaves públicas (JWKS) oficiais do Google.
2. Isolamento de Tenant: A autenticação do Google ocorre obrigatoriamente no contexto
   do tenant atual (exceto no cadastro de nova organização). Chamar o login do Google no
   Tenant A com um e-mail cadastrado apenas no Tenant B deve resultar em 401.
3. Compatibilidade: O resultado final de um login via Google deve ser a emissão do mesmo
   cookie HttpOnly `rsdros_session` contendo o JWT nativo com claims 'sub' e 'org'.
4. Sem Senha Nativa: Usuários criados via Google não possuem senha nativa inicial. O campo
   de senha no banco deve ser opcional (nullable) ou preenchido com um hash inválido/bloqueado
   (ex: "!google_auth_disabled_pwd") para impedir bypass de login nativo.
```

---

## 2. Alteração de Schema (SQLModel + Alembic)

Adicione os campos no model `User` para vincular a conta do Google de forma isolada por tenant:

```python
# app/users/models.py
from sqlmodel import Field, SQLModel, UniqueConstraint
from app.db.base import TenantMixin

class User(TenantMixin, table=True):
    __tablename__ = "users"
    
    # ... campos existentes (id, email, role, preferred_locale, etc.) ...
    
    # Campo opcional para senha nativa
    password_hash: str | None = Field(default=None, nullable=True)
    
    # Campos do provedor de identidade social
    auth_provider: str = Field(default="native", nullable=False)  # "native", "google"
    google_id: str | None = Field(default=None, nullable=True)

    __table_args__ = (
        UniqueConstraint("organization_id", "email", name="uq_users_org_email"),
        # Garante que um ID do Google só se vincule a uma conta dentro do mesmo tenant
        UniqueConstraint("organization_id", "google_id", name="uq_users_org_google_id"),
    )
```

---

## 3. Validação do ID Token do Google

O frontend envia o `google_id_token` obtido via Google Sign-In / One Tap no payload. O backend deve validar:

### Opção A: Utilizando a biblioteca `google-auth` (Recomendado)
```python
# app/auth/google_verifier.py
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.errors import ValidationError

def verify_google_token(token: str, client_id: str) -> dict:
    """Valida o ID token e retorna o payload com informações do usuário."""
    try:
        # requests.Request() gerencia cache dos certificados do Google automaticamente
        id_info = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        
        # Validar o issuer do token
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValidationError("Wrong issuer.")
            
        return id_info
    except Exception as e:
        raise ValidationError(f"Invalid Google ID Token: {str(e)}")
```

### Opção B: Validação Pura com `PyJWT` (Sem dependências externas pesadas)
```python
import jwt
import requests
from app.core.errors import ValidationError

GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"

def verify_google_token_jwt(token: str, client_id: str) -> dict:
    try:
        # Obter JWKS público do Google (em produção, cachear esta resposta)
        jwks = requests.get(GOOGLE_CERTS_URL).json()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        # Encontrar a chave correspondente ao 'kid' do token
        public_key = None
        for key in jwks["keys"]:
            if key["kid"] == kid:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break
                
        if not public_key:
            raise ValidationError("Invalid kid key ID.")
            
        # Decodificar e validar
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=client_id,
            issuer="https://accounts.google.com"
        )
        return payload
    except Exception as e:
        raise ValidationError(f"Invalid Google token validation: {str(e)}")
```

---

## 4. Endpoints e Serviços (Receitas de Código)

### A. Login com Google (`app/auth/api.py`)

```python
from fastapi import APIRouter, Response, Depends, status
from app.core.errors import AuthenticationError
from app.db.session import DbSession
from app.auth.schemas import GoogleLoginRequest, LoginResponse
from app.auth.service import AuthService
from app.auth.dependencies import CurrentOrganization

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login/google", response_model=LoginResponse)
async def login_google(
    payload: GoogleLoginRequest,
    response: Response,
    session: DbSession,
    organization: CurrentOrganization,
):
    """Executa login social com o Google associando ao tenant ativo."""
    auth_service = AuthService(session)
    
    # 1. Valida o ID Token recebido e extrai informações do Google
    # Em produção, o CLIENT_ID vem de settings.google_client_id
    google_data = auth_service.verify_google_token(
        token=payload.google_id_token,
        client_id=auth_service.settings.GOOGLE_CLIENT_ID
    )
    
    google_id = google_data["sub"]
    email = google_data["email"]

    # 2. Busca ou vincula o usuário no tenant do contexto
    user = auth_service.authenticate_google_user(
        google_id=google_id,
        email=email,
        organization_id=organization.id
    )
    if not user:
        raise AuthenticationError("User not found or registration not allowed.")

    # 3. Emite tokens e configura cookies idêntico ao login nativo
    token = auth_service.create_access_token(user_id=user.id, org_id=organization.id)
    
    response.set_cookie(
        key="rsdros_session",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )

    return LoginResponse(access_token=token, token_type="bearer", user=user)
```

### B. Lógica de Autenticação/Associação no `AuthService` (`app/auth/service.py`)

```python
from sqlmodel import select
from app.users.models import User
from app.core.errors import AuthenticationError

class AuthService:
    # ... métodos existentes ...

    def authenticate_google_user(self, google_id: str, email: str, organization_id: str) -> User | None:
        """Autentica usuário do Google e trata auto-vínculo com conta nativa."""
        # 1. Buscar usuário pelo google_id isolado no tenant
        statement = select(User).where(
            User.organization_id == organization_id,
            User.google_id == google_id
        )
        user = self.session.exec(statement).first()
        if user:
            if user.status == "inactive":
                raise AuthenticationError("User is inactive")
            return user
            
        # 2. Caso não exista por google_id, buscar por e-mail no tenant para auto-vinculação
        statement = select(User).where(
            User.organization_id == organization_id,
            User.email == email
        )
        user_by_email = self.session.exec(statement).first()
        if user_by_email:
            if user_by_email.status == "inactive":
                raise AuthenticationError("User is inactive")
                
            # Vincula a conta Google ao usuário nativo existente
            user_by_email.google_id = google_id
            if user_by_email.auth_provider == "native":
                # Mantém opcionalmente suporte híbrido ou força migração
                user_by_email.auth_provider = "google"
            self.session.add(user_by_email)
            self.session.commit()
            return user_by_email
            
        return None
```

### C. Cadastro de Organização via Google (`app/auth/api.py`)

```python
@router.post("/signup/google", status_code=status.HTTP_201_CREATED)
async def signup_google(
    payload: GoogleSignupRequest,
    session: DbSession,
):
    """Cria uma nova organização e seu Owner a partir da conta do Google."""
    auth_service = AuthService(session)
    
    # 1. Valida o ID Token do Google
    google_data = auth_service.verify_google_token(
        token=payload.google_id_token,
        client_id=auth_service.settings.GOOGLE_CLIENT_ID
    )
    
    # 2. Cria a nova organização e o usuário proprietário associado
    new_org, new_admin = auth_service.create_organization_with_google_admin(
        org_name=payload.organization_name,
        org_slug=payload.tenant_slug,
        google_id=google_data["sub"],
        email=google_data["email"],
        name=google_data.get("name", "Admin")
    )
    
    return {"status": "created", "organization_id": new_org.id, "user_id": new_admin.id}
```

---

## 5. Estratégia de Testes do Coder

Toda alteração de autenticação social com Google deve conter testes automatizados em `tests/` mockando a validação do token do Google para evitar chamadas de rede reais:

```python
import pytest
from unittest.mock import patch
from app.core.errors import AuthenticationError

def test_login_google_success(client, db_session, seed_organization, seed_user):
    # Mockando a chamada externa ao Google
    with patch("app.auth.service.AuthService.verify_google_token") as mock_verify:
        mock_verify.return_value = {
            "sub": "google_123456789",
            "email": seed_user.email,  # Mesmo e-mail para forçar associação
            "name": "Maria Silva"
        }
        
        # Seta o header do Host do tenant
        headers = {"Host": f"{seed_organization.slug}.localhost:8000"}
        
        response = client.post(
            "/api/v1/auth/login/google",
            json={"google_id_token": "valid_token_mock"},
            headers=headers
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.cookies.get("rsdros_session") is not None
        
        # Validar se o google_id foi persistido no usuário do banco
        db_session.refresh(seed_user)
        assert seed_user.google_id == "google_123456789"

def test_login_google_cross_tenant_block(client, db_session, seed_org_a, seed_org_b, seed_user_a):
    """Usuário do Tenant A não pode usar o Google para logar no Tenant B."""
    with patch("app.auth.service.AuthService.verify_google_token") as mock_verify:
        mock_verify.return_value = {
            "sub": "google_123456789",
            "email": seed_user_a.email,  # E-mail do Tenant A
            "name": "User A"
        }
        
        # Tenta acessar no domínio do Tenant B
        headers = {"Host": f"{seed_org_b.slug}.localhost:8000"}
        
        response = client.post(
            "/api/v1/auth/login/google",
            json={"google_id_token": "valid_token_mock"},
            headers=headers
        )
        
        # Retorna 401 generico para evitar cross-tenant leak
        assert response.status_code == 401
```

---

## 6. Anti-padrões (Evite a todo custo)

```
[X] Confiar em dados do usuário enviados diretamente pelo frontend (ex: POST com {email, google_id}
    sem passar o token e validá-lo no backend).
[X] Não validar o Client ID (Audience) na decodificação do ID token do Google.
[X] Permitir auto-registro de novos usuários no login comum (se o usuário não existe no tenant atual,
    o login deve falhar para proteger a organização de intrusos).
[X] Permitir login do Google sem validar se o tenant ativo no contexto bate com o usuário retornado.
```
