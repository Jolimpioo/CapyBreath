"""
API Dependencies - Dependency Injection Helpers

Este módulo fornece funções de dependência para FastAPI que:
1. Criam instâncias de Repositories a partir da sessão do banco
2. Criam instâncias de Services com seus Repositories injetados
3. Facilitam o uso nos endpoints via Depends()

Localização: app/api/dependencies.py
Usado por: Endpoints em app/api/v1/endpoints/

Exemplo de uso:
    from app.api.dependencies import SessionServiceDep
    
    @router.post("/sessions")
    async def create_session(
        session_service: SessionServiceDep  # Injetado automaticamente
    ):
        return await session_service.create_session(...)
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories import (
    UserRepository,
    SessionRepository,
    AchievementRepository,
    UserAchievementRepository
)
from app.services import (
    AuthService,
    UserService,
    SessionService,
    AchievementService
)


# Repositories
def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRepository:
    return UserRepository(db)

def get_session_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> SessionRepository:
    return SessionRepository(db)

def get_achievement_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AchievementRepository:
    return AchievementRepository(db)

def get_user_achievement_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserAchievementRepository:
    return UserAchievementRepository(db)


# Services
def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> AuthService:
    return AuthService(user_repo)

def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    session_repo: Annotated[SessionRepository, Depends(get_session_repository)],
    user_achievement_repo: Annotated[
        UserAchievementRepository,
        Depends(get_user_achievement_repository)
    ]
) -> UserService:
    return UserService(user_repo, session_repo, user_achievement_repo)

def get_session_service(
    session_repo: Annotated[SessionRepository, Depends(get_session_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> SessionService:
    return SessionService(session_repo, user_repo)

def get_achievement_service(
    achievement_repo: Annotated[
        AchievementRepository,
        Depends(get_achievement_repository)
    ],
    user_achievement_repo: Annotated[
        UserAchievementRepository,
        Depends(get_user_achievement_repository)
    ],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> AchievementService:
    return AchievementService(
        achievement_repo,
        user_achievement_repo,
        user_repo
    )


# Type aliases para facilitar uso nos endpoints
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]
AchievementServiceDep = Annotated[AchievementService, Depends(get_achievement_service)]