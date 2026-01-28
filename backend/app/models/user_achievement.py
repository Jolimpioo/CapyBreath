from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.achievement import Achievement

class UserAchievement(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_achievements"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    achievement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False
    )

    unlocked_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="Data e hora em que a conquista foi desbloqueada"
    )

    progress_value: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Valor de progresso atual"
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_achievements"
    )

    achievement: Mapped["Achievement"] = relationship(
        "Achievement",
        back_populates="user_achievements"
    )  

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "achievement_id",
            name="uq_user_achievement"
        ),

        Index(
            "ix_user_achievements_user_unlocked",
            "user_id",
            "unlocked_at"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<UserAchievement(user_id={self.user_id}, "
            f"achievement_id={self.achievement_id})>"
        )
    
    @property
    def is_recent(self) -> bool:
        now = datetime.now(timezone.utc)
        delta = now - self.unlocked_at
        return delta.total_seconds() < 86400
    
    def update_progress(self, new_value: int) -> bool:
        if new_value > self.progress_value:
            self.progress_value = new_value
            return True
        return False