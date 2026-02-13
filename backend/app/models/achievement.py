from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user_achievement import UserAchievement

class AchievementCategory(str, enum.Enum):
    SESSIONS = 'sessions'
    RETENTION = 'retention'
    STREAK = 'streak'
    IMPROVEMENT = 'improvement'
    MILESTONE = 'milestone'

class AchievementRarity(str, enum.Enum):
    COMMON = 'common'
    RARE = 'rare'
    EPIC = 'epic'
    LEGENDARY = 'legendary'

class Achievement(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "achievements"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    category: Mapped[AchievementCategory] = mapped_column(
        Enum(AchievementCategory),
        nullable=False,
        index=True
    )

    rarity: Mapped[AchievementRarity] = mapped_column(
        Enum(AchievementRarity),
        nullable=False,
        default=AchievementRarity.COMMON
    )

    icon: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="url do icone"
    )

    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
        comment="Pontos concedidos ao desbloquear a conquista"
    )

    criteria_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Tipo de critério para desbloquear a conquista (e.g., 'total_sessions', best_retention, current_streak, etc."
    )

    criteria_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Valor necessário para cumprir o critério"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica se a conquista está ativa e disponível para os usuários"
    )

    is_hidden: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica se a conquista está oculta na interface do usuário" 
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Ordem de exibição das conquistas na interface do usuário"
    )

    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement",
        back_populates="achievement",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Achievement(id={self.id}, name={self.name}, category={self.category})>"
    
    def check_unlock(self, user_stats: dict) -> bool:
        if not self.is_active:
            return False
        
        stat_value = user_stats.get(self.criteria_type, 0)
        return stat_value >= self.criteria_value

    @property
    def rarity_color(self) -> str:
        colors = {
            AchievementRarity.COMMON: "#9CA3AF",      # gray
            AchievementRarity.RARE: "#3B82F6",        # blue
            AchievementRarity.EPIC: "#A855F7",        # purple
            AchievementRarity.LEGENDARY: "#F59E0B"    # amber
        }
        return colors.get(self.rarity, "#9CA3AF")