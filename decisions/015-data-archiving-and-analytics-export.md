# ADR-015 — Arquivamento de Dados, Tiering de Histórico e Exportação Analítica (PostgreSQL / Supabase)

- **Status:** Aceito (Sprint 00 / Atualizado para v2.2 na Sprint 07)
- **Data:** 2026-07-21 (Atualizado: 2026-07-27)

## Contexto e Problema

O **Revenue SDR OS** foi estruturado com base em uma arquitetura de banco de dados *offline-first* utilizando Turso/libSQL local (ADR-002 e ADR-016). Isso garante isolamento estrito, performance altíssima para as APIs transacionais e facilidade extrema de deploy.

Porém, conforme a operação de SDR (humana e por agentes de IA) escala, o volume de mensagens de conversa, transcrições e eventos append-only cresce significativamente. Manter todo o histórico de conversas passadas no banco operacional local (Turso) causa inchaço de disco I/O e degradação de performance nas rotas de webhook em tempo real. Além disso, análises analíticas (Dashboards da Sprint 07), **Busca Textual Avançada (Full-Text Search)** e **Busca Semântica/RAG** exigem capacidades que o SQLite/libSQL local não provê nativamente de forma escalável.

## Decisão

Instituir uma arquitetura de **Tiering de Dados (Hot Storage vs. Cold Storage)** com exportação assíncrona ETL e purga programada, adotando **PostgreSQL / Supabase (com `pgvector` e Full-Text Search)** como a **Opção B Homologada e Recomendada** para o banco de histórico e analítico.

### 1. Modelo de Armazenamento em Camadas (Storage Tiering)

* **Hot Storage (Turso / libSQL Local Operacional):**
  * Armazena leads ativos (em atendimento/prospecção) e a janela recente de conversas (mensagens do dia atual + retenção ativa de 30 dias).
  * Foco em baixíssima latência (< 10ms) para gravação de webhooks de mensagens do WhatsApp/Canais e montagem rápida de contextos para prompts da IA SDR.
* **Cold Storage / Data Warehouse (PostgreSQL / Supabase Gerenciado):**
  * Destino padrão para todo o histórico D-1 consolidado e mensagens de leads finalizados (Ganhos/Perdidos/Arquivados).
  * Equipado com a extensão **`pgvector`** para RAG / embeddings de histórico de conversas e suporte a **Full-Text Search (`tsvector`)** para buscas textuais avançadas.

### 2. Exportação Assíncrona (Replicação ETL D-1)

- Através da Fila Leve de Jobs (ARQ/APScheduler — Sprint 03), processos periódicos executados na madrugada (ex: 02:00 AM) despacharão blocos de `events` imutáveis, `conversations` e `messages` consolidadas (Append-Only/Upsert) para o Supabase / PostgreSQL.
- Estruturação em schemas otimizados (*Star Schema* / *Wide Tables*) para consumo direto pelo *Revenue Brain* (Sprint 07), BI e motores de busca semântica.

### 3. Arquivamento Seguro e Purga (Archiving & Purge)

- **Time-to-Live (TTL):** Janela de retenção configurável para o Turso local (padrão: 30 a 90 dias ou apenas leads com status ativo).
- **Validação de Sincronia:** Uma vez que os dados ultrapassaram a janela e **a sincronia com o PostgreSQL/Supabase foi confirmada**, o job de *Archiving* executa a remoção física (`DELETE` + `VACUUM` otimizado) do banco Turso local.
- Garante que o arquivo `.db` local se mantenha sempre enxuto (poucas centenas de MBs), veloz e responsivo.

### 4. Acesso Transparente na UI (Unified Service Layer + HTMX Lazy Load)

- **Backend (Service Layer):** O serviço `MessageService` abstrai o acesso às mensagens. As primeiras mensagens (recentes) são consultadas no Turso Hot DB. Se o usuário solicitar histórico mais antigo, o serviço consulta o PostgreSQL/Supabase e une os resultados de forma transparente.
- **Frontend (HTMX):** A interface renderiza o chat inicial rapidamente e utiliza um trigger HTMX (`hx-trigger="intersect once"`) no topo do container de mensagens para carregar partes mais antigas do histórico via *lazy loading* sob demanda.

### 5. Processo de Restauração (Restore & Replay)

- Em caso de falha de hardware ou reinicialização de ambiente, scripts de *Restore* repuxam dados consolidados do Supabase/PostgreSQL para reconstruir a base local Turso de um tenant respeitando a estrutura do domínio.

## Consequências

- **Positivas:**
  - Desacoplamento total entre operações em tempo real (OLTP no Turso/libSQL) e buscas complexas / analíticas (OLAP no PostgreSQL/Supabase).
  - Habilita busca semântica (RAG via `pgvector`) no histórico de conversas passadas para retroalimentar a IA SDR sem impactar o banco principal.
  - Performance constante nas APIs e webhooks, independente de o sistema possuir meses ou anos de dados acumulados.
  - Capacidades completas de Business Intelligence e estatísticas agregadas cross-tenant.
- **Negativas:**
  - Requer a manutenção de uma conexão externa com PostgreSQL/Supabase para funcionalidades de histórico longo e analytics.
  - Eventual consistência (latência do job de ETL) entre ações do dia e os relatórios analíticos consolidados no DW.

## Implementação

Modelos analíticos, schemas PostgreSQL/Supabase (com `pgvector`), jobs de ETL D-1 e abstrações do `MessageService` serão finalizados na **Sprint 07** com a entrega do *Revenue Brain*.
