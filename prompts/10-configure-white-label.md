# Prompt — Configurar White-Label (Idiomas Customizados & Presets de Cores)

> Spec reutilizável para implementar o sistema avançado de White Label (traduções por tela/usuário e presets de cores) no Revenue SDR OS.
> Padrões completos: `.skills/white-label-customization.md` (v1.0.0).

---

## Contexto

Precisamos implementar suporte a customização de idiomas de forma granular (por usuário e por tela) e presets de cores para o White-Label.

Locales iniciais suportados:
* `pt-BR` (Português do Brasil)
* `es-ES` (Espanhol da Espanha)
* `en-GB` (Inglês do Reino Unido)
* `de-DE` (Alemão da Alemanha)
* `lt-LT` (Lituano da Lituânia)

Além disso, precisamos disponibilizar 5 presets de cores iniciais (Sakura Bloom, Emerald Garden, Ocean Breeze, Obsidian Night e Amber Warmth) no banco de dados e dar a capacidade de selecionar ou customizar individualmente na tela de configurações.

---

## Passo a Passo

### 1. Criar os Arquivos de Tradução Padrão (Locales)
Crie o diretório `app/web/locales/` e salve os seguintes arquivos JSON com as chaves padrão:
- `pt-BR.json`
- `es-ES.json`
- `en-GB.json`
- `de-DE.json`
- `lt-LT.json`

Exemplo de chaves a incluir nos JSONs para as telas `login`, `dashboard` e `settings`:
* `title` (Título da tela)
* `welcome` (Mensagem de boas-vindas)
* `save_button` (Rótulo do botão salvar)
* `select_language` (Rótulo de seleção de idioma)
* `select_theme` (Rótulo de seleção de tema)

### 2. Criar o Model de Tradução no Banco
Adicione o model `UserTranslation` em `app/themes/models.py` (ou em pacote equivalente):

```python
from sqlmodel import Field
from app.db.base import TenantMixin, prefixed_id

class UserTranslation(TenantMixin, table=True):
    __tablename__ = "user_translations"

    id: str = Field(
        default_factory=lambda: prefixed_id("utr"),
        primary_key=True,
    )
    user_id: str = Field(foreign_key="users.id", index=True, nullable=False)
    screen: str = Field(max_length=100, index=True)
    key: str = Field(max_length=100, index=True)
    locale: str = Field(max_length=10, index=True)
    value: str = Field(max_length=1000, nullable=False)
```

Adicione também o campo `preferred_locale: str` no model `User` (default: `"pt-BR"`) via migração Alembic.

### 3. Implementar o Serviço de Resolução de Tradução
Crie `app/web/localization.py` com suporte a cache em memória e invalidação (limpar o cache do usuário quando as chaves forem salvas).

```python
# app/web/localization.py
import json
from pathlib import Path
from fastapi import Request
from sqlmodel import select
from app.themes.models import UserTranslation

def load_base_translations(app):
    locales_dir = Path("app/web/locales")
    base_trans = {}
    for path in locales_dir.glob("*.json"):
        locale = path.stem
        with open(path, "r", encoding="utf-8") as f:
            base_trans[locale] = json.load(f)
    app.state.base_translations = base_trans
    app.state.user_translation_cache = {}

def get_translations_for_user(request: Request, user_id: str, locale: str, screen: str) -> dict:
    app = request.app
    cache_key = f"{user_id}:{screen}:{locale}"
    
    if cache_key in app.state.user_translation_cache:
        return app.state.user_translation_cache[cache_key]
        
    base_dict = app.state.base_translations.get(locale, {}).get(screen, {}).copy()
    
    db = request.state.db
    statement = select(UserTranslation).where(
        UserTranslation.user_id == user_id,
        UserTranslation.screen == screen,
        UserTranslation.locale == locale
    )
    overrides = db.exec(statement).all()
    for o in overrides:
        base_dict[o.key] = o.value
        
    app.state.user_translation_cache[cache_key] = base_dict
    return base_dict

def invalidate_user_cache(app, user_id: str):
    # Remove as chaves de cache correspondentes ao usuário
    keys_to_remove = [k for k in app.state.user_translation_cache.keys() if k.startswith(f"{user_id}:")]
    for k in keys_to_remove:
        app.state.user_translation_cache.pop(k, None)
```

### 4. Implementar Presets de Cores no `Organization`
Certifique-se de que a tabela `organizations` suporta as seguintes colunas de cores (via Alembic):
* `theme_primary_color: str`
* `theme_primary_hover_color: str`
* `theme_secondary_color: str`
* `theme_background_color: str`
* `theme_surface_color: str`
* `theme_text_color: str`

E crie uma rota na API (`/api/v1/theme/preset`) para aplicar um dos 5 presets iniciais:
* `sakura_bloom` (Pink)
* `emerald_garden` (Green)
* `ocean_breeze` (Navy Blue)
* `obsidian_night` (Dark Slate/Purple)
* `amber_warmth` (Amber Gold)

### 5. Integrar na Tela de Configurações (`settings.html`)
Desenvolva a UI usando HTMX + Alpine.js que permite:
* Escolher o idioma padrão do usuário (`preferred_locale`).
* Ver uma lista de chaves de tradução por tela/fabric, permitindo edição inline com salvamento via `hx-post` (que invalida o cache do backend).
* Escolher um preset de cor e aplicar instantaneamente sem recarregar a página (atualizando as variáveis CSS do `:root`).

---

## Validação

1. **Testes Unitários**:
   * Crie `tests/test_localization.py` para validar o carregamento dos JSONs, a resolução de strings e a invalidação do cache ao atualizar uma tradução de usuário.
   * Crie `tests/test_theme_presets.py` para validar a aplicação de presets e integridade de isolamento.
2. **Lint & Formatação**:
   ```bash
   ruff check app/
   ruff format --check app/
   ```

---

## Checklist

```
[ ] Arquivos JSON padrão em app/web/locales/
[ ]preferred_locale adicionado ao model User
[ ] Tabela user_translations criada com TenantMixin e Alembic migration
[ ] Localization helper integrado no render_template do Jinja2
[ ] Cache em memória implementado e invalidado corretamente
[ ] Presets de cores definidos no dicionário THEME_PRESETS
[ ] Endpoint de configuração de tradução e tema funcional (API e UI)
[ ] Testes cobrindo isolamento de tradução por usuário e preset de cores por tenant
```
