# Prompt — Gerenciador de Temas White-Label & Customização Total de Variáveis CSS (v2.0)

> **Instrução:** Copie o prompt abaixo e envie para o seu agente de codificação nos repositórios `~/AGENCIA/SDR` (Backend/Full-stack) ou `01_SDR_Prototype` (Protótipo Frontend).

---

**INÍCIO DO PROMPT:**

Você é um Engenheiro de Software Principal e Designer de Sistemas especialista em **White-Labeling, Design Tokens e CSS Architecture**. Sua missão é projetar e implementar a nova tela dedicada de **"Gerenciador de Temas White-Label"** no **Revenue SDR OS**.

---

### Contexto & Requisitos de Demonstração
1. **Tema Padrão da Demonstração (Default)**: Nesta versão de demonstração, o tema ativo padrão por default do sistema será o **"Obsidian Night"** (Dark Mode puro com acentos de alto contraste), substituindo o antigo tema "Sakura Bloom".
2. **Sub-tela de Preview Interactive & Fluxo de Aprovação**: A tela de gerenciamento de temas deve contar com uma **sub-tela/modal de "Preview Interativo Completo"**. O usuário pode editar as variáveis em modo Rascunho/Sandbox, abrir a sub-tela de Preview para observar a aplicação inteira com o novo visual, e optar por **Aprovar** ou **Rejeitar** as mudanças:
   - **Ao Aprovar**: Abre-se um modal para definir o **Nome do Novo Tema** (ex: *"Clínica Luxury Dark"*). Ao confirmar, o novo tema é criado, persistido e automaticamente adicionado ao **Perfil de Escolhas/Presets do Tenant**.
   - **Ao Rejeitar**: Todas as edições não salvas do rascunho são descartadas e o app retorna ao tema ativo anterior.

---

### 1. ARQUITETURA DE DESIGN TOKENS E VARIÁVEIS CSS COMPLETA

O sistema de temas deve expor e controlar os seguintes tokens no CSS `:root`:

#### A. Cores da Marca & Interação
* `--color-primary`: Cor primária principal (botões principais, destaques ativos).
* `--color-primary-hover`: Estado de hover do elemento primário.
* `--color-primary-light`: Fundo sutil / tint de elementos primários (badges, seleções).
* `--color-secondary`: Cor secundária da marca (ações secundárias, acentos).
* `--color-secondary-hover`: Hover da cor secundária.
* `--color-accent`: Cor de destaque para elementos de atenção/conversão.
* `--color-ring-focus`: Cor do anel de foco (accessibility & inputs ativos).

#### B. Superfícies, Layout & Estrutura
* `--color-background`: Fundo global do aplicativo (`body`).
* `--color-surface`: Fundo de cards, modais e containers.
* `--color-surface-hover`: Hover em linhas de tabelas e cards interativos.
* `--color-sidebar-bg`: Fundo da barra de navegação lateral (Sidebar).
* `--color-sidebar-text`: Cor do texto e ícones na Sidebar.
* `--color-sidebar-active`: Fundo do item selecionado na Sidebar.
* `--color-navbar-bg`: Fundo da barra de navegação superior (Header/Navbar).
* `--color-navbar-text`: Cor do texto/elementos no Navbar.

#### C. Tipografia & Conteúdo
* `--color-text-main`: Cor do texto principal (títulos e corpo).
* `--color-text-muted`: Cor de textos secundários/subtítulos.
* `--color-text-inverse`: Cor do texto sobre fundos escuros/primários.
* `--font-family-sans`: Família tipográfica do corpo (ex: `'Inter', sans-serif`).
* `--font-family-heading`: Família tipográfica de títulos.

#### D. Bordas, Divisores & Geometria
* `--color-border`: Cor das bordas de cards, tabelas e inputs.
* `--color-border-subtle`: Divisores sutis.
* `--radius-sm`: Arredondamento pequeno (inputs, badges - ex: `6px`).
* `--radius-md`: Arredondamento médio (botões, dropdowns - ex: `10px`).
* `--radius-lg`: Arredondamento grande (cards, modais - ex: `16px`).
* `--shadow-card`: Sombreamento padrão dos cards.

