from typing import Sequence
from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.user_achievement import UserAchievement
from app.models.achievement import Achievement
from app.repositories.base_repository import BaseRepository


class UserAchievementRepository(BaseRepository[UserAchievement]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserAchievement, db)


    # unlock
    async def unlock_achievement(
        self,
        user_id: UUID,
        achievement_id: UUID,
        progress_value: int = 0
    ) -> UserAchievement:
        return await self.create(
            user_id=user_id,
            achievement_id=achievement_id,
            progress_value=progress_value,
            unlocked_at=datetime.now(timezone.utc)
        )

    async def has_achievement(
        self,
        user_id: UUID,
        achievement_id: UUID
    ) -> bool:
        result = await self.db.execute(
            select(func.count())
            .select_from(UserAchievement)
            .where(
                and_(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == achievement_id
                )
            )
        )
        return result.scalar_one() > 0


    # lista conquistas usuarios
    async def get_user_achievements(
        self,
        user_id: UUID,
        include_achievement: bool = True
    ) -> Sequence[UserAchievement]:
        query = select(UserAchievement).where(
            UserAchievement.user_id == user_id
        )

        if include_achievement:
            query = query.options(joinedload(UserAchievement.achievement))

        query = query.order_by(desc(UserAchievement.unlocked_at))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_user_achievement_ids(
        self,
        user_id: UUID
    ) -> set[UUID]:
        result = await self.db.execute(
            select(UserAchievement.achievement_id).where(
                UserAchievement.user_id == user_id
            )
        )
        return set(result.scalars().all())

    async def get_recent_unlocks(
        self,
        user_id: UUID,
        hours: int = 24
    ) -> Sequence[UserAchievement]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        result = await self.db.execute(
            select(UserAchievement)
            .options(joinedload(UserAchievement.achievement))
            .where(
                and_(
                    UserAchievement.user_id == user_id,
                    UserAchievement.unlocked_at >= cutoff_time
                )
            )
            .order_by(desc(UserAchievement.unlocked_at))
        )
        return result.scalars().all()


    # estatisticas
    async def count_user_achievements(self, user_id: UUID) -> int:
        return await self.count_by_field("user_id", user_id)

    async def get_total_points(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.sum(Achievement.points))
            .select_from(UserAchievement)
            .join(Achievement, UserAchievement.achievement_id == Achievement.id)
            .where(UserAchievement.user_id == user_id)
        )
        return result.scalar_one() or 0

    async def get_achievements_by_category_count(
        self,
        user_id: UUID
    ) -> dict[str, int]:
        result = await self.db.execute(
            select(
                Achievement.category,
                func.count(UserAchievement.id).label("count")
            )
            .select_from(UserAchievement)
            .join(Achievement, UserAchievement.achievement_id == Achievement.id)
            .where(UserAchievement.user_id == user_id)
            .group_by(Achievement.category)
        )

        return {row.category: row.count for row in result.all()}

    async def get_achievements_by_rarity_count(
        self,
        user_id: UUID
    ) -> dict[str, int]:
        result = await self.db.execute(
            select(
                Achievement.rarity,
                func.count(UserAchievement.id).label("count")
            )
            .select_from(UserAchievement)
            .join(Achievement, UserAchievement.achievement_id == Achievement.id)
            .where(UserAchievement.user_id == user_id)
            .group_by(Achievement.rarity)
        )

        return {row.rarity: row.count for row in result.all()}


    # progresso
    async def update_progress(
        self,
        user_id: UUID,
        achievement_id: UUID,
        new_value: int
    ) -> UserAchievement | None:
        result = await self.db.execute(
            select(UserAchievement).where(
                and_(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == achievement_id
                )
            )
        )
        user_achievement = result.scalar_one_or_none()

        if not user_achievement:
            return None

        # Método do modelo valida se deve atualizar
        if user_achievement.update_progress(new_value):
            await self.update_instance(user_achievement)

        return user_achievement


    # leaderboard
    async def get_top_users_by_achievements(
        self,
        limit: int = 10
    ) -> list[dict]:
        result = await self.db.execute(
            select(
                UserAchievement.user_id,
                func.count(UserAchievement.id).label("achievements_count")
            )
            .group_by(UserAchievement.user_id)
            .order_by(desc("achievements_count"))
            .limit(limit)
        )

        return [
            {
                "user_id": row.user_id,
                "achievements_count": row.achievements_count
            }
            for row in result.all()
        ]

    async def get_top_users_by_points(
        self,
        limit: int = 10
    ) -> list[dict]:
        result = await self.db.execute(
            select(
                UserAchievement.user_id,
                func.sum(Achievement.points).label("total_points")
            )
            .select_from(UserAchievement)
            .join(Achievement, UserAchievement.achievement_id == Achievement.id)
            .group_by(UserAchievement.user_id)
            .order_by(desc("total_points"))
            .limit(limit)
        )

        return [
            {
                "user_id": row.user_id,
                "total_points": int(row.total_points)
            }
            for row in result.all()
        ]


    # delete
    async def revoke_achievement(
        self,
        user_id: UUID,
        achievement_id: UUID
    ) -> bool:
        result = await self.db.execute(
            select(UserAchievement).where(
                and_(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == achievement_id
                )
            )
        )
        user_achievement = result.scalar_one_or_none()

        if not user_achievement:
            return False

        await self.delete_instance(user_achievement)
        return True

    async def delete_all_user_achievements(
        self,
        user_id: UUID
    ) -> int:
        achievements = await self.get_user_achievements(
            user_id,
            include_achievement=False
        )

        for ua in achievements:
            await self.delete_instance(ua)

        return len(achievements)