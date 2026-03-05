# (c) Stefan Loesch 2026. All rights reserved.
from app.server import compute_signature, resolve_slug, FORBIDDEN
from app.qrdata import QRCODES_BY_SLUG


def test_compute_signature_deterministic():
    sig1 = compute_signature("test")
    sig2 = compute_signature("test")
    assert sig1 == sig2


def test_compute_signature_length():
    sig = compute_signature("anything")
    assert len(sig) == 6


def test_compute_signature_base62_chars():
    sig = compute_signature("check-chars")
    assert all(c.isalnum() for c in sig)


def test_compute_signature_different_inputs():
    assert compute_signature("a") != compute_signature("b")


def test_resolve_plain_slug(slug):
    entry = resolve_slug(slug)
    assert entry is not None
    assert entry.slug == slug


def test_resolve_nonexistent_slug():
    assert resolve_slug("nonexistent") is None


def test_resolve_signed_slug(slug):
    sig = compute_signature(slug)
    entry = resolve_slug(f"{slug}-{sig}")
    assert entry is not None
    assert entry.slug == slug


def test_resolve_signed_slug_with_random(slug):
    preimage = f"{slug}-abc123"
    sig = compute_signature(preimage)
    entry = resolve_slug(f"{slug}-abc123-{sig}")
    assert entry is not None
    assert entry.slug == slug


def test_resolve_invalid_signature(slug):
    assert resolve_slug(f"{slug}-XXXXXX") is FORBIDDEN


def test_resolve_wrong_signature_length(slug):
    assert resolve_slug(f"{slug}-abc") is None


def test_resolve_signed_required_blocks_plain(slug):
    entry = QRCODES_BY_SLUG[slug]
    original = entry.signature
    try:
        entry.signature = True
        assert resolve_slug(slug) is FORBIDDEN
        # But signed still works
        sig = compute_signature(slug)
        assert resolve_slug(f"{slug}-{sig}") is not None
    finally:
        entry.signature = original
