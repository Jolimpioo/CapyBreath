from pydantic import Field, EmailStr, HttpUrl, field_validator
from datetime import datetime
from uuid import UUID
from app.schemas.common import BaseSchema, TimestampSchema, UUIDSchema

# base user
class UserBase(BaseSchema):
    email: EmailStr = Field(
        ...,
        description="Email do usuário"
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nome de usuário"
    )
    full_name: str | None = Field(
        None,
        max_length=255,
        description="Nome completo"
    )


# update
class UserUpdate(BaseSchema):
    full_name: str | None = Field(
        None,
        max_length=255,
        description="Nome completo"
    )
    avatar_url: HttpUrl | None = Field(
        None,
        description="URL do avatar"
    )

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str | None) -> str | None:
        if v:
            return ' '.join(v.split())
        return v


# reponse
class UserResponse(UUIDSchema, TimestampSchema, UserBase):
    avatar_url: str | None = Field(
        None,
        description="URL do avatar"
    )
    is_active: bool = Field(
        ...,
        description="Usuário está ativo"
    )
    is_verified: bool = Field(
        ...,
        description="Email verificado"
    )


class UserStatsResponse(UserResponse):
    total_sessions: int = Field(
        ...,
        ge=0,
        description="Total de sessões completadas"
    )
    total_retention_time: int = Field(
        ...,
        ge=0,
        description="Tempo total de retenção (segundos)"
    )
    best_retention_time: int = Field(
        ...,
        ge=0,
        description="Melhor tempo de retenção (segundos)"
    )
    current_streak: int = Field(
        ...,
        ge=0,
        description="Sequência atual de dias consecutivos"
    )
    longest_streak: int = Field(
        ...,
        ge=0,
        description="Maior sequência de dias consecutivos"
    )
    last_session_date: datetime | None = Field(
        None,
        description="Data da última sessão"
    )

    @property
    def average_retention_time(self) -> float:
        if self.total_sessions == 0:
            return 0.0
        return self.total_retention_time / self.total_sessions


# profile
class UserProfile(UserStatsResponse):
    pass


# login response
class UserLoginResponse(BaseSchema):
    id: UUID = Field(
        ...,
        description="ID do usuário"
    )
    username: str = Field(
        ...,
        description="Nome de usuário"
    )
    email: EmailStr = Field(
        ...,
        description="Email do usuário"
    )
    full_name: str | None = Field(
        None,
        description="Nome completo"
    )
    avatar_url: str | None = Field(
        None,
        description="URL do avatar"
    )