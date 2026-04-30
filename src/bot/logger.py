"""Logging configuration for the trading bot"""
import logging
import os
from datetime import datetime, timedelta, timezone


NEPAL_TZ = timezone(timedelta(hours=5, minutes=45))


def _nepal_time_converter(timestamp: float):
    """Convert epoch timestamp to Nepal local timetuple for logging."""
    return datetime.fromtimestamp(timestamp, tz=NEPAL_TZ).timetuple()


def _now_nepal() -> datetime:
    """Return current datetime in Nepal timezone."""
    return datetime.now(tz=NEPAL_TZ)


def setup_logger(name, log_level="INFO", log_file=None, add_console=True):
    """Setup a logger with optional file and console handlers.

    The logger is configured only once per name to avoid duplicate handlers.
    """
    logger = logging.getLogger(name)
    if getattr(logger, "_bot_logger_configured", False):
        return logger

    logger.setLevel(log_level)
    logger.propagate = False

    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    formatter.converter = _nepal_time_converter

    if add_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

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
