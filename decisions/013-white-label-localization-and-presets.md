# ADR-013 — Customização de Idiomas por Tela/Usuário e Presets de Cores no White-Label

* **Status**: Aprovado
* **Data**: 2026-07-21
* **Autor**: Hermes (Arquiteto)

---

## Contexto

O Revenue SDR OS v0.2.0 introduziu temas de cores básicos por tenant baseados em variáveis CSS carregadas do banco de dados. No entanto, para suportar parceiros de White Label que exigem flexibilidade internacional e customização profunda, precisamos de:
1. **Multi-idiomas dinâmico**: Suporte inicial para Português Brasileiro (`pt-BR`), Espanhol da Espanha (`es-ES`), Inglês Britânico (`en-GB`), Alemão da Alemanha (`de-DE`) e Lituano da Lituânia (`lt-LT`).
2. **Customização granular (por tela e usuário)**: Os usuários de um tenant devem ser capazes de alterar a tradução de rótulos específicos em telas individuais ("telas" ou "fabrics"), mantendo listas individuais por usuário para cada tela.
3. **Temas Estéticos Pré-configurados**: Pelo menos 5 paletas de cores prontas e curadas (presets) contendo no mínimo 5 variáveis de cores essenciais em cada uma.

---

## Decisão

### 1. Modelo de Tradução Dinâmica

Usaremos uma abordagem híbrida de **arquivos estáticos + banco de dados**:
* **Arquivos de Tradução Base**: Arquivos JSON locais (ex: `app/web/locales/{locale}.json`) contêm as chaves e valores padrão para cada idioma. Isso garante que a inicialização do app seja autossuficiente e rápida.
* **Tabela de Sobrescrita (`user_translations`)**: Uma tabela SQLModel que armazena as chaves customizadas de cada usuário para cada tela.

#### DDL / Schema do Model `UserTranslation`

```python
class UserTranslation(TenantMixin, table=True):
    __tablename__ = "user_translations"

    id: str = Field(
        default_factory=lambda: prefixed_id("utr"),
        primary_key=True,
    )
    user_id: str = Field(foreign_key="users.id", index=True, nullable=False)
    screen: str = Field(max_length=100, index=True)  # ex: "dashboard", "leads"
    key: str = Field(max_length=100, index=True)     # ex: "welcome_message"
    locale: str = Field(max_length=10, index=True)   # ex: "pt-BR", "lt-LT"
    value: str = Field(max_length=1000)              # Tradução customizada pelo usuário
```

### 2. Fluxo de Resolução de Idioma e Cache

1. O middleware de autenticação identifica o `User` atual, que possui a coluna `preferred_locale: str` (default: `pt-BR`).
2. Uma função auxiliar `get_translations(user: User, screen: str) -> dict` é invocada no renderizador de templates.
3. O sistema carrega o dicionário padrão para o `preferred_locale`.
4. Ele aplica as sobrescritas da tabela `user_translations` para aquele `user_id` e `screen`.
5. **Estratégia de Cache**: Para evitar queries de banco em cada render, os dicionários fundidos de traduções por usuário e tela são armazenados em cache em memória (`app.state.translation_cache`), invalidado sempre que o usuário salvar uma nova tradução.

### 3. Presets de Cores (Cores & Variantes)

Definiremos 5 presets iniciais ricos no banco de dados. Cada preset define valores específicos para as seguintes 5 variáveis CSS inegociáveis:
* `--color-primary`
* `--color-primary-hover`
* `--color-secondary`
* `--color-background`
* `--color-surface`

#### Os 5 Presets Iniciais:

| Preset Name | `--color-primary` | `--color-primary-hover` | `--color-secondary` | `--color-background` | `--color-surface` |
|---|---|---|---|---|---|
| **Sakura Bloom** | `#EC4899` (Rosa) | `#DB2777` | `#F472B6` | `#FDF2F8` | `#FFFFFF` |
| **Emerald Garden** | `#10B981` (Verde) | `#059669` | `#34D399` | `#ECFDF5` | `#FFFFFF` |
| **Ocean Breeze** | `#1E3A8A` (Navy) | `#1E40AF` | `#3B82F6` | `#F0F9FF` | `#FFFFFF` |
| **Obsidian Night** | `#8B5CF6` (Roxo) | `#7C3AED` | `#06B6D4` | `#0F172A` | `#1E293B` |
| **Amber Warmth** | `#D97706` (Amber) | `#B45309` | `#F59E0B` | `#FEF3C7` | `#FFFFFF` |

O tenant admin pode selecionar um desses presets na UI ou personalizar as cores manualmente.

---

## Consequências

* **Positivas**:
  * Flexibilidade total de White Label: os clientes podem adaptar a plataforma para sua nomenclatura corporativa.
  * Baixíssima latência via cache em memória das traduções ativas.
  * UI de alta fidelidade visual com presets testados e modernos.
* **Negativas**:
  * Aumento da complexidade na camada de renderização dos templates, que agora precisa injetar dicionários de tradução dinâmicos baseados no usuário e na tela.
