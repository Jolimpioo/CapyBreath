from typing import Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID

# base schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,  # Permite criar a partir de ORM models
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class TimestampSchema(BaseSchema):
    created_at: datetime = Field(
        ...,
        description="Data de criação"
    )
    updated_at: datetime = Field(
        ...,
        description="Data da última atualização"
    )


class UUIDSchema(BaseSchema):
    id: UUID = Field(
        ...,
        description="Identificador único"
    )


# response messages
class MessageResponse(BaseSchema):
    message: str = Field(
        ...,
        description="Mensagem de sucesso ou informação"
    )


class ErrorResponse(BaseSchema):
    detail: str = Field(
        ...,
        description="Detalhes do erro"
    )
    error_code: str | None = Field(
        None,
        description="Código do erro (opcional)"
    )


# pagination
T = TypeVar('T')

class PaginatedParams(BaseSchema):
    page: int = Field(
        1,
        ge=1,
        description="Número da página (inicia em 1)"
    )
    size: int = Field(
        20,
        ge=1,
        le=100,
        description="Itens por página (máx: 100)"
    )
    sort: str | None = Field(
        None,
        description="Campo para ordenação"
    )
    order: str = Field(
        "desc",
        pattern="^(asc|desc)$",
        description="Direção da ordenação: asc ou desc"
    )


class PaginatedResponse(BaseSchema, Generic[T]):
    items: list[T] = Field(
        ...,
        description="Lista de itens da página atual"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total de itens (todas as páginas)"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Página atual"
    )
    size: int = Field(
        ...,
        ge=1,
        description="Itens por página"
    )
    pages: int = Field(
        ...,
        ge=0,
        description="Total de páginas"
    )

    @property
    def has_next(self) -> bool:
        """Verifica se há próxima página"""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Verifica se há página anterior"""
        return self.page > 1


# filtros
class DateRangeFilter(BaseSchema):
    start_date: datetime | None = Field(
        None,
        description="Data inicial (inclusive)"
    )
    end_date: datetime | None = Field(
        None,
        description="Data final (inclusive)"
    )