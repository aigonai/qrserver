# (c) Stefan Loesch 2026. All rights reserved.
import asyncio
import argparse
import logging

from .config import PORT
from .server import QRServer


async def main():
    parser = argparse.ArgumentParser(description="QR Code Server")
    parser.add_argument("--socket", default=None, help="Unix socket path")
    parser.add_argument("--port", type=int, default=None, help=f"Listen on TCP port instead of socket (default: {PORT})")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Default: port mode (dev). Use --socket for production behind Caddy.
    port = args.port if args.port is not None else (None if args.socket else PORT)

    server = QRServer(socket_path=args.socket, port=port)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
