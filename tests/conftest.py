# (c) Stefan Loesch 2026. All rights reserved.
import pytest
from httpx import ASGITransport, AsyncClient

from app.server import create_app
from app.qrdata import QRCODES


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def slug():
    """First slug from whatever data is loaded (example or real)."""
    return QRCODES[0].slug
