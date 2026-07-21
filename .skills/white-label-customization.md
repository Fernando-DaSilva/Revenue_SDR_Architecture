---
name: white-label-customization
description: |
  Instruções para implementação de internacionalização (i18n) customizável
  por usuário/tela e gerenciamento de presets de cores no Revenue SDR OS.
  Carregue esta skill quando for implementar ou modificar traduções e temas.
version: 1.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# White-Label Customization (Locales & Cores Presets)

Esta skill define os padrões e a arquitetura para suportar múltiplos idiomas dinâmicos com sobrescritas individuais por usuário e por tela, além de presets de cores para White Label.

---

## 1. Idiomas Suportados (Locales)

O sistema suporta cinco locales padrão inicialmente:
* `pt-BR`: Português (Brasil) — idioma padrão
* `es-ES`: Espanhol (Espanha)
* `en-GB`: Inglês (Reino Unido)
* `de-DE`: Alemão (Alemanha)
* `lt-LT`: Lituano (Lituânia)

Cada usuário possui um campo `preferred_locale: str` no model `User` para determinar seu idioma ativo.

---

## 2. Tradução por Tela e Usuário (Telas = Fabrics)

### Estrutura de Dicionários Padrão
As chaves de tradução padrão ficam localizadas em arquivos JSON no diretório de recursos da aplicação:
`app/web/locales/{locale}.json`.

Exemplo de estrutura do JSON (`pt-BR.json`):
```json
{
  "login": {
    "title": "Acessar Plataforma",
    "email_label": "E-mail comercial",
    "password_label": "Senha",
    "submit_button": "Entrar"
  },
  "dashboard": {
    "welcome": "Olá, bem-vindo de volta",
    "leads_count": "Total de Leads"
  }
}
```

### DDL / Model de Sobrescritas
Para permitir que o usuário customize rótulos por tela, usamos o model `UserTranslation` herdando de `TenantMixin` para isolamento:

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
    screen: str = Field(max_length=100, index=True)  # ex: "login", "dashboard"
    key: str = Field(max_length=100, index=True)     # ex: "submit_button"
    locale: str = Field(max_length=10, index=True)   # ex: "pt-BR"
    value: str = Field(max_length=1000, nullable=False)
```

### Lógica de Resolução e Cache
Para mitigar a latência de consultas ao banco de dados em cada requisição de página/fragmento:
1. As traduções padrão dos arquivos JSON são carregadas na memória durante a inicialização do app factory e guardadas em `app.state.base_translations`.
2. Um resolvedor de tradução busca na tabela `user_translations` as chaves customizadas para o usuário ativo e a tela em questão.
3. Usamos uma estratégia de cache em memória: `app.state.user_translation_cache: dict[str, dict]` onde a chave é `f"{user_id}:{screen}:{locale}"`.
4. O cache deve ser **invalidado** (removendo a chave do cache) sempre que houver inserção, atualização ou deleção na tabela `user_translations` para aquele usuário.

```python
# app/web/localization.py
import json
from pathlib import Path
from fastapi import Request
from sqlmodel import select
from app.models import UserTranslation

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
    
    # Carrega padrão
    base_dict = app.state.base_translations.get(locale, {}).get(screen, {}).copy()
    
    # Consulta banco para obter overrides
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
```

---

## 3. Presets de Cores do White Label

O banco de dados do tenant (tabela `organizations`) armazena os valores hexadecimais para as cores. Oferecemos 5 presets padrão integrados:

```python
THEME_PRESETS = {
    "sakura_bloom": {
        "theme_primary_color": "#EC4899",
        "theme_primary_hover_color": "#DB2777",
        "theme_secondary_color": "#F472B6",
        "theme_background_color": "#FDF2F8",
        "theme_surface_color": "#FFFFFF",
        "theme_text_color": "#111827"
    },
    "emerald_garden": {
        "theme_primary_color": "#10B981",
        "theme_primary_hover_color": "#059669",
        "theme_secondary_color": "#34D399",
        "theme_background_color": "#ECFDF5",
        "theme_surface_color": "#FFFFFF",
        "theme_text_color": "#111827"
    },
    "ocean_breeze": {
        "theme_primary_color": "#1E3A8A",
        "theme_primary_hover_color": "#1E40AF",
        "theme_secondary_color": "#3B82F6",
        "theme_background_color": "#F0F9FF",
        "theme_surface_color": "#FFFFFF",
        "theme_text_color": "#111827"
    },
    "obsidian_night": {
        "theme_primary_color": "#8B5CF6",
        "theme_primary_hover_color": "#7C3AED",
        "theme_secondary_color": "#06B6D4",
        "theme_background_color": "#0F172A",
        "theme_surface_color": "#1E293B",
        "theme_text_color": "#F9FAFB"
    },
    "amber_warmth": {
        "theme_primary_color": "#D97706",
        "theme_primary_hover_color": "#B45309",
        "theme_secondary_color": "#F59E0B",
        "theme_background_color": "#FEF3C7",
        "theme_surface_color": "#FFFFFF",
        "theme_text_color": "#111827"
    }
}
```

### Injeção de CSS em `base.html`
O arquivo `app/themes/resolver.py` gera as variáveis CSS a partir dos dados do tenant carregados em cache ou consultados no banco:

```python
def generate_theme_css(organization) -> str:
    return f""":root {{
  --color-primary: {organization.theme_primary_color};
  --color-primary-hover: {organization.theme_primary_hover_color};
  --color-secondary: {organization.theme_secondary_color};
  --color-background: {organization.theme_background_color};
  --color-surface: {organization.theme_surface_color};
  --color-text: {organization.theme_text_color};
  --color-border: #E5E7EB;
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-danger: #EF4444;
}}"""
```

---

## 4. Integração com Jinja2 / HTMX

No renderizador `app/web/templating.py`, injete as traduções resolvidas com base no usuário autenticado:

```python
from app.web.localization import get_translations_for_user

def render(request: Request, template_name: str, context: dict) -> HTMLResponse:
    user = request.state.user  # se autenticado
    screen = template_name.split("/")[0]  # infere tela a partir do caminho do template
    
    if user:
        locale = getattr(user, "preferred_locale", "pt-BR")
        translations = get_translations_for_user(request, user.id, locale, screen)
        context["_"] = lambda key: translations.get(key, key)
    else:
        # Fallback sem usuário
        context["_"] = lambda key: key
        
    # Render normal com Jinja...
```

No HTML, use a tag de tradução de forma declarativa:
```html
<h1 x-text="'{{ _("title") }}'">{{ _("title") }}</h1>
```
E use HTMX para submeter formulários de modificação de tradução diretamente a partir da UI de configurações de forma dinâmica.
