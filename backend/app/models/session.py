from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey,CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User

class Session(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    breaths_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
        comment="Número de respirações realizadas"
    )

    retention_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Tempo de retenção em segundos"
    )

    recovery_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15,
        comment="Tempo de recuperação em segundos"
    )

    session_date: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="Data e hora em que a sessão foi realizada"
    )

    duration_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Duração total da sessão em segundos"
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Notas ou comentários sobre a sessão"
    )

    mood_before: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Humor antes da sessão (1-10)"
    )

    mood_after: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Humor após a sessão (1-10)"
    )

    technique_variant: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="standard",
        comment="Variante da técnica utilizada na sessão"
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="sessions"
    )

    __table_args__ = (
        CheckConstraint(
            "retention_time >= 0",
            name="retention_time_positive"
        ),
        CheckConstraint(
            "breaths_count > 0",
            name="breaths_count_positive"
        ),
        CheckConstraint(
            "duration_seconds > 0",
            name="duration_seconds_positive"
        ),
        CheckConstraint(
            "mood_before >=1 AND mood_before <=10",
            name="mood_before_range"
        ),
        CheckConstraint(
            "mood_after >=1 AND mood_after <=10",
            name="mood_after_range"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Session(id={self.id}, user_id={self.user_id}, "
            f"retention_time={self.retention_time}s)>"
        )
    
    @property
    def is_personal_best(self) -> bool:
        if not self.user:
            return False
        return self.retention_time == self.user.best_retention_time
    
    @property
    def mood_improvement(self) -> int | None:
        if self.mood_before is None or self.mood_after is None:
            return None
        return self.mood_after - self.mood_before
    
    def calculate_duration(
        self,
        breath_duration: int = 4,
        recovery_time: int = 15
    ) -> int:
        breathing_phase = self.breaths_count * breath_duration
        retention_phase = self.retention_time
        recovery_phase = recovery_time

        return breathing_phase + retention_phase + recovery_phase