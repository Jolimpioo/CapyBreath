from fastapi import APIRouter, HTTPException, status, Query

from app.schemas.user import (
    UserUpdate,
    UserResponse,
    UserStatsResponse,
    UserProfile
)
from app.schemas.common import MessageResponse
from app.api.dependencies import UserServiceDep
from app.api.auth import CurrentUserDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obter meu perfil"
)
async def get_my_profile(
    user_id: CurrentUserDep,
    user_service: UserServiceDep
):
    user = await user_service.get_active_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Atualizar meu perfil"
)
async def update_my_profile(
    user_update: UserUpdate,
    user_id: CurrentUserDep,
    user_service: UserServiceDep
):
    updated_user = await user_service.update_user(user_id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return updated_user


@router.get(
    "/me/stats",
    response_model=UserStatsResponse,
    summary="Obter minhas estatísticas"
)
async def get_my_stats(
    user_id: CurrentUserDep,
    user_service: UserServiceDep,
    use_cache: bool = Query(True, description="Usar cache do Redis")
):
    stats = await user_service.get_user_stats(user_id, use_cache=use_cache)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return stats


@router.get(
    "/me/profile",
    response_model=UserProfile,
    summary="Obter meu perfil completo"
)
async def get_my_full_profile(
    user_id: CurrentUserDep,
    user_service: UserServiceDep
):
    profile = await user_service.get_user_profile(user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return profile


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Deletar minha conta"
)
async def delete_my_account(
    user_id: CurrentUserDep,
    user_service: UserServiceDep
):
    success = await user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return MessageResponse(
        message="Conta deletada com sucesso"
    )


# leaderboards (nao requer autenticacao)
@router.get(
    "/leaderboard/retention",
    response_model=list[UserStatsResponse],
    summary="Top usuários por tempo de retenção"
)
async def leaderboard_by_retention(
    user_service: UserServiceDep,
    limit: int = Query(10, ge=1, le=100, description="Número de usuários")
):
    return await user_service.get_top_by_retention(limit)


@router.get(
    "/leaderboard/streak",
    response_model=list[UserStatsResponse],
    summary="Top usuários por sequência (streak)"
)
async def leaderboard_by_streak(
    user_service: UserServiceDep,
    limit: int = Query(10, ge=1, le=100, description="Número de usuários")
):
    return await user_service.get_top_by_streak(limit)


@router.get(
    "/leaderboard/active",
    response_model=list[UserStatsResponse],
    summary="Usuários mais ativos"
)
async def leaderboard_most_active(
    user_service: UserServiceDep,
    limit: int = Query(10, ge=1, le=100, description="Número de usuários")
):
    return await user_service.get_most_active(limit)


# search
@router.get(
    "/search",
    response_model=list[UserResponse],
    summary="Buscar usuários por username"
)
async def search_users(
    user_service: UserServiceDep,
    q: str = Query(..., min_length=2, description="Termo de busca"),
    limit: int = Query(10, ge=1, le=50)
):
    return await user_service.search_users(q, limit)