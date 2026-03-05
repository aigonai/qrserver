# (c) Stefan Loesch 2026. All rights reserved.
import pytest

from app.server import compute_signature
from app.config import QR_CREDENTIAL


pytestmark = pytest.mark.anyio


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


async def test_index(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "QR Server" in resp.text


async def test_redirect(client, slug):
    resp = await client.get(f"/{slug}", follow_redirects=False)
    assert resp.status_code == 302


async def test_redirect_not_found(client):
    resp = await client.get("/nonexistent")
    assert resp.status_code == 404


async def test_redirect_signed(client, slug):
    sig = compute_signature(slug)
    resp = await client.get(f"/{slug}-{sig}", follow_redirects=False)
    assert resp.status_code == 302


async def test_redirect_invalid_sig(client, slug):
    resp = await client.get(f"/{slug}-XXXXXX")
    assert resp.status_code == 403


async def test_qr_image(client, slug):
    resp = await client.get(f"/{slug}/qr.png")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert resp.content[:4] == b"\x89PNG"


async def test_qr_image_not_found(client):
    resp = await client.get("/nonexistent/qr.png")
    assert resp.status_code == 404


async def test_qr_image_signed_with_cred(client, slug):
    resp = await client.get(f"/{slug}/qr.png?cred={QR_CREDENTIAL}")
    assert resp.status_code == 200
    assert resp.content[:4] == b"\x89PNG"


async def test_qr_image_signed_with_ran_and_cred(client, slug):
    resp = await client.get(f"/{slug}/qr.png?ran=xyz&cred={QR_CREDENTIAL}")
    assert resp.status_code == 200
    assert resp.content[:4] == b"\x89PNG"


async def test_qr_image_wrong_cred_no_signing(client, slug):
    resp = await client.get(f"/{slug}/qr.png?cred=wrong")
    assert resp.status_code == 200
    # Still returns a QR, just not signed
