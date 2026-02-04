from uuid import UUID
from typing import Sequence

from app.repositories.achievement_repository import AchievementRepository
from app.repositories.user_achievement_repository import UserAchievementRepository
from app.repositories.user_repository import UserRepository
from app.schemas.achievement import (
    AchievementCreate,
    AchievementUpdate,
    AchievementResponse,
    AchievementProgress,
    UnlockedAchievement,
    LockedAchievement,
    UserAchievementsResponse,
    AchievementDetail,
    AchievementUnlocked
)
from app.models.achievement import AchievementCategory, AchievementRarity
from app.core.redis_client import cache
from app.core.config import settings


class AchievementService:
    def __init__(
        self,
        achievement_repo: AchievementRepository,
        user_achievement_repo: UserAchievementRepository,
        user_repo: UserRepository
    ):
        self.achievement_repo = achievement_repo
        self.user_achievement_repo = user_achievement_repo
        self.user_repo = user_repo


    # admin - create/update achievements
    async def create_achievement(
        self,
        achievement_data: AchievementCreate
    ) -> AchievementResponse:
        exists = await self.achievement_repo.exists_by_name(
            achievement_data.name
        )
        if exists:
            raise ValueError("Conquista com este nome já existe")

        achievement = await self.achievement_repo.create_achievement(
            **achievement_data.model_dump()
        )

        return AchievementResponse.model_validate(achievement)

    async def update_achievement(
        self,
        achievement_id: UUID,
        achievement_update: AchievementUpdate
    ) -> AchievementResponse | None:
        achievement = await self.achievement_repo.get_by_id(achievement_id)
        if not achievement:
            return None

        update_data = achievement_update.model_dump(exclude_unset=True)
        if not update_data:
            return AchievementResponse.model_validate(achievement)

        updated = await self.achievement_repo.update_by_id(
            achievement_id,
            **update_data
        )

        return AchievementResponse.model_validate(updated)


    # list achievements
    async def list_all_achievements(
        self,
        include_hidden: bool = False,
        active_only: bool = True
    ) -> list[AchievementResponse]:
        achievements = await self.achievement_repo.list_active_achievements(
            include_hidden=include_hidden
        )

        return [AchievementResponse.model_validate(a) for a in achievements]

    async def list_by_category(
        self,
        category: AchievementCategory
    ) -> list[AchievementResponse]:
        achievements = await self.achievement_repo.list_by_category(
            category,
            active_only=True
        )

        return [AchievementResponse.model_validate(a) for a in achievements]

    async def list_by_rarity(
        self,
        rarity: AchievementRarity
    ) -> list[AchievementResponse]:
        achievements = await self.achievement_repo.list_by_rarity(
            rarity,
            active_only=True
        )

        return [AchievementResponse.model_validate(a) for a in achievements]


    # user achievements
    async def get_user_achievements(
        self,
        user_id: UUID,
        use_cache: bool = True
    ) -> UserAchievementsResponse:
        # Tenta cache
        if use_cache:
            cache_key = f"stats:{user_id}:achievements"
            cached = await cache.get_json(cache_key)
            if cached:
                return UserAchievementsResponse.model_validate(cached)

        # Busca conquistas desbloqueadas
        user_achievements = await self.user_achievement_repo.get_user_achievements(
            user_id,
            include_achievement=True
        )

        unlocked_ids = {ua.achievement_id for ua in user_achievements}

        # Monta lista de desbloqueadas
        unlocked = [
            UnlockedAchievement(
                **ua.achievement.__dict__,
                unlocked_at=ua.unlocked_at,
                is_recent=ua.is_recent
            )
            for ua in user_achievements
        ]

        # Busca todas as conquistas ativas
        all_achievements = await self.achievement_repo.list_active_achievements(
            include_hidden=False
        )

        # Busca stats do usuário
        user = await self.user_repo.get_by_id(user_id)
        user_stats = {
            "total_sessions": user.total_sessions,
            "best_retention_time": user.best_retention_time,
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "total_retention_time": user.total_retention_time
        } if user else {}

        # Monta lista de bloqueadas com progresso
        locked = []
        for achievement in all_achievements:
            if achievement.id not in unlocked_ids:
                # Calcula progresso
                user_value = user_stats.get(achievement.criteria_type, 0)
                target = achievement.criteria_value

                progress = AchievementProgress(
                    current=user_value,
                    target=target,
                    percentage=min((user_value / target) * 100, 100) if target > 0 else 0
                )

                locked.append(
                    LockedAchievement(
                        **achievement.__dict__,
                        progress=progress
                    )
                )

        # Calcula total de pontos
        total_points = await self.user_achievement_repo.get_total_points(user_id)

        response = UserAchievementsResponse(
            unlocked=unlocked,
            locked=locked,
            total_points=total_points,
            unlocked_count=len(unlocked),
            total_count=len(all_achievements)
        )

        # Salva no cache
        if use_cache:
            cache_key = f"stats:{user_id}:achievements"
            await cache.set_json(
                cache_key,
                response.model_dump(mode='json'),
                ttl=settings.cache_ttl_stats
            )

        return response


    # unlock achievements
    async def check_and_unlock_achievements(
        self,
        user_id: UUID
    ) -> list[AchievementUnlocked]:
        # Busca IDs já desbloqueados
        unlocked_ids = await self.user_achievement_repo.get_user_achievement_ids(
            user_id
        )

        # Busca stats do usuário
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return []

        user_stats = {
            "total_sessions": user.total_sessions,
            "best_retention_time": user.best_retention_time,
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "total_retention_time": user.total_retention_time
        }

        # Verifica quais podem ser desbloqueadas
        unlockable = await self.achievement_repo.check_unlockable(
            user_stats,
            unlocked_ids
        )

        # Desbloqueia cada uma
        newly_unlocked = []
        for achievement in unlockable:
            user_value = user_stats.get(achievement.criteria_type, 0)

            user_achievement = await self.user_achievement_repo.unlock_achievement(
                user_id=user_id,
                achievement_id=achievement.id,
                progress_value=user_value
            )

            newly_unlocked.append(
                AchievementUnlocked(
                    achievement_id=achievement.id,
                    name=achievement.name,
                    description=achievement.description,
                    icon=achievement.icon,
                    points=achievement.points,
                    rarity=achievement.rarity,
                    unlocked_at=user_achievement.unlocked_at
                )
            )

        # Invalida cache se desbloqueou algo
        if newly_unlocked:
            cache_key = f"stats:{user_id}:achievements"
            await cache.delete(cache_key)

        return newly_unlocked


    # achievement detail
    async def get_achievement_detail(
        self,
        user_id: UUID,
        achievement_id: UUID
    ) -> AchievementDetail | None:
        achievement = await self.achievement_repo.get_active_by_id(achievement_id)
        if not achievement:
            return None

        # Verifica se usuário já tem
        has_achievement = await self.user_achievement_repo.has_achievement(
            user_id,
            achievement_id
        )

        if has_achievement:
            # Busca dados de desbloqueio
            user_achievements = await self.user_achievement_repo.get_user_achievements(
                user_id,
                include_achievement=False
            )

            ua = next(
                (ua for ua in user_achievements if ua.achievement_id == achievement_id),
                None
            )

            return AchievementDetail(
                **achievement.__dict__,
                unlocked=True,
                unlocked_at=ua.unlocked_at if ua else None,
                progress=None
            )
        else:
            # Calcula progresso
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return None

            user_stats = {
                "total_sessions": user.total_sessions,
                "best_retention_time": user.best_retention_time,
                "current_streak": user.current_streak,
                "longest_streak": user.longest_streak,
                "total_retention_time": user.total_retention_time
            }

            user_value = user_stats.get(achievement.criteria_type, 0)
            target = achievement.criteria_value

            progress = AchievementProgress(
                current=user_value,
                target=target,
                percentage=min((user_value / target) * 100, 100) if target > 0 else 0
            )

            return AchievementDetail(
                **achievement.__dict__,
                unlocked=False,
                unlocked_at=None,
                progress=progress
            )


    # statistics
    async def get_achievement_stats(self) -> dict:
        total = await self.achievement_repo.count()
        total_points = await self.achievement_repo.get_total_points_possible()

        return {
            "total_achievements": total,
            "total_points_possible": total_points
        }


    # admin operations
    async def deactivate_achievement(
        self,
        achievement_id: UUID
    ) -> bool:
        return await self.achievement_repo.deactivate_achievement(achievement_id)

    async def activate_achievement(
        self,
        achievement_id: UUID
    ) -> bool:
        return await self.achievement_repo.activate_achievement(achievement_id)