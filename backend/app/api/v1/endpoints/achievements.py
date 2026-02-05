from fastapi import APIRouter, HTTPException, status, Query
from uuid import UUID

from app.schemas.achievement import (
    AchievementResponse,
    UserAchievementsResponse,
    AchievementDetail,
    AchievementCreate,
    AchievementUpdate
)
from app.schemas.common import MessageResponse
from app.models.achievement import AchievementCategory, AchievementRarity
from app.api.dependencies import AchievementServiceDep
from app.api.auth import CurrentUserDep

router = APIRouter(prefix="/achievements", tags=["Achievements"])


# public routes (sem autenticação)
@router.get(
    "",
    response_model=list[AchievementResponse],
    summary="Listar todas as conquistas"
)
async def list_all_achievements(
    achievement_service: AchievementServiceDep,
    include_hidden: bool = Query(False, description="Incluir conquistas ocultas")
):
    return await achievement_service.list_all_achievements(
        include_hidden=include_hidden
    )


@router.get(
    "/category/{category}",
    response_model=list[AchievementResponse],
    summary="Listar conquistas por categoria"
)
async def list_by_category(
    category: AchievementCategory,
    achievement_service: AchievementServiceDep
):
    return await achievement_service.list_by_category(category)


@router.get(
    "/rarity/{rarity}",
    response_model=list[AchievementResponse],
    summary="Listar conquistas por raridade"
)
async def list_by_rarity(
    rarity: AchievementRarity,
    achievement_service: AchievementServiceDep
):
    return await achievement_service.list_by_rarity(rarity)


@router.get(
    "/stats",
    response_model=dict,
    summary="Estatísticas gerais do sistema de conquistas"
)
async def get_achievement_stats(
    achievement_service: AchievementServiceDep
):
    return await achievement_service.get_achievement_stats()


# user achievements (requer autenticação)
@router.get(
    "/me",
    response_model=UserAchievementsResponse,
    summary="Minhas conquistas"
)
async def get_my_achievements(
    user_id: CurrentUserDep,
    achievement_service: AchievementServiceDep,
    use_cache: bool = Query(True, description="Usar cache")
):
    return await achievement_service.get_user_achievements(
        user_id,
        use_cache=use_cache
    )


@router.get(
    "/me/{achievement_id}",
    response_model=AchievementDetail,
    summary="Detalhes de uma conquista específica"
)
async def get_achievement_detail(
    achievement_id: UUID,
    user_id: CurrentUserDep,
    achievement_service: AchievementServiceDep
):
    detail = await achievement_service.get_achievement_detail(
        user_id,
        achievement_id
    )
    
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conquista não encontrada"
        )
    
    return detail


@router.post(
    "/check",
    response_model=dict,
    summary="Verificar e desbloquear conquistas"
)
async def check_achievements(
    user_id: CurrentUserDep,
    achievement_service: AchievementServiceDep
):
    newly_unlocked = await achievement_service.check_and_unlock_achievements(
        user_id
    )
    
    return {
        "newly_unlocked": [a.model_dump() for a in newly_unlocked],
        "count": len(newly_unlocked),
        "message": f"{len(newly_unlocked)} conquista(s) desbloqueada(s)!"
    }


# admin routes (futuro - adicionar proteção de role)
@router.post(
    "/admin/create",
    response_model=AchievementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[ADMIN] Criar conquista",
    include_in_schema=False  # Ocultar do Swagger por enquanto
)
async def create_achievement(
    achievement_data: AchievementCreate,
    user_id: CurrentUserDep,  # TODO: Verificar se é admin
    achievement_service: AchievementServiceDep
):
    """
    **[ADMIN ONLY]** Cria uma nova conquista no sistema.
    
    **TODO:** Adicionar verificação de role admin.
    
    **Requer autenticação.**
    """
    try:
        return await achievement_service.create_achievement(achievement_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/admin/{achievement_id}",
    response_model=AchievementResponse,
    summary="[ADMIN] Atualizar conquista",
    include_in_schema=False
)
async def update_achievement(
    achievement_id: UUID,
    achievement_update: AchievementUpdate,
    user_id: CurrentUserDep,  # TODO: Verificar se é admin
    achievement_service: AchievementServiceDep
):
    """
    **[ADMIN ONLY]** Atualiza uma conquista existente.
    
    **TODO:** Adicionar verificação de role admin.
    
    **Requer autenticação.**
    """
    updated = await achievement_service.update_achievement(
        achievement_id,
        achievement_update
    )
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conquista não encontrada"
        )
    
    return updated


@router.post(
    "/admin/{achievement_id}/deactivate",
    response_model=MessageResponse,
    summary="[ADMIN] Desativar conquista",
    include_in_schema=False
)
async def deactivate_achievement(
    achievement_id: UUID,
    user_id: CurrentUserDep,  # TODO: Verificar se é admin
    achievement_service: AchievementServiceDep
):
    """
    **[ADMIN ONLY]** Desativa uma conquista.
    
    **Ação:**
    - Conquista não aparece mais para usuários
    - Usuários que já têm mantêm a conquista
    
    **TODO:** Adicionar verificação de role admin.
    
    **Requer autenticação.**
    """
    success = await achievement_service.deactivate_achievement(achievement_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conquista não encontrada"
        )
    
    return MessageResponse(
        message="Conquista desativada com sucesso"
    )