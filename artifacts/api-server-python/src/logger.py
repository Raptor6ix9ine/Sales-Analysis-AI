"""Logging configuration for the API server."""

import logging
import os


log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
is_production = os.getenv('APP_ENV', os.getenv('NODE_ENV', '')).lower() == 'production'


class ColoredFormatter(logging.Formatter):
    """Add ANSI colors to log levels in development mode."""

    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
    }
    RESET = '\033[0m'

    def format(self, record):
        if not is_production and record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


# Build logger
logger = logging.getLogger('api-server')
logger.setLevel(getattr(logging, log_level))

_handler = logging.StreamHandler()
_handler.setLevel(getattr(logging, log_level))
_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if is_production
    else ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger.addHandler(_handler)
