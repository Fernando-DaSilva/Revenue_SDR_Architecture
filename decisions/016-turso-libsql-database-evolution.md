# ADR-016 — Adoção do Turso (libSQL) com Suporte a Embedded Replicas e Fallback Local

- **Status:** Aceito
- **Data:** 2026-07-27

## Contexto e Problema

O **Revenue SDR OS** foi estruturado segundo um modelo *self-contained* rodando em VPS dedicada por cliente (ADR-004). Na v0.2.0, o banco de dados soberano foi definido como SQLite WAL local (ADR-002), garantindo zero fricção de infraestrutura e performance transacional de microssegundos.

No entanto, conforme a plataforma evolui para gerenciar centenas de nós de clientes (VPSs), o SQLite puro apresenta desafios operacionais:
1. **Backup e Disaster Recovery:** Fazer backups de arquivos `.db` em execução sem bloquear escritas ou corromper páginas exige rotinas de cópia complexas (*online backup API*).
2. **Observabilidade e Gestão de Schema:** Testar alterações de schema em CI/CD exige instâncias limpas, e o gerenciamento centralizado de réplicas via Platform Console (MyraOS) exige um protocolo de sincronia.
3. **Escalabilidade de Leitura:** Operações de leitura pesadas no arquivo local podem disputar I/O com a escrita do motor de IA durante picos de conversas.

## Decisão

Adotar o **Turso** (baseado no motor open-source **libSQL**) como o motor de banco de dados do Revenue SDR OS, utilizando o dialect `sqlite+libsql://` (via `sqlalchemy-libsql`).

### Diretrizes de Arquitetura:

1. **Funcionamento Standalone Local (Custo ZERO, Sem Nuvem Obrigatória)**
   - O libSQL é um fork 100% compatível com o SQLite.
   - Em sua configuração padrão (sem variáveis de sincronia na nuvem), o sistema grava e lê diretamente no arquivo `.db` local da VPS (`sqlite+libsql:///revenue_sdr_os.db` ou `sqlite:///...`).
   - Não há dependência de serviços externos, não há obrigatoriedade de cadastro em nuvem e **o custo permanece R$ 0,00**.

2. **Embedded Replicas (Sincronização e Backup Automatizado Opcional)**
   - Quando configuradas as variáveis de ambiente `TURSO_DATABASE_URL` e `TURSO_AUTH_TOKEN`, o driver utiliza a funcionalidade de *Embedded Replica*.
   - A aplicação continua lendo e gravando no arquivo `.db` local da VPS com altíssima velocidade (latência de microssegundos).
   - O motor sincroniza de forma assíncrona as transações com a nuvem do Turso (*Primary Cloud Cluster*), fornecendo backup contínuo, Point-in-Time Recovery e alta disponibilidade sem travar a thread da aplicação.

3. **Compatibilidade Transparente com a Stack Existente**
   - **ORM:** SQLModel e SQLAlchemy conectam nativamente utilizando o dialect `sqlite+libsql://`.
   - **Migrations:** O Alembic continua executando comandos `upgrade head` e `downgrade` normalmente, pois o libSQL utiliza o dialecto SQL exato do SQLite.
   - **Testes Automáticos:** A suíte de testes (`pytest`) continua utilizando SQLite em memória (`sqlite://` com `StaticPool`), garantindo execuções isoladas e ultrarrápidas sem tocar em recursos externos.

4. **Database Branching em CI/CD**
   - Adoção do fluxo de *branching* do Turso (`turso db branch`) para criar réplicas temporárias de banco de dados durante testes de integração de migrations do Alembic no GitHub Actions/CI, evitando testes destrutivos no banco de produção.

## Consequências

- **Positivas:**
  - **Zero Breaking Changes:** Nenhuma query ou modelo SQLModel precisa ser alterado.
  - **Resiliência e Backup:** Soluciona nativamente o backup das VPSs sem bloquear o arquivo local.
  - **Flexibilidade Total:** Permite operar 100% offline (arquivo local `.db`) ou híbrido (Embedded Replica com backup em nuvem).
  - **Plano Gratuito Amplo:** O plano *Hobby* do Turso (9 GB, 500 bancos, 1B leituras/mês) cobre com sobra múltiplos nós de staging e produção com custo zero.
- **Negativas:**
  - Inclusão do pacote `sqlalchemy-libsql` no gerenciamento de dependências (`pyproject.toml`).
  - Necessidade de documentar as chaves de configuração `TURSO_DATABASE_URL` e `TURSO_AUTH_TOKEN` no `.env.example`.

## Implementação

1. Adicionar `sqlalchemy-libsql` nas dependências do projeto.
2. Atualizar a fábrica de engines (`app/db/engine.py`) para tratar URLs `sqlite+libsql://` e configurar `connect_args` quando as variáveis do Turso estiverem presentes no ambiente.
3. Atualizar a documentação do projeto (`ARCHITECTURE.md`, `FOUNDATION.md`, `AGENTS.md` e skills).
