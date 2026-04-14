import json
import logging
from datetime import datetime, timezone
from typing import Any

REDACTED = "***redacted***"
SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "cookie",
    "set-cookie",
    "secret",
    "secret_key",
}


def sanitize_log_data(value: Any, *, key: str | None = None) -> Any:
    normalized_key = (key or "").lower()
    if normalized_key in SENSITIVE_KEYS:
        return REDACTED

    if isinstance(value, dict):
        return {
            nested_key: sanitize_log_data(nested_value, key=str(nested_key))
            for nested_key, nested_value in value.items()
        }

    if isinstance(value, list):
        return [sanitize_log_data(item) for item in value]

    if isinstance(value, tuple):
        return tuple(sanitize_log_data(item) for item in value)

    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        event_data = getattr(record, "event_data", None)
        if isinstance(event_data, dict):
            payload.update(sanitize_log_data(event_data))

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(log_level: str = "INFO") -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def mask_sensitive(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) <= 4:
        return "***"
    return f"{value[:2]}***{value[-2:]}"
