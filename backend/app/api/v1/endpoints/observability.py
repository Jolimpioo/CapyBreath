from fastapi import APIRouter

from app.core.metrics import security_metrics

router = APIRouter(prefix="/observability", tags=["Observability"])


@router.get(
    "/security-metrics",
    summary="Resumo operacional de auth/abuso"
)
async def get_security_metrics_summary():
    """
    Retorna um snapshot simples para acompanhamento diário.
    """
    return security_metrics.snapshot()