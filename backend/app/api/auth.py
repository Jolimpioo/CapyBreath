from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import AuthService
from app.api.dependencies import AuthServiceDep

# Security scheme para documentação automática do Swagger
security = HTTPBearer(
    scheme_name="JWT Bearer Token",
    description="Insira o token JWT no formato: Bearer <token>"
)


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: AuthServiceDep
) -> UUID:
    token = credentials.credentials
    
    try:
        user_id = await auth_service.verify_access_token(token)
        return user_id
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )


# Type alias para facilitar uso nos endpoints
CurrentUserDep = Annotated[UUID, Depends(get_current_user_id)]