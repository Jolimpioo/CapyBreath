from uuid import UUID
from typing import Sequence
from datetime import datetime, timedelta, timezone

from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionDetailResponse,
    SessionListItem,
    SessionsSummary,
    PeriodStats,
    ProgressDataPoint,
    ProgressResponse,
    MoodCorrelationResponse
)
from app.core.redis_client import cache, invalidate_user_stats
from app.core.config import settings


class SessionService:
    def __init__(
        self,
        session_repo: SessionRepository,
        user_repo: UserRepository
    ):
        self.session_repo = session_repo
        self.user_repo = user_repo


    # create session
    async def create_session(
        self,
        user_id: UUID,
        session_data: SessionCreate
    ) -> SessionDetailResponse:
        # Cria sessão
        session = await self.session_repo.create_session(
            user_id=user_id,
            **session_data.model_dump()
        )

        # Atualiza stats do usuário
        await self.user_repo.update_stats(
            user_id=user_id,
            retention_time=session_data.retention_time,
            session_date=session.session_date
        )

        # Invalida cache
        await invalidate_user_stats(str(user_id))

        # Verifica se é personal best
        user = await self.user_repo.get_by_id(user_id)
        is_personal_best = (
            session.retention_time == user.best_retention_time
            if user else False
        )

        return SessionDetailResponse(
            **session.__dict__,
            is_personal_best=is_personal_best
        )


    # get session
    async def get_session(
        self,
        user_id: UUID,
        session_id: UUID
    ) -> SessionDetailResponse | None:
        session = await self.session_repo.get_user_session(user_id, session_id)
        if not session:
            return None

        user = await self.user_repo.get_by_id(user_id)
        is_personal_best = (
            session.retention_time == user.best_retention_time
            if user else False
        )

        return SessionDetailResponse(
            **session.__dict__,
            is_personal_best=is_personal_best
        )


    # list sessions
    async def list_user_sessions(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "session_date",
        order_dir: str = "desc"
    ) -> tuple[list[SessionListItem], int]:
        sessions = await self.session_repo.get_user_sessions(
            user_id=user_id,
            skip=skip,
            limit=limit,
            order_by=order_by,
            order_dir=order_dir
        )

        total = await self.session_repo.count_user_sessions(user_id)

        user = await self.user_repo.get_by_id(user_id)
        best_retention = user.best_retention_time if user else 0

        items = [
            SessionListItem(
                id=s.id,
                breaths_count=s.breaths_count,
                retention_time=s.retention_time,
                session_date=s.session_date,
                technique_variant=s.technique_variant,
                mood_improvement=s.mood_improvement,
                is_personal_best=(s.retention_time == best_retention)
            )
            for s in sessions
        ]

        return items, total


    # update session
    async def update_session(
        self,
        user_id: UUID,
        session_id: UUID,
        session_update: SessionUpdate
    ) -> SessionResponse | None:
        session = await self.session_repo.get_user_session(user_id, session_id)
        if not session:
            return None

        update_data = session_update.model_dump(exclude_unset=True)
        if not update_data:
            return SessionResponse.model_validate(session)

        updated = await self.session_repo.update_by_id(
            session_id,
            **update_data
        )

        return SessionResponse.model_validate(updated)


    # delete session
    async def delete_session(
        self,
        user_id: UUID,
        session_id: UUID
    ) -> bool:
        success = await self.session_repo.delete_user_session(
            user_id,
            session_id
        )

        if success:
            await invalidate_user_stats(str(user_id))

        return success


    # statistics
    async def get_sessions_summary(
        self,
        user_id: UUID,
        use_cache: bool = True
    ) -> SessionsSummary:
        # Tenta cache
        if use_cache:
            cache_key = f"stats:{user_id}:summary"
            cached = await cache.get_json(cache_key)
            if cached:
                return SessionsSummary.model_validate(cached)

        # Busca dados
        total_stats = await self.session_repo.get_user_total_stats(user_id)
        last_7_days = await self.session_repo.get_user_stats_by_period(
            user_id, 7
        )
        last_30_days = await self.session_repo.get_user_stats_by_period(
            user_id, 30
        )

        user = await self.user_repo.get_by_id(user_id)

        summary = SessionsSummary(
            total_sessions=total_stats["total_sessions"],
            total_retention_time=total_stats["total_retention_time"],
            average_retention_time=total_stats["average_retention_time"],
            best_retention_time=total_stats["best_retention_time"],
            current_streak=user.current_streak if user else 0,
            longest_streak=user.longest_streak if user else 0,
            total_breaths=total_stats["total_breaths"],
            last_7_days=PeriodStats(**last_7_days),
            last_30_days=PeriodStats(**last_30_days)
        )

        # Salva no cache
        if use_cache:
            cache_key = f"stats:{user_id}:summary"
            await cache.set_json(
                cache_key,
                summary.model_dump(mode='json'),
                ttl=settings.cache_ttl_stats
            )

        return summary


    # progress tracking
    async def get_progress(
        self,
        user_id: UUID,
        days: int = 30
    ) -> ProgressResponse:
        daily_data = await self.session_repo.get_daily_progress(
            user_id,
            days
        )

        data_points = [
            ProgressDataPoint(**day)
            for day in daily_data
        ]

        # Calcula tendência simples
        if len(data_points) >= 2:
            first_avg = data_points[0].average_retention_time
            last_avg = data_points[-1].average_retention_time

            if last_avg > first_avg * 1.1:
                trend = "improving"
            elif last_avg < first_avg * 0.9:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return ProgressResponse(
            data_points=data_points,
            period_days=days,
            trend=trend
        )


    # mood analysis
    async def get_mood_correlation(
        self,
        user_id: UUID
    ) -> MoodCorrelationResponse:
        mood_data = await self.session_repo.get_mood_correlation(user_id)

        correlation = 0.0  # Placeholder

        return MoodCorrelationResponse(
            average_mood_before=mood_data["average_mood_before"],
            average_mood_after=mood_data["average_mood_after"],
            average_improvement=mood_data["average_improvement"],
            correlation_retention_improvement=correlation,
            sessions_with_mood=mood_data["sessions_with_mood"]
        )


    # filters
    async def get_sessions_by_date_range(
        self,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> list[SessionResponse]:
        sessions = await self.session_repo.get_sessions_by_date_range(
            user_id,
            start_date,
            end_date
        )

        return [SessionResponse.model_validate(s) for s in sessions]

    async def get_sessions_by_technique(
        self,
        user_id: UUID,
        technique_variant: str
    ) -> list[SessionResponse]:
        sessions = await self.session_repo.get_sessions_by_technique(
            user_id,
            technique_variant
        )

        return [SessionResponse.model_validate(s) for s in sessions]


    # personal bests
    async def get_personal_best(
        self,
        user_id: UUID
    ) -> SessionDetailResponse | None:
        session = await self.session_repo.get_personal_best(user_id)
        if not session:
            return None

        return SessionDetailResponse(
            **session.__dict__,
            is_personal_best=True
        )

    async def get_recent_personal_bests(
        self,
        user_id: UUID,
        days: int = 30
    ) -> list[SessionDetailResponse]:
        sessions = await self.session_repo.get_recent_personal_bests(
            user_id,
            days
        )

        return [
            SessionDetailResponse(
                **s.__dict__,
                is_personal_best=True
            )
            for s in sessions
        ]


    # weekly progress
    async def get_weekly_progress(
        self,
        user_id: UUID,
        weeks: int = 12
    ) -> list[dict]:
        return await self.session_repo.get_weekly_progress(user_id, weeks)