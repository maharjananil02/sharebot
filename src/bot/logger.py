"""Logging configuration for the trading bot with Nepal timezone timestamps."""
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo


NEPAL_TZ = ZoneInfo("Asia/Kathmandu")


def _now_nepal() -> datetime:
    """Return current datetime in Nepal timezone."""
    return datetime.now(tz=NEPAL_TZ)


class NepalFormatter(logging.Formatter):
    """Custom formatter that formats times in Nepal timezone."""

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=NEPAL_TZ)
        if datefmt:
            try:
                return dt.strftime(datefmt)
            except Exception:
                pass
        # Fallback ISO format
        return dt.isoformat()


def setup_logger(name, log_level="INFO", log_file=None, add_console=True, enable_file=False):
    """Setup a logger with optional file and console handlers.

    The logger is configured only once per name to avoid duplicate handlers.
    """
    logger = logging.getLogger(name)
    if getattr(logger, "_bot_logger_configured", False):
        return logger

    logger.setLevel(log_level)
    logger.propagate = False

    logs_dir = "logs"
    if enable_file:
        os.makedirs(logs_dir, exist_ok=True)

    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S %Z"
    formatter = NepalFormatter(fmt=fmt, datefmt=datefmt)

    if add_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if enable_file:
        if log_file is None:
            log_file = os.path.join(logs_dir, f"bot_{_now_nepal().strftime('%Y%m%d')}.log")

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger._bot_logger_configured = True
    return logger


# Create module logger
logger = setup_logger(__name__)
