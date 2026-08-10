# ADR-025: Estratégia de Caching em Camadas, Rate Limiting e Proteção de Ingestão (Valkey / Redis / In-Memory)

* **Status**: Aprovado
* **Data**: Agosto 2026
* **Autores**: Equipe de Performance, FinOps e Segurança (Revenue SDR OS)

---

## 1. Contexto e Problema

O **Revenue SDR OS** enfrenta três desafios críticos de performance e custo operacional:
1. **Overhead de Carregamento de Tenants e Temas White-Label**: A cada requisição HTTP ou página HTMX renderizada, o sistema precisa resolver a organização (`organization_id`), buscar parâmetros de branding, variáveis de CSS e preferências de idioma. Fazer queries no banco a cada request geraria overhead desnecessário.
2. **Proteção Contra DDoS e Bot Spam**: Endpoints públicos como webhooks do Zap, formulários de captura e a API de ingestão de logs do client-side (`/api/v1/logs/client`) exigem limitação de taxa (*Rate Limiting*) por IP e por `organization_id`.
3. **Estouro de Custos de LLM (FinOps)**: Re-enviar System Prompts extensos ou re-computar memórias frequentes sem reaproveitar resultados intermediários resulta em desperdício de tokens de entrada.

---

## 2. Decisão Arquitetural

Adotar uma **Arquitetura de Caching Híbrida em Duas Camadas (Multi-Tier Caching)** acoplada a um middleware de **Rate Limiting Orientado a Tenant**:

```
Request Inbound (API / Webhook / UI)
   |
   v
+-----------------------------------------------------------------------------------+
| CAMADA 1: IN-MEMORY CACHE (LRU ContextVar Cache)                                  |
|  - Alvo: Configurações de Tenant, Presets de Cores White-Label, Traduções        |
|  - Latência: < 0.1ms | Invalidação: Por eventos de atualização no admin           |
+----------------------------------------+------------------------------------------+
                                         | (Miss)
                                         v
+-----------------------------------------------------------------------------------+
| CAMADA 2: VALKEY / REDIS CACHE (ou DiskCache em VPS Standalone)                   |
|  - Alvo: Sessões ativas, Tokens revogados, Rate Limit counters, Prompt Hash Keys  |
|  - Latência: < 2ms   | Rate Limiter: Window-sliding por Organization & IP        |
+-----------------------------------------------------------------------------------+
```

---

## 3. Especificação do Rate Limiting Multi-Tenant

Para proteger a infraestrutura e controlar o consumo FinOps por cliente:

```python
from fastapi import Request, HTTPException, status
from app.core.cache import cache_provider

class TenantRateLimiter:
    def __init__(self, requests_per_minute: int = 120):
        self.requests_per_minute = requests_per_minute

    async def __call__(self, request: Request):
        # Resolver tenant e IP do cliente
        org = getattr(request.state, "organization", None)
        org_id = org.id if org else "anonymous"
        client_ip = request.client.host if request.client else "unknown"
        
        rate_key = f"rate_limit:{org_id}:{client_ip}:{request.url.path}"
        current_requests = await cache_provider.incr(rate_key, ttl=60)
        
        if current_requests > self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"error": {"code": "rate_limit_exceeded", "message": "Limite de requisições excedido."}}
            )
```

---

## 4. Orçamento de Cache e Políticas de Expiração (TTL)

| Tipo de Dado | Mecanismo de Cache | TTL (Tempo de Vida) | Invalidação |
|---|---|---|---|
| Tema / Cores White-Label | Camada 1 (In-Memory LRU) | 1 hora (3600s) | Ativa no salvamento do formulário de temas |
| Traduções Granulares | Camada 1 (In-Memory LRU) | 2 horas (7200s) | Ativa no painel de idiomas |
| Sessões JWT (`jti`) | Camada 2 (Valkey / Redis) | Duração do Token | Revogação explícita no logout |
| System Prompt Caching | Provider Native (Gemini/OpenAI) | 5 minutos | Automática por inatividade |
| Ingestão Client Logs | Camada 2 (Valkey / Redis) | Sliding Window 60s | Máximo de 30 logs por minuto por IP |

---

## 5. Resiliência e Fallback Standalone

Para manter o requisito inegociável de **VPS Standalone com Custo R$ 0,00 sem dependências obrigatórias**:
- Se o serviço Redis/Valkey não estiver rodando na VPS do cliente, o sistema comuta automaticamente para o driver **`DiskCache` (baseado em arquivo SQLite local `/tmp/cache.db`)**, mantendo 100% da API de cache funcional sem falhas de inicialização.

---

## 6. Invariantes para Agentes de Codificação (AI Coding Guardrails)

1. **SEMPRE** utilizar a abstração `cache_provider` em vez de instanciar clientes Redis diretos no código de domínio.
2. **SEMPRE** incluir o `organization_id` na chave de cache de dados relacionados a empresas para evitar vazamento de informações entre organizações.
3. **NUNCA** armazenar objetos de conexão com o banco de dados ou instâncias de request no cache. Armazenar apenas tipos serializáveis em JSON ou dicionários puros.
