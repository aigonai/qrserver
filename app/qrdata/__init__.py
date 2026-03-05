# (c) Stefan Loesch 2026. All rights reserved.
from .models import QREntry

try:
    from .qrdata import QRCODES
    QRDATA_SOURCE = "qrdata"
except ImportError:
    from .example import QRCODES
    QRDATA_SOURCE = "example"

QRCODES_BY_SLUG: dict[str, QREntry] = {qr.slug: qr for qr in QRCODES}

__all__ = ["QREntry", "QRCODES", "QRCODES_BY_SLUG", "QRDATA_SOURCE"]
