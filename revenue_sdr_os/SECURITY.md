# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**NAO** abra issue publica para vulnerabilidades de seguranca.

Envie email para **team@myraos.com** com:

1. Descricao da vulnerabilidade
2. Passos para reproduzir
3. Impacto potencial
4. Sugestao de fix (se houver)

Resposta esperada em ate 48h.

## Security Best Practices

Se voce esta fazendo deploy do Revenue SDR OS:

### 1. SECRET_KEY

**SEMPRE** gere uma chave forte em producao:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Configure via env var `SECRET_KEY`. NUNCA commite no git.

### 2. HTTPS

Em producao, **SEMPRE** use HTTPS. Configure:
- Reverse proxy (Caddy, Nginx, Traefik) com SSL
- Let's Encrypt para certificado
- Cookie `Secure=true` (ja configurado em prod)

### 3. Banco de dados

- Backups diarios (criptografados)
- Acesso restrito (firewall, VPN)
- Credenciais em vault (nao .env em prod)

### 4. Updates

- Subscribe a releases do GitHub
- Aplique security patches imediatamente
- Rode em versao suportada

### 5. Multi-tenancy

- Cada tenant isolado por `organization_id`
- **SEMPRE** filtrar queries por tenant
- Testes de regressao (`tests/test_tenant_isolation.py`) devem passar

### 6. LGPD

- Dados isolados por VPS (white-label) ou por row (multi-tenant)
- Termos de uso customizaveis por tenant
- Direito ao esquecimento implementado
- Logs de auditoria para acoes sensiveis

## Known Security Considerations

- **JWT e stateless**: logout invalida cookie mas token permanece valido ate expirar. Para revogacao imediata, implementar blacklist com `jti` (ja preparado).
- **SQLite WAL**: arquivo .db pode ser copiado. Em prod, considere criptografia em repouso.
- **WhatsApp Z-API**: nao-oficial, Meta pode bloquear. Mitigacao: provider abstraido, migracao para Twilio/Cloud API possivel.

## Contact

- **Email**: team@myraos.com
- **PGP**: (TODO: adicionar chave PGP publica)

---

Obrigado por ajudar a manter o Revenue SDR OS seguro!