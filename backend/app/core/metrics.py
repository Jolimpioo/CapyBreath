from __future__ import annotations

from collections import defaultdict
from threading import Lock


class SecurityMetricsStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._auth = defaultdict(int)
        self._http_status_by_endpoint = defaultdict(lambda: defaultdict(int))
        self._rate_limit_blocks = defaultdict(int)

    def increment_auth(self, flow: str, outcome: str) -> None:
        key = f"{flow}_{outcome}"
        with self._lock:
            self._auth[key] += 1

    def increment_http_status(self, endpoint: str, status_code: int) -> None:
        if status_code not in (401, 403, 429):
            return

        with self._lock:
            self._http_status_by_endpoint[endpoint][str(status_code)] += 1

        if status_code == 429:
            self.increment_rate_limit_block(endpoint)

    def increment_rate_limit_block(self, endpoint: str) -> None:
        with self._lock:
            self._rate_limit_blocks[endpoint] += 1

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "auth": dict(self._auth),
                "http_status_by_endpoint": {
                    endpoint: dict(statuses)
                    for endpoint, statuses in self._http_status_by_endpoint.items()
                },
                "rate_limit_blocks": dict(self._rate_limit_blocks),
            }


security_metrics = SecurityMetricsStore()