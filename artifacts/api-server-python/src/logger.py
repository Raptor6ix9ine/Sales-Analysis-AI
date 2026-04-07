import logging
import os
from datetime import datetime

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
is_production = os.getenv('NODE_ENV', '').lower() == 'production'

class ColoredFormatter(logging.Formatter):
    """Add colors to logs in development mode"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if not is_production:
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)

# Create logger
logger = logging.getLogger('api-server')
logger.setLevel(getattr(logging, log_level))

# Create console handler
handler = logging.StreamHandler()
handler.setLevel(getattr(logging, log_level))

# Create formatter
if is_production:
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
else:
    formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)
