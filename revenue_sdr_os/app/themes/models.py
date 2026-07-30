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
    "--color-primary": "#A855F7",
    "--color-primary-hover": "#9333EA",
    "--color-primary-light": "rgba(168, 85, 247, 0.18)",
    "--color-secondary": "#22D3EE",
    "--color-secondary-hover": "#06B6D4",
    "--color-accent": "#FF2E93",
    "--color-background": "#0B0F19",
    "--color-surface": "rgba(26, 35, 56, 0.65)",
    "--color-surface-hover": "rgba(34, 46, 74, 0.75)",
    "--color-sidebar-bg": "rgba(11, 15, 25, 0.85)",
    "--color-sidebar-text": "#94A3B8",
    "--color-sidebar-active": "#A855F7",
    "--color-navbar-bg": "rgba(11, 15, 25, 0.82)",
    "--color-navbar-text": "#F8FAFC",
    "--color-text-main": "#F8FAFC",
    "--color-text-muted": "#9CA3AF",
    "--color-text-inverse": "#0B0F19",
    "--color-border": "rgba(255, 255, 255, 0.12)",
    "--color-border-subtle": "rgba(255, 255, 255, 0.08)",
    "--radius-sm": "8px",
    "--radius-md": "12px",
    "--radius-lg": "18px"
}
