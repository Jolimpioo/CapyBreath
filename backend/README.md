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
