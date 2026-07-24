from typing import Optional, Dict
from pydantic import BaseModel, Field

class ThemeApproveRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nome do novo tema a ser criado e aprovado")
    preset_base: Optional[str] = Field(default="obsidian_night", max_length=50)
    css_tokens: Dict[str, str] = Field(default_factory=dict)
    custom_css: Optional[str] = Field(default=None)
    logo_light_url: Optional[str] = Field(default=None)
    logo_dark_url: Optional[str] = Field(default=None)
    favicon_url: Optional[str] = Field(default=None)
    hide_watermark: Optional[bool] = Field(default=False)
    footer_text: Optional[str] = Field(default=None)

class ThemeResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    preset_base: str
    is_active: bool
    is_system_preset: bool
    css_tokens: Dict[str, str]
    custom_css: Optional[str] = None
    logo_light_url: Optional[str] = None
    logo_dark_url: Optional[str] = None
    favicon_url: Optional[str] = None
    hide_watermark: bool = False
    footer_text: Optional[str] = None
