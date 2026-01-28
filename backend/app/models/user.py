from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.models.base import Base, TimestampMixin, UUIDMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.user_achievement import UserAchievement

class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
        
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True    
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    total_sessions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    total_retention_time: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Tempo total de retenção em segundos"
    )

    best_retention_time: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Melhor tempo de retenção em segundos"
    )

    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Dias consecutivos praticando"
    )

    longest_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Maior sequência de dias consecutivos"
    )

    last_session_date: Mapped[datetime | None] = mapped_column(
        nullable=True
)

    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
        
    def update_stats(
        self,
        retention_time: int,
        session_date: datetime
    ) -> None:
        self.total_sessions += 1
        self.total_retention_time += retention_time

        if retention_time > self.best_retention_time:
            self.best_retention_time = retention_time

        if self.last_session_date:
            days_diff = (session_date.date() - self.last_session_date.date()).days

            if days_diff == 1:
                self.current_streak += 1
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
                
            elif days_diff > 1:
                self.current_streak = 1

        else:
            self.current_streak = 1
            self.longest_streak = 1

        self.last_session_date = session_date

    @property
    def average_retention_time(self) -> float:
        if self.total_sessions == 0:
            return 0.0
        return self.total_retention_time / self.total_sessions