from pydantic import Field
from datetime import datetime
from uuid import UUID
from app.schemas.common import BaseSchema, TimestampSchema, UUIDSchema
from app.models.achievement import AchievementCategory, AchievementRarity

# create (admin)
class AchievementCreate(BaseSchema):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nome da conquista"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Descrição da conquista"
    )
    category: AchievementCategory = Field(
        ...,
        description="Categoria da conquista"
    )
    rarity: AchievementRarity = Field(
        AchievementRarity.COMMON,
        description="Raridade da conquista"
    )
    icon: str = Field(
        ...,
        max_length=100,
        description="Emoji ou URL do ícone"
    )
    points: int = Field(
        10,
        ge=1,
        le=1000,
        description="Pontos concedidos"
    )
    criteria_type: str = Field(
        ...,
        max_length=50,
        description="Tipo de critério (ex: total_sessions)"
    )
    criteria_value: int = Field(
        ...,
        ge=1,
        description="Valor necessário para desbloquear"
    )
    is_active: bool = Field(
        True,
        description="Conquista ativa"
    )
    is_hidden: bool = Field(
        False,
        description="Conquista oculta"
    )
    display_order: int = Field(
        0,
        ge=0,
        description="Ordem de exibição"
    )

# update(admin)
class AchievementUpdate(BaseSchema):
    name: str | None = Field(
        None,
        min_length=1,
        max_length=100
    )
    description: str | None = Field(
        None,
        min_length=1,
        max_length=500
    )
    icon: str | None = Field(
        None,
        max_length=100
    )
    points: int | None = Field(
        None,
        ge=1,
        le=1000
    )
    is_active: bool | None = None
    is_hidden: bool | None = None
    display_order: int | None = Field(
        None,
        ge=0
    )

    # response
class AchievementResponse(UUIDSchema, TimestampSchema):
    name: str = Field(
        ...,
        description="Nome da conquista"
    )
    description: str = Field(
        ...,
        description="Descrição"
    )
    category: AchievementCategory = Field(
        ...,
        description="Categoria"
    )
    rarity: AchievementRarity = Field(
        ...,
        description="Raridade"
    )
    icon: str = Field(
        ...,
        description="Ícone"
    )
    points: int = Field(
        ...,
        description="Pontos"
    )
    criteria_type: str = Field(
        ...,
        description="Tipo de critério"
    )
    criteria_value: int = Field(
        ...,
        description="Valor necessário"
    )
    is_active: bool = Field(
        ...,
        description="Está ativa"
    )
    is_hidden: bool = Field(
        ...,
        description="Está oculta"
    )
    display_order: int = Field(
        ...,
        description="Ordem de exibição"
    )

    @property
    def rarity_color(self) -> str:
        colors = {
            AchievementRarity.COMMON: "#9CA3AF",
            AchievementRarity.RARE: "#3B82F6",
            AchievementRarity.EPIC: "#A855F7",
            AchievementRarity.LEGENDARY: "#F59E0B"
        }
        return colors.get(self.rarity, "#9CA3AF")

# progress
class AchievementProgress(BaseSchema):
    current: int = Field(
        ...,
        ge=0,
        description="Valor atual"
    )
    target: int = Field(
        ...,
        ge=1,
        description="Valor alvo"
    )
    percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Porcentagem de progresso"
    )

# unlocked
class UnlockedAchievement(AchievementResponse):
    unlocked_at: datetime = Field(
        ...,
        description="Data de desbloqueio"
    )
    is_recent: bool = Field(
        ...,
        description="Desbloqueada nas últimas 24h"
    )

# locked
class LockedAchievement(AchievementResponse):
    progress: AchievementProgress = Field(
        ...,
        description="Progresso atual"
    )

# user achievements
class UserAchievementsResponse(BaseSchema):
    unlocked: list[UnlockedAchievement] = Field(
        ...,
        description="Conquistas desbloqueadas"
    )
    locked: list[LockedAchievement] = Field(
        ...,
        description="Conquistas bloqueadas"
    )
    total_points: int = Field(
        ...,
        ge=0,
        description="Total de pontos acumulados"
    )
    unlocked_count: int = Field(
        ...,
        ge=0,
        description="Total de conquistas desbloqueadas"
    )
    total_count: int = Field(
        ...,
        ge=0,
        description="Total de conquistas disponíveis"
    )

    @property
    def completion_percentage(self) -> float:
        if self.total_count == 0:
            return 0.0
        return (self.unlocked_count / self.total_count) * 100

# achievement detail
class AchievementDetail(AchievementResponse):
    unlocked: bool = Field(
        ...,
        description="Indica se foi desbloqueada"
    )
    unlocked_at: datetime | None = Field(
        None,
        description="Data de desbloqueio (se aplicável)"
    )
    progress: AchievementProgress | None = Field(
        None,
        description="Progresso (se bloqueada)"
    )

# notification
class AchievementUnlocked(BaseSchema):
    achievement_id: UUID = Field(
        ...,
        description="ID da conquista"
    )
    name: str = Field(
        ...,
        description="Nome da conquista"
    )
    description: str = Field(
        ...,
        description="Descrição"
    )
    icon: str = Field(
        ...,
        description="Ícone"
    )
    points: int = Field(
        ...,
        description="Pontos ganhos"
    )
    rarity: AchievementRarity = Field(
        ...,
        description="Raridade"
    )
    unlocked_at: datetime = Field(
        ...,
        description="Momento do desbloqueio"
    )