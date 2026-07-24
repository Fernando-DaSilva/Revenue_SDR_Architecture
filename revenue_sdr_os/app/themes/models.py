from typing import Optional, Dict, Any
from sqlmodel import Field, JSON, SQLModel
from app.db.base import TenantMixin, TimestampMixin, prefixed_id

class OrganizationTheme(TenantMixin, TimestampMixin, table=True):
    __tablename__ = "organization_themes"

    id: str = Field(default_factory=lambda: prefixed_id("thm"), primary_key=True)
    name: str = Field(default="Novo Tema Customizado", max_length=100)
    preset_base: str = Field(default="obsidian_night", max_length=50) # Default demo
    is_active: bool = Field(default=False, index=True)
    is_system_preset: bool = Field(default=False)
    
    # Dicionario de Tokens CSS (Chave -> Valor CSS)
    css_tokens: Dict[str, str] = Field(default_factory=dict, sa_type=JSON)
    
    # Injecao de CSS personalizado
    custom_css: Optional[str] = Field(default=None)
    
    # Logotipos e branding
    logo_light_url: Optional[str] = Field(default=None)
    logo_dark_url: Optional[str] = Field(default=None)
    favicon_url: Optional[str] = Field(default=None)
    hide_watermark: bool = Field(default=False)
    footer_text: Optional[str] = Field(default=None)

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
