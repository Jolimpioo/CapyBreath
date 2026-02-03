from typing import Sequence
from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, and_, desc, asc, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.repositories.base_repository import BaseRepository


class SessionRepository(BaseRepository[Session]):
    def __init__(self, db: AsyncSession):
        super().__init__(Session, db)


    # queries basica
    async def create_session(
        self,
        user_id: UUID,
        **kwargs
    ) -> Session:
        return await self.create(user_id=user_id, **kwargs)

    async def get_user_sessions(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "session_date",
        order_dir: str = "desc"
    ) -> Sequence[Session]:
        # Determina campo de ordenação
        order_field = getattr(Session, order_by, Session.session_date)
        order_func = desc if order_dir == "desc" else asc

        result = await self.db.execute(
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(order_func(order_field))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def count_user_sessions(self, user_id: UUID) -> int:
        return await self.count_by_field("user_id", user_id)

    async def get_user_session(
        self,
        user_id: UUID,
        session_id: UUID
    ) -> Session | None:
        result = await self.db.execute(
            select(Session).where(
                and_(
                    Session.id == session_id,
                    Session.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()

    # statistics basica

    async def get_user_total_stats(self, user_id: UUID) -> dict:
        result = await self.db.execute(
            select(
                func.count(Session.id).label("total_sessions"),
                func.sum(Session.retention_time).label("total_retention_time"),
                func.avg(Session.retention_time).label("average_retention_time"),
                func.max(Session.retention_time).label("best_retention_time"),
                func.sum(Session.breaths_count).label("total_breaths"),
            ).where(Session.user_id == user_id)
        )
        row = result.one()

        return {
            "total_sessions": row.total_sessions or 0,
            "total_retention_time": int(row.total_retention_time or 0),
            "average_retention_time": float(row.average_retention_time or 0),
            "best_retention_time": int(row.best_retention_time or 0),
            "total_breaths": int(row.total_breaths or 0),
        }

    async def get_user_stats_by_period(
        self,
        user_id: UUID,
        days: int
    ) -> dict:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            select(
                func.count(Session.id).label("sessions_count"),
                func.sum(Session.retention_time).label("total_retention_time"),
                func.avg(Session.retention_time).label("average_retention_time"),
                func.max(Session.retention_time).label("best_retention_time"),
            ).where(
                and_(
                    Session.user_id == user_id,
                    Session.session_date >= cutoff_date
                )
            )
        )
        row = result.one()

        return {
            "sessions_count": row.sessions_count or 0,
            "total_retention_time": int(row.total_retention_time or 0),
            "average_retention_time": float(row.average_retention_time or 0),
            "best_retention_time": int(row.best_retention_time or 0),
        }


    # progress tracking
    async def get_daily_progress(
        self,
        user_id: UUID,
        days: int = 30
    ) -> list[dict]:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self.db.execute(
            select(
                func.date(Session.session_date).label("date"),
                func.count(Session.id).label("sessions_count"),
                func.sum(Session.retention_time).label("total_retention_time"),
                func.avg(Session.retention_time).label("average_retention_time"),
                func.max(Session.retention_time).label("best_retention_time"),
            )
            .where(
                and_(
                    Session.user_id == user_id,
                    Session.session_date >= cutoff_date
                )
            )
            .group_by(func.date(Session.session_date))
            .order_by(asc(func.date(Session.session_date)))
        )

        return [
            {
                "date": row.date.isoformat(),
                "sessions_count": row.sessions_count,
                "total_retention_time": int(row.total_retention_time),
                "average_retention_time": float(row.average_retention_time),
                "best_retention_time": int(row.best_retention_time),
            }
            for row in result.all()
        ]

    async def get_weekly_progress(
        self,
        user_id: UUID,
        weeks: int = 12
    ) -> list[dict]:
        cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=weeks)

        result = await self.db.execute(
            select(
                func.date_trunc("week", Session.session_date).label("week"),
                func.count(Session.id).label("sessions_count"),
                func.avg(Session.retention_time).label("average_retention_time"),
                func.max(Session.retention_time).label("best_retention_time"),
            )
            .where(
                and_(
                    Session.user_id == user_id,
                    Session.session_date >= cutoff_date
                )
            )
            .group_by(func.date_trunc("week", Session.session_date))
            .order_by(asc(func.date_trunc("week", Session.session_date)))
        )

        return [
            {
                "week": row.week.date().isoformat(),
                "sessions_count": row.sessions_count,
                "average_retention_time": float(row.average_retention_time),
                "best_retention_time": int(row.best_retention_time),
            }
            for row in result.all()
        ]


    # personal best
    async def get_personal_best(self, user_id: UUID) -> Session | None:
        result = await self.db.execute(
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(desc(Session.retention_time))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_recent_personal_bests(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Sequence[Session]:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Subquery: máximo até aquela data
        subq = (
            select(func.max(Session.retention_time))
            .where(
                and_(
                    Session.user_id == user_id,
                    Session.session_date < Session.session_date
                )
            )
            .correlate(Session)
            .scalar_subquery()
        )

        result = await self.db.execute(
            select(Session)
            .where(
                and_(
                    Session.user_id == user_id,
                    Session.session_date >= cutoff_date,
                    Session.retention_time > subq
                )
            )
            .order_by(desc(Session.session_date))
        )
        return result.scalars().all()


    # mood analise
    async def get_mood_correlation(self, user_id: UUID) -> dict:
        result = await self.db.execute(
            select(
                func.avg(Session.mood_before).label("avg_before"),
                func.avg(Session.mood_after).label("avg_after"),
                func.count(Session.id).label("count"),
            ).where(
                and_(
                    Session.user_id == user_id,
                    Session.mood_before.isnot(None),
                    Session.mood_after.isnot(None),
                )
            )
        )
        row = result.one()

        avg_before = float(row.avg_before or 0)
        avg_after = float(row.avg_after or 0)

        return {
            "average_mood_before": avg_before,
            "average_mood_after": avg_after,
            "average_improvement": avg_after - avg_before,
            "sessions_with_mood": row.count or 0,
        }

    async def get_sessions_with_mood_improvement(
        self,
        user_id: UUID,
        min_improvement: int = 2
    ) -> Sequence[Session]:
        result = await self.db.execute(
            select(Session)
            .where(
                and_(
                    Session.user_id == user_id,
                    Session.mood_before.isnot(None),
                    Session.mood_after.isnot(None),
                    (Session.mood_after - Session.mood_before) >= min_improvement
                )
            )
            .order_by(desc(Session.session_date))
        )
        return result.scalars().all()


    # filters \ serach
    async def get_sessions_by_date_range(
        self,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Sequence[Session]:
        result = await self.db.execute(
            select(Session)
            .where(
                and_(
                    Session.user_id == user_id,
                    Session.session_date >= start_date,
                    Session.session_date <= end_date
                )
            )
            .order_by(desc(Session.session_date))
        )
        return result.scalars().all()

    async def get_sessions_by_technique(
        self,
        user_id: UUID,
        technique_variant: str
    ) -> Sequence[Session]:
        result = await self.db.execute(
            select(Session)
            .where(
                and_(
                    Session.user_id == user_id,
                    Session.technique_variant == technique_variant
                )
            )
            .order_by(desc(Session.session_date))
        )
        return result.scalars().all()


    # delete
    async def delete_user_session(
        self,
        user_id: UUID,
        session_id: UUID
    ) -> bool:
        # Verifica se sessão existe e pertence ao usuário
        session = await self.get_user_session(user_id, session_id)
        if not session:
            return False

        await self.delete_by_id(session_id)
        return True