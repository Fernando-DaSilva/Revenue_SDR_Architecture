# templates/sqlmodel-translation-model.py
"""
Template do modelo SQLModel para armazenamento de traduções customizadas por usuário.
Isso segue a convenção do TenantMixin e IDs com prefixo.
"""
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.db.base import TenantMixin, prefixed_id

if TYPE_CHECKING:
    from app.users.models import User


class UserTranslation(TenantMixin, table=True):
    """
    Tabela que armazena a sobrescrita individual de traduções por usuário e tela (fabric).
    Toda linha possui isolation por organization_id via TenantMixin.
    """
    __tablename__ = "user_translations"

    id: str = Field(
        default_factory=lambda: prefixed_id("utr"),
        primary_key=True,
    )

    # Identificadores de Relacionamento
    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
    )
    
    # Contexto da Tradução
    screen: str = Field(
        max_length=100,
        index=True,
        nullable=False,
    )  # ex: "login", "dashboard", "leads"
    
    key: str = Field(
        max_length=100,
        index=True,
        nullable=False,
    )  # ex: "welcome_message", "submit_button"
    
    locale: str = Field(
        max_length=10,
        index=True,
        nullable=False,
    )  # ex: "pt-BR", "es-ES", "en-GB", "de-DE", "lt-LT"

    # Valor da Tradução
    value: str = Field(
        max_length=1000,
        nullable=False,
    )

    # Relationships
    user: "User" = Relationship(back_populates="translations")
