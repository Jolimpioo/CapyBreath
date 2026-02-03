from typing import Sequence
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, and_, or_, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)


    # queries especificas
    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.email == email.lower(),
                    User.deleted_at.is_(None)  # Soft delete
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.username == username.lower(),
                    User.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email_or_username(
        self,
        email: str,
        username: str
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(
                and_(
                    or_(
                        User.email == email.lower(),
                        User.username == username.lower()
                    ),
                    User.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        return await self.exists_by_field("email", email.lower())

    async def exists_by_username(self, username: str) -> bool:
        return await self.exists_by_field("username", username.lower())


    # active users
    async def get_active_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.id == user_id,
                    User.is_active.is_(True),
                    User.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_active_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[User]:
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    User.is_active.is_(True),
                    User.deleted_at.is_(None)
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(desc(User.created_at))
        )
        return result.scalars().all()


    # statistics \ leaderboard
    async def get_top_users_by_retention(
        self,
        limit: int = 10
    ) -> Sequence[User]:
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    User.is_active.is_(True),
                    User.deleted_at.is_(None),
                    User.best_retention_time > 0
                )
            )
            .order_by(desc(User.best_retention_time))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_top_users_by_streak(
        self,
        limit: int = 10
    ) -> Sequence[User]:
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    User.is_active.is_(True),
                    User.deleted_at.is_(None),
                    User.current_streak > 0
                )
            )
            .order_by(desc(User.current_streak))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_most_active_users(
        self,
        limit: int = 10
    ) -> Sequence[User]:
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    User.is_active.is_(True),
                    User.deleted_at.is_(None),
                    User.total_sessions > 0
                )
            )
            .order_by(desc(User.total_sessions))
            .limit(limit)
        )
        return result.scalars().all()


    # update stats
    async def update_stats(
        self,
        user_id: UUID,
        retention_time: int,
        session_date: datetime
    ) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Método do modelo faz os cálculos
        user.update_stats(retention_time, session_date)

        await self.update_instance(user)
        return user


    # admin operation
    async def deactivate_user(self, user_id: UUID) -> bool:
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def activate_user(self, user_id: UUID) -> bool:
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=True)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def verify_email(self, user_id: UUID) -> bool:
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_verified=True)
        )
        await self.db.commit()
        return result.rowcount > 0


    # search
    async def search_by_username(
        self,
        query: str,
        limit: int = 10
    ) -> Sequence[User]:
        result = await self.db.execute(
            select(User)
            .where(
                and_(
                    User.username.ilike(f"%{query}%"),
                    User.is_active.is_(True),
                    User.deleted_at.is_(None)
                )
            )
            .limit(limit)
            .order_by(User.username)
        )
        return result.scalars().all()