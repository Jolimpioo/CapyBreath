from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis_client import init_redis, close_redis
from app.api.v1.router import api_router


# lifecicle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia ciclo de vida da aplicação
    - Startup: Conecta ao banco e Redis
    - Shutdown: Fecha conexões
    """
    # Startup
    print("🚀 Iniciando CapyBreath API...")
    
    # Conecta ao banco de dados
    await init_db()
    print("✅ Conectado ao PostgreSQL")
    
    # Conecta ao Redis
    await init_redis()
    print("✅ Conectado ao Redis")
    
    print(f"🦫 {settings.app_name} v{settings.app_version} está rodando!")
    print(f"📚 Documentação: http://{settings.host}:{settings.port}/docs")
    
    yield
    
    # Shutdown
    print("🛑 Encerrando CapyBreath API...")
    await close_redis()
    await close_db()
    print("👋 Até logo!")


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
    allow_methods=["*"],  # GET, POST, PUT, DELETE, PATCH, OPTIONS
    allow_headers=["*"],  # Authorization, Content-Type, etc.
    expose_headers=["*"]
)


# routers
# Inclui router da API v1
app.include_router(
    api_router,
    prefix="/api"
)


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