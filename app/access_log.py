# (c) Stefan Loesch 2026. All rights reserved.
import json
import time
from pathlib import Path

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from .config import LOG_FILE


class AccessLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, log_path: Path | None = None):
        super().__init__(app)
        self.log_path = log_path or Path(LOG_FILE)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)

        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "method": request.method,
            "path": str(request.url.path),
            "query": str(request.url.query) or None,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "client": request.headers.get("x-forwarded-for", request.client.host if request.client else None),
            "user_agent": request.headers.get("user-agent"),
            "referer": request.headers.get("referer"),
        }

        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return response
