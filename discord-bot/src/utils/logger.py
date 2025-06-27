import logging
import sys
import os
from datetime import datetime
from config import Config

def setup_logger():
    """Set up logging configuration for the bot."""
    
    # Create logger
    logger = logging.getLogger('mealbot')
    
    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler - always add this for immediate feedback
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if Config.LOG_FILE:
        try:
            # Ensure logs directory exists
            log_dir = os.path.dirname(Config.LOG_FILE) if os.path.dirname(Config.LOG_FILE) else '.'
            if log_dir != '.' and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            # Test log file creation
            logger.info(f"Log file created: {Config.LOG_FILE}")
        except Exception as e:
            print(f"Could not create file handler: {e}")
            logger.warning(f"Could not create file handler: {e}")
    
    # Set discord.py logging to INFO to see connection issues
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.INFO)
    
    # Reduce aiohttp logging noise
    aiohttp_logger = logging.getLogger('aiohttp')
    aiohttp_logger.setLevel(logging.WARNING)
    
    # Test the logger
    logger.info("Logger setup completed successfully")
    
    return logger
