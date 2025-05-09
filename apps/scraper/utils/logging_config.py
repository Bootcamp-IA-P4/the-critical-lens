import os
import logging
from logging.handlers import RotatingFileHandler

def configure_logging(log_dir="logs", log_level=logging.INFO):
    """
    Configure logging system for the scraper.
    
    Args:
        log_dir (str): Directory to store log files
        log_level: Minimum log level to capture
        
    Returns:
        logging.Logger: Configured logger for the scraper
    """
    try:
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatters
        file_formatter = logging.Formatter(
          '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
          '%(asctime)s - %(levelname)s - %(message)s'
        )

        # Configure file handler with rotation (10MB files, keep 5 backups)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'scraper.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)

        # Configure error log separately
        error_handler = RotatingFileHandler(
            os.path.join(log_dir, 'scraper_error.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)

        # Configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)

        # Add handlers to root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(console_handler)

        # Configure specific logger for our package
        scraper_logger = logging.getLogger('apps.scraper')
        scraper_logger.setLevel(log_level)
        
        # Log a success message to verify configuration
        scraper_logger.info("Logging system initialized successfully")
        
        return scraper_logger
    
    except Exception as e:
        # Fallback to basic configuration if there's any error
        print(f"Error configuring logging system: {e}")
        print("Falling back to basic configuration")
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        
        return logging.getLogger('apps.scraper')