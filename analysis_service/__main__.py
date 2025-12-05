"""
Entry point for running the analysis service.

Usage: python -m analysis_service
"""

import logging

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Analysis service starting...")

    # Server implementation will be added in Phase 2
    logger.info("Service ready (placeholder)")

if __name__ == "__main__":
    main()
