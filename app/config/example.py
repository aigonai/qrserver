# (c) Stefan Loesch 2026. All rights reserved.
import os

URL = "qr.example.com"
SOCKET_PATH = "/run/example/qr.sock"
PORT = 8199
LOG_FILE = "access.jsonl"
SIGNING_SECRET = os.environ.get("QR_SIGNING_SECRET", "change-me-in-production")
QR_CREDENTIAL = "change-me"
