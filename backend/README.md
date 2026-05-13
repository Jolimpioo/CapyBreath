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
- `REFRESH_COOKIE_SAMESITE` (default: `lax`; valores: `lax`, `strict`, `none`)

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
REFRESH_COOKIE_SAMESITE=lax
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

Quando essa opção está ativa, o frontend envia o header `X-Auth-Mode: cookie`;
em CORS estrito, esse header deve permanecer permitido.

## Métricas de auth/abuso (CB-SEC-002)

Foi adicionado um snapshot operacional para acompanhamento diário:

- `GET /api/v1/observability/security-metrics`

Estrutura retornada:

- `auth.login_success`, `auth.login_failed`
- `auth.refresh_success`, `auth.refresh_failed`
- `http_status_by_endpoint` (com foco em `401`, `403`, `429`)
- `rate_limit_blocks` (incrementado para respostas `429` por endpoint)

Exemplo de consulta:

```bash
curl -s http://localhost:8000/api/v1/observability/security-metrics | jq .
```

## Dual mode auth (CB-AUTH-010)

Quando `AUTH_DUAL_MODE_ENABLED=true`, o backend aceita temporariamente os dois modos:

- **Modo Bearer (legado):** refresh via body (`refresh_token`).
- **Modo Cookie (novo):** refresh token enviado em cookie HttpOnly (`refresh_token`)
  e sinalizado pelo header `X-Auth-Mode: cookie`.

## Refresh token em cookie HttpOnly (CB-AUTH-011)

- `POST /api/v1/auth/login` e `POST /api/v1/auth/register` passam a setar cookie de refresh.
- Clientes cookie recebem `refresh_token: null` no body para evitar dependência de JavaScript/localStorage.
- `POST /api/v1/auth/refresh` prioriza cookie e mantém fallback para body em clientes legados.
- `POST /api/v1/auth/logout` limpa cookie quando dual mode está ativo.
- Eventos de auditoria registram `auth_mode` como `cookie` ou `bearer`.

Telemetria de auditoria inclui `auth_mode` (`bearer` ou `cookie`) nos eventos principais de auth.
