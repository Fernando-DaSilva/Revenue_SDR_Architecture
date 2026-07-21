# ADR-015 — Arquivamento de Dados e Exportação Analítica (ETL / DW)

- **Status:** Aceito (Sprint 00 / Implementação na Sprint 07)
- **Data:** 2026-07-21

## Contexto e Problema

O **Revenue SDR OS** foi estruturado com base em uma arquitetura de banco de dados *offline-first* utilizando SQLite WAL individual por tenant (ADR-002 e ADR-004). Isso garante isolamento estrito, performance altíssima para as APIs transacionais e facilidade extrema de deploy.

Porém, conforme os clientes escalam suas operações de SDR e de inteligência artificial, o volume de `events`, histórico de `conversations` e transcrições começará a sobrecarregar o SQLite. Além disso, a **Sprint 07** introduzirá o *Manager/Revenue Brain* — funcionalidades com Dashboards agregados (Funil, CAC, ROI, Canal Vencedor) que necessitam de consultas e junções complexas (Analytics). Realizar essas análises pesadas diretamente no SQLite transacional local poderia causar *locks* e degradação da experiência de uso real-time da operação de vendas.

## Decisão

Projetar uma esteira assíncrona de **Exportação Analítica (ETL/CDC)** acoplada a um processo de **Arquivamento Seguro (Cold Storage)**, baseando-se nestas diretrizes operacionais para a Sprint 07:

### 1. Suporte a Múltiplos Data Warehouses (DW)
O sistema deve ser agnóstico quanto ao banco analítico de destino. Haverá uma camada de configuração via "MyraOS" (Platform Console) ou interface do Tenant Admin para cadastrar drivers externos.
- **Bancos Homologados de Destino:**
  - Supabase (PostgreSQL em Cloud).
  - PostgreSQL On-Premise/Gerenciado.
  - Microsoft SQL Server (MS-SQL).
  - Outros compatíveis via SQLAlchemy.

### 2. Exportação Assíncrona (Replicação ETL)
- Através da Fila Leve de Jobs (ARQ/APScheduler — Sprint 03), processos periódicos despacharão blocos de `events` imutáveis e `leads` atualizados (Append-Only/Upsert) para o DW configurado.
- Os modelos SQL exportados focarão em *Star Schema* ou *Wide Tables* para que dashboards (Grafana, PowerBI, ou os Dashboards internos do Sprint 07) sejam imediatos e velozes.

### 3. Arquivamento (Archiving)
- **Time-to-Live (TTL):** Definir janelas de retenção configuráveis para o SQLite (exemplo: manter apenas conversas e eventos dos últimos 6 ou 12 meses).
- Uma vez que os dados tenham ultrapassado a janela e **a sincronia de ETL com o DW tenha sido confirmada**, um job de *Archiving* expurgará de forma física (DELETE e subsequente VACUUM otimizado) esses registros do banco SQLite local.
- Isso mantém o `.db` local sempre com no máximo algumas centenas de MBs, super responsivo e leve.

### 4. Processo de Restauração (Desastre/Restore)
- Se um tenant corromper sua instância local ou houver a necessidade de analisar retroativamente um lead antigo, um script/endpoint de *Restore* poderá repuxar transações consolidadas do DW ou Supabase e repopular o SQLite parcial ou integralmente, respeitando a estrutura do domínio.

## Consequências

- **Positivas:**
  - Desacoplamento perfeito entre Operacional (Transacional/OLTP no SQLite) e Inteligência (Analítico/OLAP no Supabase/MS-SQL).
  - Garantia de que a base local nunca inchará até o limite de degradação I/O do SQLite.
  - Habilita capacidades reais de Business Intelligence e Treinamentos de Machine Learning sem tocar na produção.
  - Cumprimento de leis de retenção de dados a longo prazo.
- **Negativas:**
  - Introduz latência (Eventual Consistency) nos Dashboards da Sprint 07: os relatórios não refletirão ações feitas no exato milissegundo, mas sim com o atraso do cron job do ETL (ex: a cada 1 hora).
  - O pipeline de deploy ganha leve complexidade por precisar lidar com schemas em dois bancos distintos (o transacional SQLite e o schema analítico no destino).

## Implementação
Criar os modelos do esquema Analítico, os Jobs de ETL baseados em Cron, a API de configuração de Destino (Driver SQL) e o sistema de Archiving puramente na **Sprint 07**, onde essas bases já serão imediatamente consumidas pelo Revenue Brain.
