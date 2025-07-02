import logging
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, 'app.log')

def get_logger(name: str = 'app', level=logging.INFO):
    logger = logging.getLogger(name)
    if not logger.handlers: # Avoid adding multiple handlers
        logger.setLevel(level)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s (%(filename)s:%(lineno)d)')
        
        # Console Handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File Handler (Rotating)
        # Rotates log file when it reaches 1MB, keeps 5 backup logs
        fh = RotatingFileHandler(LOG_FILE_PATH, maxBytes=1024*1024, backupCount=5, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger

# Global logger instance if you prefer
# app_logger = get_logger()