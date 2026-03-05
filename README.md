<!-- (c) Stefan Loesch 2026. All rights reserved. -->
# QR Server

A lightweight FastAPI service for QR code redirects and image generation.

## Features

- **Short URL redirects** — `/{slug}` redirects to a configured target URL
- **QR code images** — `/{slug}/qr.png` generates a QR code PNG for the redirect URL
- **Signed slugs** — optional HMAC-style signatures for non-guessable access-controlled URLs
- **Customizable QR codes** — foreground/background colors, size, border, transparency
- **Access logging** — JSON Lines request log

## Quick Start

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run on default port (8199)
uv run python -m app.main

# Run on a specific port
uv run python -m app.main --port 8080

# Run on a Unix socket (production, behind Caddy)
uv run python -m app.main --socket /run/qr.sock
```

## Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Index page listing all QR entries |
| `GET /health` | Health check |
| `GET /{slug}` | 302 redirect to the target URL |
| `GET /{slug}/qr.png` | QR code PNG image |

### QR Image Parameters

| Param | Default | Description |
|---|---|---|
| `fg` | `black` | Foreground color (name, hex, or `blank` for transparent) |
| `bg` | `white` | Background color (name, hex, or `blank` for transparent) |
| `size` | `10` | Box size in pixels (1–50) |
| `border` | `4` | Border width in boxes (0–20) |
| `ran` | — | Random string for signed URL generation |
| `cred` | — | Credential to authorize signed QR generation |

### Examples

```bash
# Default black-on-white QR code
/{slug}/qr.png

# Red foreground on white background
/{slug}/qr.png?fg=red

# Custom hex color with transparent background
/{slug}/qr.png?fg=%23336699&bg=blank

# Larger boxes, no border
/{slug}/qr.png?size=20&border=0

# Generate a signed QR code (requires credential)
/{slug}/qr.png?cred=YOUR_CREDENTIAL

# Signed QR code with a random component
/{slug}/qr.png?ran=myRandom123&cred=YOUR_CREDENTIAL
```

When `cred` matches the configured `QR_CREDENTIAL`, the generated QR code encodes a signed URL (`/{slug}-{signature}` or `/{slug}-{ran}-{signature}`) instead of the plain slug. Without a valid credential, the QR code encodes the plain slug.

## Signed Slugs

Entries with `signature=True` require a signed URL — plain slug access returns 403.

Signed URL formats:
```
/{slug}-{signature}              # signs the slug
/{slug}-{random}-{signature}     # signs slug + random
```

The signature is the first 6 characters of a base62-encoded SHA-256 hash of the signing secret concatenated with the preimage.

Set the signing secret via the `QR_SIGNING_SECRET` environment variable.

## Configuration

Copy `app/config/example.py` to `app/config/config.py` and edit, or use environment variables:

| Setting | Env Var | Default |
|---|---|---|
| `SIGNING_SECRET` | `QR_SIGNING_SECRET` | `change-me-in-production` |
| `QR_CREDENTIAL` | — | `change-me` |

## License

MIT — see [LICENSE](LICENSE).

Copyright (c) 2026 Stefan Loesch
