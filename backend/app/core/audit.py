import logging
from typing import Any
from fastapi import Request


audit_logger = logging.getLogger("app.audit")


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
        "latency_ms": None,
    }

    if extra:
        event_data.update(extra)

    audit_logger.info("security_event", extra={"event_data": event_data})
