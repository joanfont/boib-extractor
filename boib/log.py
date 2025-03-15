import logging
import sys

def setup_logging(level: str = 'DEBUG'):
    # Create logger

    logger = logging.getLogger('boib')
    logger.setLevel(getattr(logging, level.upper()))

    # Create formatter and console handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Create a default logger instance
logger = setup_logging() 