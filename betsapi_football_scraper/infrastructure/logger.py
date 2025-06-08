from __future__ import annotations
import sys
from loguru import logger


logger.remove()


logger.add(
    sys.stderr,
    level="INFO",
    backtrace=False,
    diagnose=False,
    colorize=True,
)


logger.disable("urllib3")

__all__: list[str] = ["logger"]
