from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    AccessTokenResponse
)
from app.schemas.user import UserLoginResponse
from app.schemas.common import MessageResponse
from app.api.dependencies import AuthServiceDep
from app.api.auth import CurrentUserDep

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário"
)
async def register(
    user_data: UserRegister,
    auth_service: AuthServiceDep
):
    try:
        user, tokens = await auth_service.register_user(user_data)
        
        return {
            "user": user.model_dump(),
            "tokens": tokens.model_dump()
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=dict,
    summary="Fazer login"
)
async def login(
    login_data: UserLogin,
    auth_service: AuthServiceDep
):
    try:
        user, tokens = await auth_service.login_user(login_data)
        
        return {
            "user": user.model_dump(),
            "tokens": tokens.model_dump()
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Renovar access token"
)
async def refresh_token(
    token_data: TokenRefresh,
    auth_service: AuthServiceDep
):
    try:
        new_access_token = await auth_service.refresh_access_token(
            token_data.refresh_token
        )
        
        return AccessTokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=30 * 60  # 30 minutos em segundos
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Fazer logout"
)
async def logout(
    user_id: CurrentUserDep,
    auth_service: AuthServiceDep
):
    await auth_service.logout_user(user_id)
    
    return MessageResponse(
        message="Logout realizado com sucesso"
    )


@router.get(
    "/me",
    response_model=UserLoginResponse,
    summary="Obter usuário atual"
)
async def get_current_user(
    user_id: CurrentUserDep,
    auth_service: AuthServiceDep
):
    user = await auth_service.get_current_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user