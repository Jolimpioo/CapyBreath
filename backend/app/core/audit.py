import logging
import time
from typing import Any
from fastapi import Request

from app.core.logging import sanitize_log_data


audit_logger = logging.getLogger("app.audit")


def _get_latency_ms(request: Request) -> float | None:
    started_at = getattr(request.state, "request_started_at", None)
    if started_at is None:
        return None
    return round((time.perf_counter() - started_at) * 1000, 2)


def log_security_event(
    *,
    event: str,
    request: Request,
    status_code: int,
    user_id: str | None = None,
    extra: dict[str, Any] | None = None
) -> None:
    event_data: dict[str, Any] = {
        "event": event,
        "request_id": getattr(request.state, "request_id", None),
        "user_id": user_id,
        "ip": request.client.host if request.client else None,
        "path": request.url.path,
        "status_code": status_code,
        "latency_ms": _get_latency_ms(request),
    }

    if extra:
        event_data.update(extra)

    audit_logger.info(
        "security_event",
        extra={"event_data": sanitize_log_data(event_data)}
    )
