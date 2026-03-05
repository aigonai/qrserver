# (c) Stefan Loesch 2026. All rights reserved.
import hashlib
import io
import logging
import os

import qrcode
import qrcode.constants
from fastapi import FastAPI, Query, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from .redirect_log import RedirectLogMiddleware
from .config import CONFIG_SOURCE, PORT, QR_CREDENTIAL, SIGNING_SECRET, SOCKET_PATH, URL
from .version import __version__
from .qrdata import QREntry, QRCODES, QRCODES_BY_SLUG, QRDATA_SOURCE

logger = logging.getLogger(__name__)

BASE62 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def compute_signature(preimage: str) -> str:
    digest = hashlib.sha256((SIGNING_SECRET + preimage).encode()).digest()
    num = int.from_bytes(digest, "big")
    chars = []
    for _ in range(6):
        num, rem = divmod(num, 62)
        chars.append(BASE62[rem])
    return "".join(chars)


FORBIDDEN = "FORBIDDEN"


def resolve_slug(raw: str) -> QREntry | str | None:
    """Return a QREntry on success, FORBIDDEN if signature required, or None if not found."""
    # Direct lookup — works for non-signed entries
    entry = QRCODES_BY_SLUG.get(raw)
    if entry:
        return FORBIDDEN if entry.signature else entry

    # Try splitting to extract signature
    parts = raw.split("-")
    if len(parts) < 2:
        return None

    sig = parts[-1]
    if len(sig) != 6:
        return None

    if len(parts) == 2:
        slug = parts[0]
        preimage = slug
    else:
        slug = parts[0]
        preimage = "-".join(parts[:-1])

    entry = QRCODES_BY_SLUG.get(slug)
    if not entry:
        return None

    if compute_signature(preimage) == sig:
        return entry
    return FORBIDDEN


def parse_color(value: str | None, default: str) -> str | None:
    """Parse a color parameter. Returns None for blank/transparent, else the color string."""
    if value is None:
        return default
    value = value.strip()
    if value.lower() in ("", "none", "transparent", "blank"):
        return None
    return value


def create_app() -> FastAPI:
    app = FastAPI(
        title="QR Code Server",
        description=f"QR code redirect and image service at {URL}",
        docs_url=None,
        redoc_url=None,
    )

    app.add_middleware(RedirectLogMiddleware)

    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "service": "qr-server",
            "version": __version__,
            "config": CONFIG_SOURCE,
            "qrdata": QRDATA_SOURCE,
        }

    @app.get("/", response_class=HTMLResponse)
    async def index():
        rows = ""
        for qr in QRCODES:
            rows += (
                f"<tr>"
                f"<td><a href='/{qr.slug}'>{qr.slug}</a></td>"
                f"<td>{qr.label}</td>"
                f"<td><a href='{qr.url}'>{qr.url}</a></td>"
                f"<td><a href='/{qr.slug}/qr.png'>qr.png</a></td>"
                f"</tr>"
            )
        return f"""<!doctype html>
<html><head><title>QR Server - {URL}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
th {{ background: #f5f5f5; }}
a {{ color: #0066cc; }}
</style></head>
<body>
<h1>QR Server</h1>
<p>{URL}</p>
<table>
<tr><th>Slug</th><th>Label</th><th>Target URL</th><th>QR Code</th></tr>
{rows}
</table>
</body></html>"""

    @app.get("/{slug}")
    async def redirect_slug(slug: str):
        result = resolve_slug(slug)
        if result is FORBIDDEN:
            return Response(status_code=403, content="Forbidden")
        if not result:
            return Response(status_code=404, content="Not found")
        return RedirectResponse(url=result.url, status_code=302)

    @app.get("/{slug}/qr.png")
    async def qr_image(
        slug: str,
        fg: str | None = Query(None, description="Foreground color (name, hex, or 'blank' for transparent)"),
        bg: str | None = Query(None, description="Background color (name, hex, or 'blank' for transparent)"),
        size: int = Query(10, ge=1, le=50, description="Box size in pixels"),
        border: int = Query(4, ge=0, le=20, description="Border size in boxes"),
        ran: str | None = Query(None, description="Random string for signed URL"),
        cred: str | None = Query(None, description="Credential for signed QR generation"),
    ):
        result = resolve_slug(slug)
        if result is FORBIDDEN:
            return Response(status_code=403, content="Forbidden")
        if not result:
            return Response(status_code=404, content="Not found")
        entry = result

        # Build the URL path encoded in the QR code
        if cred == QR_CREDENTIAL:
            if ran:
                preimage = f"{entry.slug}-{ran}"
                sig = compute_signature(preimage)
                qr_path = f"{entry.slug}-{ran}-{sig}"
            else:
                sig = compute_signature(entry.slug)
                qr_path = f"{entry.slug}-{sig}"
        else:
            qr_path = entry.slug

        fill_color = parse_color(fg, "black")
        back_color = parse_color(bg, "white")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=size,
            border=border,
        )
        qr.add_data(f"https://{URL}/{qr_path}")
        qr.make(fit=True)

        img = qr.make_image(
            fill_color=fill_color or "black",
            back_color=back_color or "white",
        )

        # If transparent background or foreground requested, convert to RGBA
        if fill_color is None or back_color is None:
            img = img.convert("RGBA")
            pixels = img.load()
            w, h = img.size
            for y in range(h):
                for x in range(w):
                    r, g, b, a = pixels[x, y]
                    if back_color is None and (r, g, b) == (255, 255, 255):
                        pixels[x, y] = (255, 255, 255, 0)
                    if fill_color is None and (r, g, b) == (0, 0, 0):
                        pixels[x, y] = (0, 0, 0, 0)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return Response(content=buf.getvalue(), media_type="image/png")

    return app


class QRServer:
    def __init__(self, socket_path: str | None = None, port: int | None = None):
        self.socket_path = socket_path or SOCKET_PATH
        self.port = port
        self.app = create_app()

    async def start(self):
        import uvicorn

        if self.port:
            logger.info(f"Starting QR Server on port: {self.port}")
            config = uvicorn.Config(
                self.app,
                host="0.0.0.0",
                port=self.port,
                log_level="info",
            )
        else:
            socket_dir = os.path.dirname(self.socket_path)
            if socket_dir:
                os.makedirs(socket_dir, exist_ok=True)

            if os.path.exists(self.socket_path):
                logger.info(f"Removing stale socket: {self.socket_path}")
                os.unlink(self.socket_path)

            logger.info(f"Starting QR Server on socket: {self.socket_path}")
            config = uvicorn.Config(
                self.app,
                uds=self.socket_path,
                log_level="info",
            )

        server = uvicorn.Server(config)
        await server.serve()
