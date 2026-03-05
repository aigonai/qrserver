# (c) Stefan Loesch 2026. All rights reserved.
from .models import QREntry

QRCODES: list[QREntry] = [
    QREntry(slug="skl", url="https://www.linkedin.com/in/skloesch/", label="Stefan LinkedIn"),
]
