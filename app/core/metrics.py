"""Metrics.

Prometheus 기반 최소 계측:
- http_requests_total{path,method}
- http_errors_total{path,method,status}
- (optional) http_request_duration_seconds{path,method}
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram
from starlette.requests import Request


http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    labelnames=("path", "method"),
)

http_errors_total = Counter(
    "http_errors_total",
    "Total number of HTTP error responses (status >= 400)",
    labelnames=("path", "method", "status"),
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    labelnames=("path", "method"),
)


def _path_template(request: Request) -> str:
    """
    가능한 경우 실제 path 대신 라우트 템플릿을 사용해 라벨 카디널리티를 제한한다.
    예: /jobs/{job_id}
    """
    route = request.scope.get("route")
    template = getattr(route, "path", None)
    if isinstance(template, str) and template:
        return template
    return request.url.path


def observe_http_request(*, request: Request, status_code: int, duration_seconds: float) -> None:
    # /metrics 자체는 보통 Prometheus가 주기적으로 호출하므로 제외(노이즈/자기참조 방지)
    if request.url.path == "/metrics":
        return

    path = _path_template(request)
    method = request.method

    http_requests_total.labels(path=path, method=method).inc()
    http_request_duration_seconds.labels(path=path, method=method).observe(duration_seconds)

    if status_code >= 400:
        http_errors_total.labels(path=path, method=method, status=str(status_code)).inc()
