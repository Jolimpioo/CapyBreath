from pydantic import Field, field_validator
from datetime import datetime
from uuid import UUID
from app.schemas.common import BaseSchema, TimestampSchema, UUIDSchema

# create
class SessionCreate(BaseSchema):
    breaths_count: int = Field(
        30,
        ge=1,
        le=100,
        description="Número de respirações (Padrão: 30)"
    )
    retention_time: int = Field(
        ...,
        ge=0,
        le=3600,
        description="Tempo de retenção em segundos (máx: 1hora)"
    )
    recovery_time: int = Field(
        15,
        ge=5,
        le=60,
        description="Tempo de recuperação em seegundos (padrão: 15)"
    )
    duration_seconds: int = Field(
        ...,
        ge=1,
        description="Duração total da sessão em segundos"
    )
    notes: str | None = Field(
        None,
        max_length=500,
        description="Notas sobre a sessão (opcional)"
    )
    mood_before: int | None = Field(
        None,
        ge=1,
        le=10,
        description="Humor antes da sessão (1-10)"
    )
    mood_after: int | None = Field(
        None,
        ge=1,
        le=10,
        description="Humor após a sessão (1-10)"
    )
    technique_variant: str = Field(
        "standard",
        max_length=50,
        description="Variante da técnica utilizada"
    )

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: str | None) -> str | None:
        if v:
            return ' '.join(v.split())
        return v
    
    @field_validator('technique_variant')
    @classmethod
    def validate_technique(cls, v: str) -> str:
        allowed = ['standard', 'advanced', 'beginner', 'power']
        if v not in allowed:
            raise ValueError(
                f'Variante deve ser uma de: {", ".join(allowed)}'
            )
        return v
    

# update
class SessionUpdate(BaseSchema):
    notes: str | None = Field(
        None,
        max_length=500,
        description="Notas sobre a sessão"
    )
    mood_before: int | None = Field(
        None,
        ge=1,
        le=10,
        description="Humor antes (1-10)"
    )
    mood_after: int | None = Field(
        None,
        ge=1,
        le=10,
        description="Humor após (1-10)"
    )

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: str | None) -> str | None:
        if v:
            return ' '.join(v.split())
        return v
    

# response
class SessionResponse(UUIDSchema, TimestampSchema):
    user_id: UUID = Field(
        ...,
        description="ID do usuário dono da sessão"
    )
    breaths_count: int = Field(
        ...,
        description="Número de respirações"
    )
    retention_time: int = Field(
        ...,
        description="Tempo de retenção (segundos)"
    )
    recovery_time: int = Field(
        ...,
        description="Tempo de recuperação (segundos)"
    )
    session_date: datetime = Field(
        ...,
        description="Data e hora da sessão"
    )
    duration_seconds: int = Field(
        ...,
        description="Duração total (segundos)"
    )
    notes: str | None = Field(
        None,
        description="Notas da sessão"
    )
    mood_before: int | None = Field(
        None,
        description="Humor antes (1-10)"
    )
    mood_after: int | None = Field(
        None,
        description="Humor após (1-10)"
    )
    technique_variant: str = Field(
        ...,
        description="Variante da técnica"
    )

    @property
    def mood_improvement(self) -> int | None:
        if self.mood_before is None or self.mood_after is None:
            return None
        return self.mood_after - self.mood_before
        

class SessionDetailResponse(SessionResponse):
    is_personal_best: bool = Field(
        ...,
        description="Indica se foi o melhor tempo do usuário"
    )


# list
class SessionListItem(UUIDSchema):
    breaths_count: int
    retention_time: int
    session_date: datetime
    technique_variant: str
    mood_improvement: int | None = None
    is_personal_best: bool = False


# statistics
class SessionStatsBase(BaseSchema):
    sessions_count: int = Field(
        ...,
        ge=0,
        description="Número de sessões"
    )
    total_retention_time: int = Field(
        ...,
        ge=0,
        description="Tempo total de retenção (segundos)"
    )
    average_retention_time: float = Field(
        ...,
        ge=0,
        description="Média de retenção (segundos)"
    )
    best_retention_time: int = Field(
        ...,
        ge=0,
        description="Melhor tempo de retenção (segundos)"
    )


class PeriodStats(SessionStatsBase):
    pass


class SessionsSummary(BaseSchema):
    total_sessions: int = Field(
        ...,
        ge=0,
        description="Total de sessões"
    )
    total_retention_time: int = Field(
        ...,
        ge=0,
        description="Tempo total acumulado (segundos)"
    )
    average_retention_time: float = Field(
        ...,
        ge=0,
        description="Média geral (segundos)"
    )
    best_retention_time: int = Field(
        ...,
        ge=0,
        description="Melhor tempo (segundos)"
    )
    current_streak: int = Field(
        ...,
        ge=0,
        description="Sequência atual"
    )
    longest_streak: int = Field(
        ...,
        ge=0,
        description="Maior sequência"
    )
    total_breaths: int = Field(
        ...,
        ge=0,
        description="Total de respirações"
    )
    last_7_days: PeriodStats = Field(
        ...,
        description="Estatísticas dos últimos 7 dias"
    )
    last_30_days: PeriodStats = Field(
        ...,
        description="Estatísticas dos últimos 30 dias"
    )


# progress
class ProgressDataPoint(BaseSchema):
    date: str = Field(
        ...,
        description="Data (YYYY-MM-DD)"
    )
    sessions_count: int = Field(
        ...,
        ge=0,
        description="Sessões nesse dia"
    )
    total_retention_time: int = Field(
        ...,
        ge=0,
        description="Retenção total do dia (segundos)"
    )
    average_retention_time: float = Field(
        ...,
        ge=0,
        description="Média do dia (segundos)"
    )
    best_retention_time: int = Field(
        ...,
        ge=0,
        description="Melhor do dia (segundos)"
    )


class ProgressResponse(BaseSchema):
    data_points: list[ProgressDataPoint] = Field(
        ...,
        description="Dados diários"
    )
    period_days: int = Field(
        ...,
        ge=1,
        description="Período em dias"
    )
    trend: str = Field(
        ...,
        pattern="^(improving|stable|declining)$",
        description="Tendência geral"
    )


# mood
class MoodCorrelationResponse(BaseSchema):
    average_mood_before: float = Field(
        ...,
        ge=0,
        description="Média de humor antes"
    )
    average_mood_after: float = Field(
        ...,
        ge=0,
        description="Média de humor após"
    )
    average_improvement: float = Field(
        ...,
        description="Melhora média"
    )
    correlation_retention_improvement: float = Field(
        ...,
        ge=-1,
        le=1,
        description="Correlação de Pearson"
    )
    sessions_with_mood: int = Field(
        ...,
        ge=0,
        description="Sessões com dados de humor"
    )