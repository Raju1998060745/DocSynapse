import logging
import os

def setup_logger(name='service_2'):
    """
    Configure logger with file and console handlers
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Only add handlers if logger doesn't have any
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler("logs/service_2.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s.%(module)s: %(message)s"
        )
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s.%(module)s: %(message)s"
        )
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger