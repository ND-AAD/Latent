"""
Entry point for running the analysis service.

Usage: python -m analysis_service [--port PORT] [--host HOST]
"""

import argparse
import logging
import sys

from .server import run_server


def main():
    parser = argparse.ArgumentParser(description="Latent Analysis Service")
    parser.add_argument("--port", type=int, default=5555, help="Port to listen on")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting analysis service on {args.host}:{args.port}")

    try:
        run_server(host=args.host, port=args.port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
