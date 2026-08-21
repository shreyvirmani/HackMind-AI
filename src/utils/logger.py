"""
Application logging configuration.
"""

import logging
import os
from pathlib import Path


def configure_logger():
    logger = logging.getLogger("HackMind")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers during reloads/imports.
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # Vercel's deployment filesystem is read-only.
    # Use stdout/stderr there so Vercel can capture the logs.
    is_vercel = os.getenv("VERCEL") == "1"

    if is_vercel:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    else:
        # Local development: keep persistent file logging.
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(
            logs_dir / "hackmind.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    logger.propagate = False

    return logger


logger = configure_logger()