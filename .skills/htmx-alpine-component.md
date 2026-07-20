---
name: htmx-alpine-component
description: |
  Padroes de UI com HTMX + Alpine.js + CSS no Revenue SDR OS. Carregue esta
  skill sempre que for criar pagina, componente visual, ou interatividade.
version: 1.0.0
platforms: [claude-code, codex, opencode, hermes-agent, github-copilot]
---

# HTMX + Alpine.js + CSS — Padroes do Revenue SDR OS

## Principio basico

```
Frontend = HTMX (partial updates) + Alpine.js (microinteratividade) + CSS puro
NAO usar React, Vue, Next, etc.
Tenant theming via CSS variables injetadas por backend.
Componentes reusaveis em templates/partials/.
```

---

## Estrutura de templates (app/web/templates/)

```
app/web/templates/
+-- base.html                    # layout base com CSS variables
+-- auth/
|   +-- login.html
+-- errors/
|   +-- error.html
|   +-- tenant_not_found.html
+-- leads/
|   +-- index.html               # lista de leads
|   +-- detail.html              # detalhe + memories + timeline
|   +-- new.html                 # form de cadastro
+-- dashboard/
|   +-- index.html
+-- partials/                    # componentes reusaveis
    +-- lead_card.html
    +-- memory_chip.html
    +-- empty_state.html
```

Paginas (rotas HTML) ficam em `app/web/pages/<feature>.py`.
Assets estaticos em `app/web/static/` — HTMX/Alpine **vendored** em
`static/js/vendor/` (sem CDN: app precisa ser self-contained, ADR-011).

---

## Template base (app/web/templates/base.html)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {{ brand_meta | safe }}
    <link rel="stylesheet" href="/static/css/base.css">
    <link rel="stylesheet" href="/static/css/components.css">
    <style>{{ theme_css | safe }}</style>
    <script src="/static/js/vendor/htmx.min.js" defer></script>
    <script src="/static/js/vendor/alpine.min.js" defer></script>
</head>
<body>
    {% block content %}{% endblock %}
    <script src="/static/js/app.js" defer></script>
</body>
</html>
```

**Contexto injetado automaticamente** pelo `render()` de
`app/web/templating.py` (a rota NAO repete isso):
- `request`, `organization`
- `brand_meta` (title, favicon, theme-color)
- `theme_css` (`:root { --color-primary: ...; }`)
- `brand_name`, `logo_url`, `tenant_slug`

---

## Como renderizar template (Python)

```python
# app/web/pages/<feature>.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.web.templating import render

router = APIRouter(tags=["pages"])


@router.get("/leads", response_class=HTMLResponse)
async def list_leads_page(request: Request, ...):
    return render(
        request,
        "leads/index.html",
        {
            "user_name": current_user.name,
            "user_role": current_user.role,
            "leads": [...],  # lista de leads (ou pagina)
        },
    )
```

**REGRA**: passe apenas tipos simples/hashable (string, int, list, dict).
Evite passar o model SQLModel inteiro — extraia os campos que o template
precisa (ou passe um schema/namespace leve).

```python
# EVITE
return render(request, "leads/index.html", {"lead": lead})

# PREFIRA
return render(request, "leads/index.html", {
    "lead_id": lead.id,
    "lead_name": lead.name,
    "lead_phone": lead.phone,
})
```

---

## CSS variables (white-label)

### Injetadas por tenant (backend)

```python
# app/themes/service.py
def generate_theme_css(organization: Organization | None) -> str:
    primary = organization.theme_primary_color if organization else DEFAULT_PRIMARY
    primary_hover = darken(primary, 10)
    return f""":root {{
  --color-primary: {primary};
  --color-primary-hover: {primary_hover};
  --color-secondary: {organization.theme_secondary_color};
  --color-background: #F9FAFB;
  --color-surface: #FFFFFF;
  --color-text: #111827;
  --color-text-muted: #6B7280;
  --color-border: #E5E7EB;
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-danger: #EF4444;
}}"""
```

### Usadas no CSS (frontend)

```css
/* static/css/base.css */
body {
    background: var(--color-background);
    color: var(--color-text);
}

.btn-primary {
    background: var(--color-primary);
    color: white;
}

