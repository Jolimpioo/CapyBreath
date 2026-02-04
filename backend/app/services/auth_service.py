from uuid import UUID
from datetime import timedelta
from jose import JWTError

from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.schemas.user import UserLoginResponse
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
    create_token_pair
)
from app.core.redis_client import (
    store_refresh_token,
    get_refresh_token,
    revoke_refresh_token
)
from app.core.config import settings


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo


    # register
    async def register_user(
        self,
        user_data: UserRegister
    ) -> tuple[UserLoginResponse, TokenResponse]:
        # Verifica se já existe
        existing = await self.user_repo.get_by_email_or_username(
            user_data.email,
            user_data.username
        )
        
        if existing:
            if existing.email.lower() == user_data.email.lower():
                raise ValueError("Email já cadastrado")
            if existing.username.lower() == user_data.username.lower():
                raise ValueError("Username já cadastrado")

        # Hash da senha
        password_hash = get_password_hash(user_data.password)

        # Cria usuário
        user = await self.user_repo.create(
            email=user_data.email.lower(),
            username=user_data.username.lower(),
            password_hash=password_hash,
            full_name=user_data.full_name,
            is_active=True,
            is_verified=False  # Pode implementar verificação de email depois
        )

        # Gera tokens
        tokens = create_token_pair(str(user.id))

        # Armazena refresh token no Redis
        await store_refresh_token(
            str(user.id),
            tokens["refresh_token"]
        )

        # Response
        user_response = UserLoginResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url
        )

        token_response = TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )

        return user_response, token_response


    # login
    async def login_user(
        self,
        login_data: UserLogin
    ) -> tuple[UserLoginResponse, TokenResponse]:
        # Busca usuário
        user = await self.user_repo.get_by_email(login_data.email)

        if not user:
            raise ValueError("Email ou senha incorretos")

        # Verifica senha
        if not verify_password(login_data.password, user.password_hash):
            raise ValueError("Email ou senha incorretos")

        # Verifica se está ativo
        if not user.is_active:
            raise ValueError("Conta desativada")

        # Verifica soft delete
        if user.is_deleted:
            raise ValueError("Conta não encontrada")

        # Gera tokens
        tokens = create_token_pair(str(user.id))

        # Armazena refresh token (substitui o antigo se existir)
        await store_refresh_token(
            str(user.id),
            tokens["refresh_token"]
        )

        # Response
        user_response = UserLoginResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url
        )

        token_response = TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )

        return user_response, token_response


    # refresh token
    async def refresh_access_token(
        self,
        refresh_token: str
    ) -> str:
        try:
            # Decodifica token
            payload = decode_token(refresh_token)

            # Verifica se é refresh token
            if not verify_token_type(payload, "refresh"):
                raise ValueError("Token type inválido")

            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Token inválido")

            # Verifica se refresh token está armazenado no Redis
            stored_token = await get_refresh_token(user_id)
            if not stored_token or stored_token != refresh_token:
                raise ValueError("Refresh token inválido ou revogado")

            # Verifica se usuário ainda existe e está ativo
            user = await self.user_repo.get_active_by_id(UUID(user_id))
            if not user:
                raise ValueError("Usuário inválido ou inativo")

            # Gera novo access token
            new_access_token = create_access_token(subject=user_id)

            return new_access_token

        except JWTError as e:
            raise ValueError(f"Token inválido: {str(e)}")


    # logout
    async def logout_user(self, user_id: UUID) -> bool:
        return await revoke_refresh_token(str(user_id))


    # verify token
    async def verify_access_token(
        self,
        access_token: str
    ) -> UUID:
        try:
            payload = decode_token(access_token)

            if not verify_token_type(payload, "access"):
                raise ValueError("Token type inválido")

            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Token inválido")

            # Verifica se usuário existe e está ativo
            user = await self.user_repo.get_active_by_id(UUID(user_id))
            if not user:
                raise ValueError("Usuário inválido ou inativo")

            return UUID(user_id)

        except JWTError as e:
            raise ValueError(f"Token inválido: {str(e)}")


    # get current user
    async def get_current_user(
        self,
        user_id: UUID
    ) -> UserLoginResponse | None:
        user = await self.user_repo.get_active_by_id(user_id)
        if not user:
            return None

        return UserLoginResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url
        )


    # password reset (futuro)
    async def request_password_reset(self, email: str) -> bool:
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Retorna True mesmo se não existe (segurança)
            return True

        return True

    async def reset_password(
        self,
        reset_token: str,
        new_password: str
    ) -> bool:
        
        return False