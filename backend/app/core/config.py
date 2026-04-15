from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    #app
    app_name: str = "CapyBreath API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    #security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    secure_cookies_enabled: bool = False
    auth_dual_mode_enabled: bool = False
    csp_report_only_enabled: bool = True
    strict_cors_enabled: bool = False

    #cors
    cors_origins: str

    #postgresql
    postgres_user: str = "capybreath"
    postgres_password: str 
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "capybreath_db"

    # redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str
    redis_db: int = 0
    redis_decode_responses: bool = True

    # cache
    cache_ttl_stats: int = 300
    cache_ttl_user: int = 600

    # pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # rate limiting
    rate_limit_per_minute: int = 60

    # logging
    log_level: str = "INFO"


    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def validate_cors_credentials_policy(self) -> None:
        """
        Com allow_credentials=True, wildcard de origem não é permitido.
        """
        if any(origin == "*" for origin in self.cors_origins_list):
            raise ValueError(
                "CORS inválido: com credenciais habilitadas, "
                "não use '*' em CORS_ORIGINS."
            )

    @property
    def cors_allow_methods(self) -> list[str]:
        if self.strict_cors_enabled:
            return ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        return ["*"]

    @property
    def cors_allow_headers(self) -> list[str]:
        if self.strict_cors_enabled:
            return ["Authorization", "Content-Type", "X-Request-ID"]
        return ["*"]

    @property
    def cors_expose_headers(self) -> list[str]:
        if self.strict_cors_enabled:
            return ["X-Request-ID"]
        return ["*"]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync_driver(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
