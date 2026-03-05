<!-- (c) Stefan Loesch 2026. All rights reserved. -->
# Config

This directory contains the server configuration.

## How it works

- **`example.py`** — template config with placeholder values (checked in)
- **`config.py`** — your actual config (gitignored, not checked in)

The `__init__.py` imports from `config.py` if it exists, otherwise falls back to `example.py`.

## Setup

To use your own config, copy the example and edit it:

```bash
cp example.py config.py
# edit config.py with your values
```

`config.py` is gitignored so your secrets and deployment details won't be published to the repo.
