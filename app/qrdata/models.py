# (c) Stefan Loesch 2026. All rights reserved.
from pydantic import BaseModel


class QREntry(BaseModel):
    slug: str
    url: str
    label: str = ""
    signature: bool = False
