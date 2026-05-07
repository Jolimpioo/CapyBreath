from fastapi import APIRouter, HTTPException, Request, Response, status

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    AuthSuccessResponse,
    TokenRefresh,
    AccessTokenResponse
)
from app.schemas.user import UserLoginResponse
from app.schemas.common import MessageResponse
from app.api.dependencies import AuthServiceDep
from app.api.auth import CurrentUserDep
from app.core.audit import log_security_event
from app.core.logging import mask_sensitive
from app.core.metrics import security_metrics
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
GENERIC_REGISTER_ERROR_MESSAGE = (
    "Não foi possível concluir o cadastro com os dados informados"
)
GENERIC_LOGIN_ERROR_MESSAGE = "Email ou senha inválidos"
REFRESH_COOKIE_NAME = "refresh_token"


def _raise_generic_auth_error(status_code: int, detail: str) -> None:
    raise HTTPException(status_code=status_code, detail=detail)


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.secure_cookies_enabled,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/api/v1/auth",
    )


@router.post(
    "/register",
    response_model=AuthSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário"
)
async def register(
    user_data: UserRegister,
    request: Request,
    response: Response,
    auth_service: AuthServiceDep
):
    try:
        user, tokens = await auth_service.register_user(user_data)

        auth_mode = "bearer"
        if settings.auth_dual_mode_enabled:
            _set_refresh_cookie(response, tokens.refresh_token)
            auth_mode = "dual"

        log_security_event(
            event="auth_register_success",
            request=request,
            status_code=status.HTTP_201_CREATED,
            user_id=str(user.id),
            extra={
                "email": mask_sensitive(user_data.email),
                "auth_mode": auth_mode,
            }
        )
        
        return {
            "user": user.model_dump(),
            "tokens": tokens.model_dump()
        }
    
    except ValueError as e:
        log_security_event(
            event="auth_register_failed",
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
            extra={
                "email": mask_sensitive(user_data.email),
                "failure_reason": str(e)
            }
        )
        _raise_generic_auth_error(
            status.HTTP_400_BAD_REQUEST,
            GENERIC_REGISTER_ERROR_MESSAGE
        )


@router.post(
    "/login",
    response_model=AuthSuccessResponse,
    summary="Fazer login"
)
async def login(
    login_data: UserLogin,
    request: Request,
    response: Response,
    auth_service: AuthServiceDep
):
    try:
        user, tokens = await auth_service.login_user(login_data)

        auth_mode = "bearer"
        if settings.auth_dual_mode_enabled:
            _set_refresh_cookie(response, tokens.refresh_token)
            auth_mode = "dual"

        security_metrics.increment_auth("login", "success")
        log_security_event(
            event="auth_login_success",
            request=request,
            status_code=status.HTTP_200_OK,
            user_id=str(user.id),
            extra={
                "email": mask_sensitive(login_data.email),
                "auth_mode": auth_mode,
            }
        )
        
        return {
            "user": user.model_dump(),
            "tokens": tokens.model_dump()
        }
    
    except ValueError as e:
        security_metrics.increment_auth("login", "failed")
        log_security_event(
            event="auth_login_failed",
            request=request,
            status_code=status.HTTP_401_UNAUTHORIZED,
            extra={
                "email": mask_sensitive(login_data.email),
                "failure_reason": str(e)
            }
        )
        _raise_generic_auth_error(
            status.HTTP_401_UNAUTHORIZED,
            GENERIC_LOGIN_ERROR_MESSAGE
        )


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Renovar access token"
)
async def refresh_token(
    request: Request,
    auth_service: AuthServiceDep,
    token_data: TokenRefresh | None = None
):
    try:
        cookie_refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
        body_refresh_token = token_data.refresh_token if token_data else None

        refresh_token_value = body_refresh_token
        auth_mode = "bearer"

        if settings.auth_dual_mode_enabled and cookie_refresh_token:
            refresh_token_value = cookie_refresh_token
            auth_mode = "cookie"

        if not refresh_token_value:
            raise ValueError("Refresh token ausente")

        new_access_token = await auth_service.refresh_access_token(
            refresh_token_value
        )
        security_metrics.increment_auth("refresh", "success")
        log_security_event(
            event="auth_refresh_success",
            request=request,
            status_code=status.HTTP_200_OK,
            extra={"auth_mode": auth_mode}
        )
        
        return AccessTokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=30 * 60  # 30 minutos em segundos
        )
    
    except ValueError as e:
        security_metrics.increment_auth("refresh", "failed")
        log_security_event(
            event="auth_refresh_failed",
            request=request,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
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
    request: Request,
    response: Response,
    user_id: CurrentUserDep,
    auth_service: AuthServiceDep
):
    await auth_service.logout_user(user_id)
    if settings.auth_dual_mode_enabled:
        _clear_refresh_cookie(response)
    log_security_event(
        event="auth_logout_success",
        request=request,
        status_code=status.HTTP_200_OK,
        user_id=str(user_id),
        extra={"auth_mode": "dual" if settings.auth_dual_mode_enabled else "bearer"}
    )
    
    return MessageResponse(
        message="Logout realizado com sucesso"
    )


@router.get(
    "/me",
    response_model=UserLoginResponse,
    summary="Obter usuário atual (legado)",
    deprecated=True
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
