# Backend CapyBreath

## Estratégia oficial de bootstrap do banco (CB-005)

A estratégia oficial para schema migration é **Apenas Alembic** (dev e prod).

- O startup da API **não** executa `create_all`.
- O startup apenas valida conectividade com `SELECT 1`.
- A criação/evolução de schema deve ser feita com migrações versionadas.

### Fluxo recomendado

```bash
cd backend
alembic upgrade head
python -m app.main
```

Para gerar nova migração:

```bash
cd backend
alembic revision --autogenerate -m "descricao"
alembic upgrade head
```

## Endpoint canônico de usuário autenticado (CB-011)

- **Canônico:** `GET /api/v1/users/me`
- **Legado (deprecated):** `GET /api/v1/auth/me`

## Endpoints expostos como roadmap (CB-012)

Os endpoints abaixo estão expostos, mas marcados como `deprecated` no OpenAPI por não estarem integrados na UI atual:

- `DELETE /api/v1/users/me`
- `GET /api/v1/sessions/filter/by-date`
- `GET /api/v1/sessions/filter/by-technique/{technique_variant}`
- `GET /api/v1/achievements/stats`
- `GET /api/v1/auth/me`

Isso reduz ambiguidade de uso até integração futura ou remoção definitiva.

## Feature flags de segurança (CB-SEC-001)

As flags abaixo são lidas por variáveis de ambiente com defaults explícitos em `app/core/config.py`:

- `SECURE_COOKIES_ENABLED` (default: `false`)
- `STRICT_CORS_ENABLED` (default: `false`)
- `AUTH_DUAL_MODE_ENABLED` (default: `false`)
- `CSP_REPORT_ONLY_ENABLED` (default: `true`)

### Sugestão por ambiente

- **dev**: `SECURE_COOKIES_ENABLED=false`, `STRICT_CORS_ENABLED=false`, `AUTH_DUAL_MODE_ENABLED=false`, `CSP_REPORT_ONLY_ENABLED=true`
- **staging**: `SECURE_COOKIES_ENABLED=true`, `STRICT_CORS_ENABLED=true`, `AUTH_DUAL_MODE_ENABLED=true`, `CSP_REPORT_ONLY_ENABLED=true`
- **prod**: `SECURE_COOKIES_ENABLED=true`, `STRICT_CORS_ENABLED=true`, `AUTH_DUAL_MODE_ENABLED=true`, `CSP_REPORT_ONLY_ENABLED=false`

### Exemplo `.env`

```env
SECURE_COOKIES_ENABLED=true
STRICT_CORS_ENABLED=true
AUTH_DUAL_MODE_ENABLED=true
CSP_REPORT_ONLY_ENABLED=true
```

## CORS com credenciais (CB-CORS-031)

- A API roda com `allow_credentials=True`.
- Por segurança, o backend valida que `CORS_ORIGINS` **não** contenha `*` (wildcard).
- Defina origens explícitas separadas por vírgula, por exemplo:

```env
CORS_ORIGINS=http://localhost:5173,https://app.capybreath.com
```

No frontend, habilite envio de cookies com:

```env
VITE_AUTH_WITH_CREDENTIALS=true
```
