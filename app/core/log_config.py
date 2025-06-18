import logging
import sys
from pathlib import Path

from loguru import logger

LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)
LOG_FILE = LOG_PATH / "fastapi.log"

logger.remove()  # Remove default logger

# Console logging (for all logs, but only from API-related modules)
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>",
    filter=lambda record: record["name"].startswith(("app", "fastapi", "uvicorn")),
    backtrace=True,
    diagnose=True,
)

# File logging (API logs only)
logger.add(
    LOG_FILE,
    level="INFO",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    serialize=True,
    filter=lambda record: record["name"].startswith(("app", "fastapi", "uvicorn")),
)


def init_logger():
    logger.info("Logger initialized")


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            # Try to map logging level to Loguru level
            level = logger.level(record.levelname).name
        except ValueError:
            # If the level doesn't exist in Loguru, fallback to raw level number
            level = record.levelno

        logger.log(level, record.getMessage())


# def patch_loggers():
#     intercept_handler = InterceptHandler()
#     for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
#         logging.getLogger(name).handlers = [intercept_handler]
#         logging.getLogger(name).setLevel(logging.DEBUG)
