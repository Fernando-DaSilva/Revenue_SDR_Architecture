from typing import List, Optional
from sqlmodel import Session, select
from app.themes.models import OrganizationTheme, OBSIDIAN_NIGHT_TOKENS
from app.core.errors import AppError, NotFoundError

def list_tenant_themes(session: Session, organization_id: str) -> List[OrganizationTheme]:
    statement = select(OrganizationTheme).where(
        OrganizationTheme.organization_id == organization_id
    )
    return list(session.exec(statement).all())

def approve_and_create_theme(
    session: Session, 
    organization_id: str, 
    name: str, 
    css_tokens: dict, 
    preset_base: str = "obsidian_night",
    custom_css: Optional[str] = None,
    logo_light_url: Optional[str] = None,
    logo_dark_url: Optional[str] = None,
    favicon_url: Optional[str] = None,
    hide_watermark: bool = False,
    footer_text: Optional[str] = None
) -> OrganizationTheme:
    # Deactivate current active themes for this organization
    active_statement = select(OrganizationTheme).where(
        OrganizationTheme.organization_id == organization_id,
        OrganizationTheme.is_active == True
    )
    for theme in session.exec(active_statement).all():
        theme.is_active = False
        session.add(theme)

    new_theme = OrganizationTheme(
        organization_id=organization_id,
        name=name,
        preset_base=preset_base,
        is_active=True,
        is_system_preset=False,
        css_tokens=css_tokens or OBSIDIAN_NIGHT_TOKENS,
        custom_css=custom_css,
        logo_light_url=logo_light_url,
        logo_dark_url=logo_dark_url,
        favicon_url=favicon_url,
        hide_watermark=hide_watermark,
        footer_text=footer_text
    )
    session.add(new_theme)
    session.commit()
    session.refresh(new_theme)
    return new_theme

def activate_tenant_theme(session: Session, organization_id: str, theme_id: str) -> OrganizationTheme:
    statement = select(OrganizationTheme).where(
        OrganizationTheme.id == theme_id,
        OrganizationTheme.organization_id == organization_id
    )
    target_theme = session.exec(statement).first()
    if not target_theme:
        raise NotFoundError("Tema nao encontrado para esta organizacao")

    # Deactivate all active themes for tenant
    active_statement = select(OrganizationTheme).where(
        OrganizationTheme.organization_id == organization_id,
        OrganizationTheme.is_active == True
    )
    for theme in session.exec(active_statement).all():
        theme.is_active = False
        session.add(theme)

    target_theme.is_active = True
    session.add(target_theme)
    session.commit()
    session.refresh(target_theme)
    return target_theme
