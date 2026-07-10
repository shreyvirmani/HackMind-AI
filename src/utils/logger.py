"""
Application logging configuration.
"""

import logging
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/hackmind.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("HackMind")