<!-- (c) Stefan Loesch 2026. All rights reserved. -->
# QR Data

This directory contains the QR code entry definitions.

## How it works

- **`models.py`** — `QREntry` Pydantic model (checked in)
- **`example.py`** — sample data with placeholder entries (checked in)
- **`qrdata.py`** — your actual data (gitignored, not checked in)

The `__init__.py` conditionally imports from `qrdata.py` if it exists, otherwise falls back to `example.py`.

## Setup

To use your own QR entries, copy the example and edit it:

```bash
cp example.py qrdata.py
# edit qrdata.py with your entries
```

`qrdata.py` is gitignored so your private data won't be published to the repo.
