from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, sessions, achievements

# Router principal da v1
api_router = APIRouter(prefix="/v1")

# Inclui todos os sub-routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(sessions.router)
api_router.include_router(achievements.router)