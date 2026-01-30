from pydantic import Field, EmailStr, field_validator
from app.schemas.common import BaseSchema
import re

# registro
class UserRegister(BaseSchema):
    email: EmailStr = Field(
        ...,
        description="Email do usuário (único)"
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nome de usuário (único, 3-50 caracteres)"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Senha (mínimo 8 caracteres)"
    )
    full_name: str | None = Field(
        None,
        max_length=255,
        description="Nome completo (opcional)"
    )

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(
                'Username deve conter apenas letras, números, _ ou -'
            )
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter ao menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter ao menos uma letra minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Senha deve conter ao menos um número')
        return v


# login
class UserLogin(BaseSchema):
    email: EmailStr = Field(
        ...,
        description="Email do usuário"
    )
    password: str = Field(
        ...,
        description="Senha do usuário"
    )


# tokens
class TokenResponse(BaseSchema):
    access_token: str = Field(
        ...,
        description="Token de acesso (JWT)"
    )
    refresh_token: str = Field(
        ...,
        description="Token de refresh (JWT)"
    )
    token_type: str = Field(
        "bearer",
        description="Tipo do token"
    )
    expires_in: int = Field(
        ...,
        description="Tempo de expiração do access_token em segundos"
    )


class TokenRefresh(BaseSchema):
    refresh_token: str = Field(
        ...,
        description="Refresh token válido"
    )


class AccessTokenResponse(BaseSchema):
    access_token: str = Field(
        ...,
        description="Novo token de acesso (JWT)"
    )
    token_type: str = Field(
        "bearer",
        description="Tipo do token"
    )
    expires_in: int = Field(
        ...,
        description="Tempo de expiração em segundos"
    )


# payload do token
class TokenPayload(BaseSchema):
    sub: str = Field(
        ...,
        description="Subject (user_id)"
    )
    exp: int = Field(
        ...,
        description="Expiration timestamp"
    )
    type: str = Field(
        ...,
        description="Tipo do token (access ou refresh)"
    )