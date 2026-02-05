from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query
from uuid import UUID

from app.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionDetailResponse,
    SessionListItem,
    SessionsSummary,
    ProgressResponse,
    MoodCorrelationResponse
)
from app.schemas.common import MessageResponse, PaginatedResponse
from app.api.dependencies import SessionServiceDep, AchievementServiceDep
from app.api.auth import CurrentUserDep

router = APIRouter(prefix="/sessions", tags=["Sessions"])


# crud operations
@router.post(
    "",
    response_model=SessionDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova sessão"
)
async def create_session(
    session_data: SessionCreate,
    user_id: CurrentUserDep,
    session_service: SessionServiceDep,
    achievement_service: AchievementServiceDep
):
    # Cria sessão
    session = await session_service.create_session(user_id, session_data)
    
    # Verifica conquistas desbloqueadas
    newly_unlocked = await achievement_service.check_and_unlock_achievements(
        user_id
    )
    
    # TODO: Retornar conquistas desbloqueadas em header ou campo extra
    # Por enquanto, apenas logamos
    if newly_unlocked:
        print(f"🏆 {len(newly_unlocked)} conquistas desbloqueadas!")
    
    return session


@router.get(
    "",
    response_model=PaginatedResponse[SessionListItem],
    summary="Listar minhas sessões"
)
async def list_my_sessions(
    user_id: CurrentUserDep,
    session_service: SessionServiceDep,
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    order_by: str = Query("session_date", description="Campo para ordenar"),
    order_dir: str = Query("desc", regex="^(asc|desc)$")
):
    skip = (page - 1) * size
    
    items, total = await session_service.list_user_sessions(
        user_id=user_id,
        skip=skip,
        limit=size,
        order_by=order_by,
        order_dir=order_dir
    )
    
    total_pages = (total + size - 1) // size  # Ceiling division
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=total_pages
    )


@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse,
    summary="Obter detalhes de uma sessão"
)
async def get_session(
    session_id: UUID,
    user_id: CurrentUserDep,
    session_service: SessionServiceDep
):
    session = await session_service.get_session(user_id, session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    return session


@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Atualizar sessão"
)
async def update_session(
    session_id: UUID,
    session_update: SessionUpdate,
    user_id: CurrentUserDep,
    session_service: SessionServiceDep
):
    updated = await session_service.update_session(
        user_id,
        session_id,
        session_update
    )
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    return updated


@router.delete(
    "/{session_id}",
    response_model=MessageResponse,
    summary="Deletar sessão"
)
async def delete_session(
    session_id: UUID,
    user_id: CurrentUserDep,
    session_service: SessionServiceDep
):
    success = await session_service.delete_session(user_id, session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    return MessageResponse(
        message="Sessão deletada com sucesso"
    )


# statistics
@router.get(
    "/stats/summary",
    response_model=SessionsSummary,
    summary="Resumo estatístico completo"
)
async def get_sessions_summary(
    user_id: CurrentUserDep,
    session_service: SessionServiceDep,
    use_cache: bool = Query(True, description="Usar cache")
):
    return await session_service.get_sessions_summary(user_id, use_cache)


@router.get(
    "/stats/progress",
    response_model=ProgressResponse,
    summary="Progresso ao longo do tempo"
)
async def get_progress(
    user_id: CurrentUserDep,
    session_service: SessionServiceDep,
    days: int = Query(30, ge=7, le=365, description="Período em dias")
):
    return await session_service.get_progress(user_id, days)


@router.get(
    "/stats/mood",
    response_model=MoodCorrelationResponse,
    summary="Análise de humor"
)
async def get_mood_correlation(
    user_id: CurrentUserDep,
    session_service: SessionServiceDep
):
    return await session_service.get_mood_correlation(user_id)


# filters
@router.get(
    "/filter/by-date",
    response_model=list[SessionResponse],
    summary="Filtrar sessões por período"
)
async def filter_by_date_range(
    user_id: CurrentUserDep,
    session_service: SessionServiceDep,
    start_date: datetime = Query(..., description="Data inicial (ISO 8601)"),
    end_date: datetime = Query(..., description="Data final (ISO 8601)")
):
    return await session_service.get_sessions_by_date_range(
        user_id,
        start_date,
        end_date
    )


@router.get(
    "/filter/by-technique/{technique_variant}",
    response_model=list[SessionResponse],
    summary="Filtrar por técnica"
)
async def filter_by_technique(
    technique_variant: str,
    user_id: CurrentUserDep,
    session_service: SessionServiceDep
):
    return await session_service.get_sessions_by_technique(
        user_id,
        technique_variant
    )


# personal bests
@router.get(
    "/personal-best",
    response_model=SessionDetailResponse,
    summary="Melhor sessão (personal best)"
)
async def get_personal_best(
    user_id: CurrentUserDep,
    session_service: SessionServiceDep
):
    best = await session_service.get_personal_best(user_id)
    
    if not best:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma sessão encontrada"
        )
    
    return best


@router.get(
    "/personal-bests/recent",
    response_model=list[SessionDetailResponse],
    summary="Personal bests recentes"
)
async def get_recent_personal_bests(
    user_id: CurrentUserDep,
    session_service: SessionServiceDep,
    days: int = Query(30, ge=1, le=365)
):
    return await session_service.get_recent_personal_bests(user_id, days)