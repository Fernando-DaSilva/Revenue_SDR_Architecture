from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.db.session import get_session
from app.tenancy.middleware import get_current_organization_id
from app.themes.schemas import ThemeApproveRequest, ThemeResponse
from app.themes import service

router = APIRouter(prefix="/api/v1/theme", tags=["themes"])

@router.get("/list", response_model=List[ThemeResponse])
def list_themes(
    session: Session = Depends(get_session),
    organization_id: str = Depends(get_current_organization_id)
):
    """Lista todos os temas disponiveis no perfil de escolhas da organizacao."""
    return service.list_tenant_themes(session=session, organization_id=organization_id)

@router.post("/approve", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
def approve_theme(
    payload: ThemeApproveRequest,
    session: Session = Depends(get_session),
    organization_id: str = Depends(get_current_organization_id)
):
    """Aprova e publica um novo tema a partir do rascunho de tokens."""
    return service.approve_and_create_theme(
        session=session,
        organization_id=organization_id,
        name=payload.name,
        preset_base=payload.preset_base,
        css_tokens=payload.css_tokens,
        custom_css=payload.custom_css,
        logo_light_url=payload.logo_light_url,
        logo_dark_url=payload.logo_dark_url,
        favicon_url=payload.favicon_url,
        hide_watermark=payload.hide_watermark or False,
        footer_text=payload.footer_text
    )

@router.post("/activate/{theme_id}", response_model=ThemeResponse)
def activate_theme(
    theme_id: str,
    session: Session = Depends(get_session),
    organization_id: str = Depends(get_current_organization_id)
):
    """Alterna o tema ativo da organizacao."""
    return service.activate_tenant_theme(session=session, organization_id=organization_id, theme_id=theme_id)