#### E. Status & Feedback
* `--color-success`: Cor de sucesso/confirmação (leads qualificados, ganhos).
* `--color-warning`: Cor de alerta/aviso.
* `--color-danger`: Cor de erro/urgência.
* `--color-info`: Cor informativa/notificações.

#### F. Código CSS Customizado (Advanced Override)
* `custom_css_override`: Bloco de texto livre para inserção de seletores CSS avançados específicos do tenant.

---

### 2. ESPECIFICAÇÃO DA NOVA TELA: "GERENCIADOR DE TEMAS WHITE-LABEL"

A nova tela deve ser uma seção dedicada (ex: `/settings/white-label` no app completo ou sub-aba exclusiva `settingsTab === 'theme_manager'` no protótipo), dividida nas seguintes áreas:

#### 🟢 Área 1: Barra de Ações & Perfil de Escolhas de Temas (Presets & Temas Customizados Criados)
* **Tema Padrão Inicial da Demo**: **🖤 Obsidian Night** (Dark Slate #0F172A / Purple #8B5CF6).
* **Galeria do Perfil de Escolhas (Presets + Temas Criados pelo Usuário)**:
  - 🖤 **Obsidian Night** *(Padrão Ativo / Default Demo)*
  - 🌸 **Sakura Bloom**
  - 🌲 **Emerald Garden**
  - 🌊 **Ocean Breeze**
  - 🌅 **Amber Warmth**
  - 👑 **Midnight Gold**
  - 🎨 *[Lista Dinâmica de Temas Criados e Aprovados pelo Tenant]*
* **Barra de Ferramentas do Gerenciador**:
  - Botão `👁️ Abrir Sub-tela de Preview & Teste`: Abre a visualização em tela cheia do aplicativo com as variáveis em rascunho.
  - Botão `💾 Salvar Rascunho`: Salva o rascunho sem publicar globalmente.
  - Botão `🔄 Restaurar Padrões`: Reseta as variáveis para o tema Obsidian Night.
  - Botão `📤 Exportar Tema (JSON)` / `📥 Importar Tema (JSON)`.

#### 🟢 Área 2: Editor Avançado de Design Tokens (Categorizado em Abas / Acordeões)
Organizar os controles em abas ou grupos expansíveis bem definidos:
1. **Marca & Interação**: Pickers de Cor Hexadecimal + RGBA para Primary, Secondary, Accent e Focus Ring.
2. **Superfícies & Layout**: Controles de cores para Body, Cards, Sidebar e Topbar.
3. **Tipografia & Textos**: Seletores de fontes (Google Fonts), cores de texto principal, muted e inverso.
4. **Bordas & Geometria**: Controles numéricos/sliders de Border-Radius (`--radius-sm`, `--radius-md`, `--radius-lg`) e cor de borda.
5. **Status & Feedback**: Pickers de cor para Success, Warning, Danger e Info.
6. **Injetor CSS Avançado**: Editor de código Monaco/CodeMirror (ou `textarea` estilizado monospace) para regras CSS customizadas.

#### 🟢 Área 3: SUB-TELA DEDICADA DE PREVIEW & FLUXO DE APROVAÇÃO (`settingsSubTab === 'theme_preview'` ou Modal Fullscreen)
Esta sub-tela permite experimentar o novo visual em um cenário real antes de torná-lo oficial:
* **Barra de Aprovação Fixa no Topo (Sticky Approval Banner)**:
  - Indicador visual: `⚠️ MODO PREVIEW DE RASCUNHO DE TEMA`.
  - Botão `✅ Aprovar e Criar Novo Tema`: Abre o modal **"Nomear Novo Tema"**. O usuário digita o nome (ex: *"Tema Black Gold 2026"*), confirma e o tema é salvo e adicionado ao **Perfil de Escolhas** do Tenant como tema ativo.
  - Botão `❌ Rejeitar Alterações`: Descarta todas as modificações temporárias e restaura o tema anterior sem salvar.
  - Botão `✏️ Voltar ao Editor`: Retorna à tela de ajuste de tokens mantendo os rascunhos.
* **Canvas de Simulação Completa do App**:
  - Exibe mini-instâncias interativas do Dashboard, Sidebar, Topbar, Tabela de Leads, Modais de Ação e Cards de Métricas renderizados estritamente com as variáveis do rascunho em teste.

#### 🟢 Área 4: Branding & Ativos de Mídia
* **Logotipos**:
  - Logo Principal (Modo Claro) — URL / Upload + Preview.
  - Logo Principal (Modo Escuro) — URL / Upload + Preview.
  - Ícone / Favicon / Logo Reduzido para Sidebar Recolhida.
* **Rodapé Customizado**:
  - Toggle de remoção da chancela "Powered by Revenue SDR OS".
  - Texto de Direitos Autorais / Copyright.

---

### 3. IMPLEMENTAÇÃO NO BACKEND (REVENUE SDR OS / FASTAPI + SQLMODEL)

#### Model & Migrations (`app/themes/models.py` & Alembic)
Estender a entidade `Organization` e criar a tabela associada `OrganizationTheme` (herdando de `TenantMixin`), permitindo múltiplos temas salvos no **Perfil de Escolhas** da organização:

```python
from typing import Optional, Dict, Any
from sqlmodel import Field, JSON
from app.db.base import TenantMixin, TimestampMixin, prefixed_id

class OrganizationTheme(TenantMixin, TimestampMixin, table=True):
    __tablename__ = "organization_themes"

    id: str = Field(default_factory=lambda: prefixed_id("thm"), primary_key=True)
    name: str = Field(default="Novo Tema Customizado", max_length=100)
    preset_base: str = Field(default="obsidian_night", max_length=50) # Default demo
    is_active: bool = Field(default=False, index=True)
    is_system_preset: bool = Field(default=False)
    
    # Dicionário de Tokens CSS (Chave -> Valor CSS)
    css_tokens: Dict[str, str] = Field(default_factory=dict, sa_type=JSON)
    
    # Injeção de CSS personalizado
    custom_css: Optional[str] = Field(default=None)
    
    # Logotipos e branding
    logo_light_url: Optional[str] = Field(default=None)
    logo_dark_url: Optional[str] = Field(default=None)
    favicon_url: Optional[str] = Field(default=None)
    hide_watermark: bool = Field(default=False)
    footer_text: Optional[str] = Field(default=None)
```

#### Preset Padrão Inicial (Seed / Fallback)
Garantir que a semente inicial de temas (`THEME_PRESETS`) configure o **Obsidian Night** como tema ativo default:

```python
DEFAULT_THEME_PRESET = "obsidian_night"

OBSIDIAN_NIGHT_TOKENS = {
    "--color-primary": "#8B5CF6",
    "--color-primary-hover": "#7C3AED",
    "--color-primary-light": "rgba(139, 92, 246, 0.15)",
    "--color-secondary": "#06B6D4",
    "--color-secondary-hover": "#0891B2",
    "--color-accent": "#F43F5E",
    "--color-background": "#0F172A",
    "--color-surface": "#1E293B",
    "--color-surface-hover": "#334155",
    "--color-sidebar-bg": "#020617",
    "--color-sidebar-text": "#94A3B8",
    "--color-sidebar-active": "#8B5CF6",
    "--color-navbar-bg": "#1E293B",
    "--color-navbar-text": "#F8FAFC",
    "--color-text-main": "#F9FAFB",
    "--color-text-muted": "#9CA3AF",
    "--color-text-inverse": "#0F172A",
    "--color-border": "#334155",
    "--color-border-subtle": "#1E293B",
    "--radius-sm": "6px",
    "--radius-md": "10px",
    "--radius-lg": "16px"
}
```

#### Endpoints da API (`app/themes/api.py`)
1. `GET /api/v1/theme/list`: Lista todos os temas disponíveis no perfil de escolhas do tenant (presets + temas customizados aprovados).
2. `POST /api/v1/theme/approve`: Recebe o rascunho de tokens e o `name` do novo tema, salva na tabela `organization_themes`, define-o como `is_active=True` e adiciona ao perfil de escolhas.
3. `POST /api/v1/theme/activate/{theme_id}`: Alterna o tema ativo do tenant para um dos temas salvos no perfil.

---

### 4. IMPLEMENTAÇÃO NO FRONTEND PROTÓTIPO (`01_SDR_Prototype` / ALPINE.JS)

No repositório de protótipo (`01_SDR_Prototype`), estruture o estado reativo com a sub-tela de preview e o modal de aprovação:

```javascript
function themeManagerApp() {
  return {
    activePreset: 'obsidian_night', // Tema padrão da demo
    isPreviewMode: false,
    showApprovalModal: false,
    newThemeName: '',
    
    // Lista de escolhas (presets + criados)
    savedThemes: [
      { id: 'obsidian_night', name: 'Obsidian Night (Default)', isPreset: true },
      { id: 'sakura_bloom', name: 'Sakura Bloom', isPreset: true },
      { id: 'emerald_garden', name: 'Emerald Garden', isPreset: true },
      { id: 'ocean_breeze', name: 'Ocean Breeze', isPreset: true },
      { id: 'amber_warmth', name: 'Amber Warmth', isPreset: true }
    ],
    
    draftTokens: { ...OBSIDIAN_NIGHT_TOKENS },
    activeTokens: { ...OBSIDIAN_NIGHT_TOKENS },
    
    openPreview() {
      this.isPreviewMode = true;
      this.applyTokensToDOM(this.draftTokens);
    },
    
    rejectChanges() {
      this.isPreviewMode = false;
      this.showApprovalModal = false;
      this.draftTokens = { ...this.activeTokens };
      this.applyTokensToDOM(this.activeTokens); // Restaura o tema anterior
    },
    
    approveAndSaveTheme() {
      if (!this.newThemeName.trim()) return;
      
      const newThemeId = 'custom_' + Date.now();
      const newThemeObj = {
        id: newThemeId,
        name: this.newThemeName.trim(),
        tokens: { ...this.draftTokens },
        isPreset: false
      };
      
      this.savedThemes.push(newThemeObj);
      this.activePreset = newThemeId;
      this.activeTokens = { ...this.draftTokens };
      this.applyTokensToDOM(this.activeTokens);
      
      this.showApprovalModal = false;
      this.isPreviewMode = false;
      alert(`Sucesso! O tema "${newThemeObj.name}" foi criado, aprovado e adicionado ao seu perfil de escolhas!`);
    },
    
    applyTokensToDOM(tokens) {
      Object.entries(tokens).forEach(([key, val]) => {
        document.documentElement.style.setProperty(key, val);
      });
    }
  }
}
```

---

### 5. CHECKLIST DE VALIDAÇÃO DE ENTREGA

```
[ ] Tema Padrão da Demo configurado como "Obsidian Night" por default
[ ] Sub-tela/Modal de Preview Interativo exibindo o app completo com o rascunho
[ ] Botão "Aprovar": abre modal de nomeação do tema e adiciona o novo tema ao perfil de escolhas do tenant
[ ] Botão "Rejeitar": descarta rascunho e restaura perfeitamente o tema ativo anterior
[ ] Todos os 18+ Design Tokens CSS catalogados e aplicados no :root
[ ] Galeria de escolhas atualizada dinamicamente com temas salvos e aprovados
[ ] Testes unitários de isolamento por tenant no backend (pytest) 100% verdes
[ ] Linting limpo com ruff check & ruff format
```

---
**FIM DO PROMPT**