.btn-primary:hover {
    background: var(--color-primary-hover);
}
```

**NUNCA hardcode cor no CSS**:
```css
/* ERRADO */
.btn-primary { background: #3B82F6; }

/* CERTO */
.btn-primary { background: var(--color-primary); }
```

---

## CSS components (static/css/components.css)

```css
/* Botoes */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.625rem 1.25rem;
    border: 1px solid transparent;
    border-radius: var(--radius);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
}

.btn-primary {
    background: var(--color-primary);
    color: white;
}

.btn-primary:hover {
    background: var(--color-primary-hover);
}

.btn-ghost {
    background: transparent;
    color: var(--color-text);
    border-color: var(--color-border);
}

/* Forms */
.form-group { margin-bottom: 1rem; }

.form-input {
    display: block;
    width: 100%;
    padding: 0.625rem 0.75rem;
    font-size: 0.875rem;
    color: var(--color-text);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    transition: border-color 0.15s, box-shadow 0.15s;
}

.form-input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Cards */
.card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
}

/* Tags */
.tag {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    border-radius: var(--radius);
    background: var(--color-surface-hover);
    color: var(--color-text-muted);
    margin-right: 0.25rem;
}
```

---

## HTMX patterns

### 1. Partial updates (recarrega so uma parte da pagina)

```html
<!-- lista de leads -->
<div id="leads-list"
     hx-get="/api/v1/leads"
     hx-trigger="load"
     hx-swap="innerHTML">
    Carregando leads...
</div>

<!-- Pode recarregar com HTMX -->
<button hx-get="/api/v1/leads"
        hx-target="#leads-list"
        hx-swap="innerHTML">
    Atualizar
</button>
```

### 2. Form submission (POST e re-render parcial)

```html
<form hx-post="/api/v1/leads"
      hx-target="#leads-list"
      hx-swap="innerHTML"
      hx-on::after-request="if(event.detail.successful) this.reset()">
    <input name="name" required>
    <input name="phone">
    <select name="source">
        <option value="whatsapp">WhatsApp</option>
        <option value="site">Site</option>
    </select>
    <button type="submit">Criar lead</button>
</form>
```

### 3. Delete com confirmacao

```html
<button hx-delete="/api/v1/leads/{{ lead_id }}"
        hx-confirm="Tem certeza que deseja deletar?"
        hx-target="#leads-list"
        hx-swap="innerHTML">
    Deletar
</button>
```

### 4. Infinite scroll

```html
<div id="leads-list"
     hx-get="/api/v1/leads?skip=0&limit=20"
     hx-trigger="revealed"
     hx-swap="afterend">
    <!-- initial content -->
</div>
```

### 5. Polling (atualizar periodicamente)

```html
<div id="notifications"
     hx-get="/api/v1/notifications"
     hx-trigger="every 5s"
     hx-swap="innerHTML">
</div>
```

**IMPORTANTE**: para real-time, use SSE (Sprint 6+) ao inves de polling.

---

## Alpine.js patterns (microinteratividade)

### 1. Toggle de visibilidade

```html
<div x-data="{ open: false }">
    <button @click="open = !open">
        Toggle detalhes
    </button>
    <div x-show="open" x-transition>
        Conteudo que aparece/desaparece
    </div>
</div>
```

### 2. Modal

```html
<div x-data="{ showModal: false }">
    <button @click="showModal = true">Abrir modal</button>

    <div x-show="showModal"
         x-transition.opacity
         @keydown.escape.window="showModal = false"
         class="modal-overlay"
         @click.self="showModal = false">
        <div class="modal-content" @click.stop>
            <h2>Titulo</h2>
            <p>Conteudo</p>
            <button @click="showModal = false">Fechar</button>
        </div>
    </div>
</div>
```

### 3. Form state (loading, disabled)

```html
<form x-data="{ submitting: false }"
      @submit="submitting = true">
    <button type="submit"
            :disabled="submitting"
            x-text="submitting ? 'Salvando...' : 'Salvar'">
    </button>
</form>
```

### 4. Confirmacao inline

```html
<div x-data="{ confirm: false }">
    <button x-show="!confirm" @click="confirm = true">Deletar</button>
    <span x-show="confirm">
        Tem certeza?
        <button @click="$dispatch('delete-lead')">Sim</button>
        <button @click="confirm = false">Nao</button>
    </span>
</div>
```

### 5. Live search (debounced)

```html
<input type="search"
       x-data="{ query: '' }"
       x-model="query"
       @input.debounce.300ms="
           $dispatch('search', { q: query })
       ">

