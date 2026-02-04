from uuid import UUID
from typing import Sequence
from datetime import datetime

from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_achievement_repository import UserAchievementRepository
from app.schemas.user import (
    UserUpdate,
    UserResponse,
    UserStatsResponse,
    UserProfile
)
from app.core.security import get_password_hash
from app.core.redis_client import cache, invalidate_user_stats
from app.core.config import settings


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        session_repo: SessionRepository,
        user_achievement_repo: UserAchievementRepository
    ):
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.user_achievement_repo = user_achievement_repo


    # get user
    async def get_user_by_id(self, user_id: UUID) -> UserResponse | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.is_deleted:
            return None
        return UserResponse.model_validate(user)

    async def get_active_user(self, user_id: UUID) -> UserResponse | None:
        user = await self.user_repo.get_active_by_id(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)


    # update user
    async def update_user(
        self,
        user_id: UUID,
        user_update: UserUpdate
    ) -> UserResponse | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.is_deleted:
            return None

        # Atualiza apenas campos fornecidos
        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            return UserResponse.model_validate(user)

        updated_user = await self.user_repo.update_by_id(
            user_id,
            **update_data
        )

        # Invalida cache
        await invalidate_user_stats(str(user_id))

        return UserResponse.model_validate(updated_user)


    # user stats
    async def get_user_stats(
        self,
        user_id: UUID,
        use_cache: bool = True
    ) -> UserStatsResponse | None:
        # Tenta cache primeiro
        if use_cache:
            cache_key = f"stats:{user_id}:full"
            cached = await cache.get_json(cache_key)
            if cached:
                return UserStatsResponse.model_validate(cached)

        user = await self.user_repo.get_by_id(user_id)
        if not user or user.is_deleted:
            return None

        stats = UserStatsResponse.model_validate(user)

        # Salva no cache
        if use_cache:
            cache_key = f"stats:{user_id}:full"
            await cache.set_json(
                cache_key,
                stats.model_dump(mode='json'),
                ttl=settings.cache_ttl_stats
            )

        return stats

    async def get_user_profile(
        self,
        user_id: UUID
    ) -> UserProfile | None:
        """Retorna perfil completo com estatísticas"""
        stats = await self.get_user_stats(user_id, use_cache=True)
        if not stats:
            return None

        return UserProfile.model_validate(stats)


    # leaderboards
    async def get_top_by_retention(
        self,
        limit: int = 10
    ) -> list[UserStatsResponse]:
        users = await self.user_repo.get_top_users_by_retention(limit)
        return [UserStatsResponse.model_validate(u) for u in users]

    async def get_top_by_streak(
        self,
        limit: int = 10
    ) -> list[UserStatsResponse]:
        users = await self.user_repo.get_top_users_by_streak(limit)
        return [UserStatsResponse.model_validate(u) for u in users]

    async def get_most_active(
        self,
        limit: int = 10
    ) -> list[UserStatsResponse]:
        users = await self.user_repo.get_most_active_users(limit)
        return [UserStatsResponse.model_validate(u) for u in users]


    # user management
    async def deactivate_user(self, user_id: UUID) -> bool:
        success = await self.user_repo.deactivate_user(user_id)
        if success:
            await invalidate_user_stats(str(user_id))
        return success

    async def activate_user(self, user_id: UUID) -> bool:
        success = await self.user_repo.activate_user(user_id)
        if success:
            await invalidate_user_stats(str(user_id))
        return success

    async def delete_user(self, user_id: UUID) -> bool:
        """Soft delete do usuário"""
        success = await self.user_repo.soft_delete_by_id(user_id)
        if success:
            await invalidate_user_stats(str(user_id))
        return success


    # search
    async def search_users(
        self,
        query: str,
        limit: int = 10
    ) -> list[UserResponse]:
        users = await self.user_repo.search_by_username(query, limit)
        return [UserResponse.model_validate(u) for u in users]


    # update password
    async def update_password(
        self,
        user_id: UUID,
        new_password: str
    ) -> bool:
        password_hash = get_password_hash(new_password)
        updated = await self.user_repo.update_by_id(
            user_id,
            password_hash=password_hash
        )
        return updated is not None


    # verify email
    async def verify_email(self, user_id: UUID) -> bool:
        return await self.user_repo.verify_email(user_id)


    # update avatar
    async def update_avatar(
        self,
        user_id: UUID,
        avatar_url: str
    ) -> UserResponse | None:
        updated = await self.user_repo.update_by_id(
            user_id,
            avatar_url=avatar_url
        )
        if updated:
            await invalidate_user_stats(str(user_id))
            return UserResponse.model_validate(updated)
        return None