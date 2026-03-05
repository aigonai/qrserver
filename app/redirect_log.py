# (c) Stefan Loesch 2026. All rights reserved.
import json
import time
from pathlib import Path

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from .config import LOG_FILE


class RedirectLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, log_path: Path | None = None):
        super().__init__(app)
        self.log_path = log_path or Path(LOG_FILE)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.time()
        response = await call_next(request)

        if response.status_code == 302:
            duration_ms = round((time.time() - start) * 1000, 2)
            entry = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "path": str(request.url.path),
                "status": 302,
                "duration_ms": duration_ms,
                "client": request.headers.get("x-forwarded-for", request.client.host if request.client else None),
                "user_agent": request.headers.get("user-agent"),
            }
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

        return response
