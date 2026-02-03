from typing import Sequence
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement, AchievementCategory, AchievementRarity
from app.repositories.base_repository import BaseRepository


class AchievementRepository(BaseRepository[Achievement]):
    def __init__(self, db: AsyncSession):
        super().__init__(Achievement, db)


    # admin crud
    async def create_achievement(self, **kwargs) -> Achievement:
        return await self.create(**kwargs)

    async def get_by_name(self, name: str) -> Achievement | None:
        return await self.get_by_field("name", name)

    async def exists_by_name(self, name: str) -> bool:
        return await self.exists_by_field("name", name)


    # achievements ativos
    async def list_active_achievements(
        self,
        include_hidden: bool = False
    ) -> Sequence[Achievement]:
        conditions = [Achievement.is_active.is_(True)]

        if not include_hidden:
            conditions.append(Achievement.is_hidden.is_(False))

        result = await self.db.execute(
            select(Achievement)
            .where(and_(*conditions))
            .order_by(Achievement.display_order, Achievement.name)
        )
        return result.scalars().all()

    async def get_active_by_id(self, achievement_id: UUID) -> Achievement | None:
        result = await self.db.execute(
            select(Achievement).where(
                and_(
                    Achievement.id == achievement_id,
                    Achievement.is_active.is_(True)
                )
            )
        )
        return result.scalar_one_or_none()


    # por categoria
    async def list_by_category(
        self,
        category: AchievementCategory,
        active_only: bool = True
    ) -> Sequence[Achievement]:
        conditions = [Achievement.category == category]

        if active_only:
            conditions.append(Achievement.is_active.is_(True))

        result = await self.db.execute(
            select(Achievement)
            .where(and_(*conditions))
            .order_by(Achievement.display_order)
        )
        return result.scalars().all()


    # pela raridade
    async def list_by_rarity(
        self,
        rarity: AchievementRarity,
        active_only: bool = True
    ) -> Sequence[Achievement]:
        conditions = [Achievement.rarity == rarity]

        if active_only:
            conditions.append(Achievement.is_active.is_(True))

        result = await self.db.execute(
            select(Achievement)
            .where(and_(*conditions))
            .order_by(Achievement.display_order)
        )
        return result.scalars().all()


    # checa criterio destravamento
    async def get_achievements_by_criteria_type(
        self,
        criteria_type: str
    ) -> Sequence[Achievement]:
        result = await self.db.execute(
            select(Achievement)
            .where(
                and_(
                    Achievement.criteria_type == criteria_type,
                    Achievement.is_active.is_(True)
                )
            )
            .order_by(Achievement.criteria_value)  # Menor para maior
        )
        return result.scalars().all()

    async def check_unlockable(
        self,
        user_stats: dict[str, int],
        unlocked_ids: set[UUID]
    ) -> Sequence[Achievement]:
        # Busca todas conquistas ativas
        all_achievements = await self.list_active_achievements()

        unlockable = []
        for achievement in all_achievements:
            # Já tem?
            if achievement.id in unlocked_ids:
                continue

            # Atende critério?
            user_value = user_stats.get(achievement.criteria_type, 0)
            if user_value >= achievement.criteria_value:
                unlockable.append(achievement)

        return unlockable


    # statistics
    async def count_by_category(
        self,
        category: AchievementCategory
    ) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Achievement)
            .where(
                and_(
                    Achievement.category == category,
                    Achievement.is_active.is_(True)
                )
            )
        )
        return result.scalar_one()

    async def count_by_rarity(
        self,
        rarity: AchievementRarity
    ) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Achievement)
            .where(
                and_(
                    Achievement.rarity == rarity,
                    Achievement.is_active.is_(True)
                )
            )
        )
        return result.scalar_one()

    async def get_total_points_possible(self) -> int:
        result = await self.db.execute(
            select(func.sum(Achievement.points))
            .where(Achievement.is_active.is_(True))
        )
        return result.scalar_one() or 0


    # admin operations
    async def deactivate_achievement(
        self,
        achievement_id: UUID
    ) -> bool:
        return await self.update_by_id(
            achievement_id,
            is_active=False
        ) is not None

    async def activate_achievement(
        self,
        achievement_id: UUID
    ) -> bool:
        return await self.update_by_id(
            achievement_id,
            is_active=True
        ) is not None

    async def toggle_hidden(
        self,
        achievement_id: UUID
    ) -> Achievement | None:
        achievement = await self.get_by_id(achievement_id)
        if not achievement:
            return None

        achievement.is_hidden = not achievement.is_hidden
        return await self.update_instance(achievement)

    async def update_display_order(
        self,
        achievement_id: UUID,
        new_order: int
    ) -> bool:
        return await self.update_by_id(
            achievement_id,
            display_order=new_order
        ) is not None