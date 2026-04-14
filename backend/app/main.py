from contextlib import asynccontextmanager
import logging
import time
import uuid
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis_client import init_redis, close_redis
from app.core.logging import configure_logging
from app.api.v1.router import api_router

configure_logging(settings.log_level)
logger = logging.getLogger("app.main")

# lifecicle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia ciclo de vida da aplicação
    - Startup: Conecta ao banco e Redis
    - Shutdown: Fecha conexões
    """
    # Startup
    logger.info(
        "startup_begin",
        extra={"event_data": {"event": "app_startup_begin"}}
    )
    
    # Conecta ao banco de dados
    await init_db()
    logger.info(
        "postgres_connected",
        extra={"event_data": {"event": "postgres_connected"}}
    )
    
    # Conecta ao Redis
    await init_redis()
    logger.info(
        "redis_connected",
        extra={"event_data": {"event": "redis_connected"}}
    )
    
    logger.info(
        "startup_complete",
        extra={"event_data": {
            "event": "app_startup_complete",
            "app": settings.app_name,
            "version": settings.app_version
        }}
    )
    
    yield
    
    # Shutdown
    logger.info(
        "shutdown_begin",
        extra={"event_data": {"event": "app_shutdown_begin"}}
    )
    await close_redis()
    await close_db()
    logger.info(
        "shutdown_complete",
        extra={"event_data": {"event": "app_shutdown_complete"}}
    )


# app instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    🦫 **CapyBreath API** - Backend para aplicação de respiração Wim Hof
    
    ## Funcionalidades
    
    * **Autenticação JWT** - Registro, login, refresh token
    * **Sessões de Respiração** - CRUD completo com estatísticas
    * **Sistema de Conquistas** - Desbloqueio automático baseado em progresso
    * **Leaderboards** - Rankings por retenção, streak e atividade
    * **Análise de Progresso** - Gráficos e tendências
    * **Análise de Humor** - Correlação entre respiração e bem-estar
    
    ## Tecnologias
    
    * FastAPI + PostgreSQL (async)
    * Redis (cache e tokens)
    * JWT Authentication
    * SQLAlchemy 2.0 (async)
    * Pydantic v2
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug
)


# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # ["http://localhost:5173", ...]
    allow_credentials=True,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=settings.cors_expose_headers
)


# routers
# Inclui router da API v1
app.include_router(
    api_router,
    prefix="/api"
)

@app.middleware("http")
async def structured_request_logging(request, call_next):
    started_at = time.perf_counter()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.request_started_at = started_at

    response = await call_next(request)

    latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "http_request",
        extra={"event_data": {
            "event": "http_request",
            "request_id": request_id,
            "user_id": None,
            "ip": request.client.host if request.client else None,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": latency_ms
        }}
    )
    return response


# root endpoints
@app.get(
    "/",
    tags=["Root"],
    summary="Endpoint raiz"
)
async def root():
    """
    Endpoint raiz da API.
    Retorna informações básicas da aplicação.
    """
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
        "api": "/api/v1"
    }


@app.get(
    "/health",
    tags=["Root"],
    summary="Health check"
)
async def health_check():
    """
    Verifica se a API está respondendo.
    Útil para monitoring e load balancers.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


# exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handler customizado para 404"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": "Endpoint não encontrado",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handler customizado para 500"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erro interno do servidor",
            "message": "Entre em contato com o suporte"
        }
    )


# startup message
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