<div x-data="{ results: [] }"
     @search.window="
       fetch(`/api/v1/leads?search=${$event.detail.q}`)
         .then(r => r.json())
         .then(data => results = data)
     ">
    <template x-for="lead in results" :key="lead.id">
        <div x-text="lead.name"></div>
    </template>
</div>
```

---

## Componentes reusaveis (partials)

### Lead card (app/web/templates/partials/lead_card.html)

```html
{# Componente: card de lead #}
<div class="lead-card card">
    <div class="lead-card-header">
        <h3>{{ lead_name }}</h3>
        <span class="tag" :class="'status-' + status">{{ status }}</span>
    </div>
    <div class="lead-card-body">
        <p><strong>Telefone:</strong> {{ lead_phone or "—" }}</p>
        <p><strong>Email:</strong> {{ lead_email or "—" }}</p>
        <p><strong>Fonte:</strong> {{ lead_source }}</p>
        {% if lead_tags %}
        <div class="tags">
            {% for tag in lead_tags %}
            <span class="tag">{{ tag }}</span>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    <div class="lead-card-footer">
        <a href="/leads/{{ lead_id }}" class="btn btn-ghost btn-sm">Ver detalhes</a>
    </div>
</div>
```

Uso:
```html
<!-- Em leads/index.html -->
<div class="leads-grid">
    {% for lead in leads %}
        {% include "partials/lead_card.html" with {
            "lead_id": lead.id,
            "lead_name": lead.name,
            "lead_phone": lead.phone,
            "lead_email": lead.email,
            "lead_source": lead.source,
            "lead_tags": lead.tags,
            "status": lead.status
        } %}
    {% endfor %}
</div>
```

---

## Live updates com SSE (Sprint 6+)

```html
<div sse-swap="lead_updated"
     hx-swap="outerHTML">
    <!-- Conteudo sera atualizado quando SSE event chegar -->
</div>

<script>
    const evtSource = new EventSource("/sse/conversations/123");
    evtSource.addEventListener("lead_updated", (e) => {
        // Atualizar UI
        document.getElementById("lead-card-123").outerHTML = e.data;
    });
</script>
```

---

## Anti-patterns (NUNCA faca)

```html
<!-- ERRADO: hardcode cor -->
<button style="background: #3B82F6;">Click</button>

<!-- CERTO: usa CSS variable -->
<button class="btn btn-primary">Click</button>


<!-- ERRADO: form action tradicional sem HTMX -->
<form action="/leads" method="POST">
    <!-- Page reload, sem HTMX -->
</form>

<!-- CERTO: HTMX para partial update -->
<form hx-post="/api/v1/leads" hx-target="#leads-list">
    ...
</form>


<!-- ERRADO: JavaScript pesado pra UI -->
<button onclick="fetch('/api/...').then(...)">Carregar</button>

<!-- CERTO: HTMX declarative -->
<button hx-get="/api/v1/leads" hx-target="#list">Carregar</button>


<!-- ERRADO: passar objeto SQLModel pro template -->
context = {"lead": lead}  # causa erro de hash

<!-- CERTO: extrair campos -->
context = {"lead_name": lead.name, "lead_phone": lead.phone}


<!-- ERRADO: criar CSS file nova pra cada componente -->
<!-- file: leads.css, dashboard.css, memory.css, ... -->

<!-- CERTO: CSS variables + components.css compartilhado -->
<!-- file: components.css com classes reutilizaveis -->
```

---

## Checklist de review de UI

```
[ ] Template herda de base.html
[ ] Tema injetado via theme_css (CSS variables)
[ ] Brand metadata injetada via brand_meta
[ ] Nenhuma cor hardcoded (usa CSS variables)
[ ] HTMX usado para partial updates (sem page reload)
[ ] Alpine.js usado para microinteratividade (NAO para tudo)
[ ] Formularios usam hx-post + hx-target
[ ] Botoes de acao usam hx-delete/hx-get com confirm
[ ] Context passa apenas tipos hashable (NAO SQLModel objects)
[ ] Componentes reusaveis em partials/
[ ] Empty state quando nao ha dados
[ ] Loading state durante requests
[ ] Error handling (htmx:response-error)
[ ] Acessibilidade basica (labels, aria-*, keyboard nav)
```

---

*"HTMX e' o 90% do que voce precisa. Alpine.js e' os outros 9%. React seria overkill."*