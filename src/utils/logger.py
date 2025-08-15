"""
Logging utilities for the Wedding Planner Hiring System
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import colorlog
from src.config import Config

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Setup logger with both file and console output"""
    
    # Create logs directory if it doesn't exist
    Config.LOGS_DIR.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green', 
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # File handler
    log_file = Config.LOGS_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_agent_action(logger: logging.Logger, agent_name: str, action: str, details: dict = None):
    """Log agent actions with structured format"""
    message = f"[{agent_name}] {action}"
    if details:
        detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
        message += f" | {detail_str}"
    logger.info(message)

def log_api_call(logger: logging.Logger, service: str, endpoint: str, cost: float = None):
    """Log API calls for monitoring"""
    message = f"API Call: {service} - {endpoint}"
    if cost:
        message += f" | Cost: ${cost:.4f}"
    logger.info(message)

def log_human_gate(logger: logging.Logger, gate_type: str, data_summary: str):
    """Log human approval gates"""
    logger.warning(f"HUMAN APPROVAL REQUIRED: {gate_type} | {data_summary}")

def log_error_with_retry(logger: logging.Logger, error: Exception, retry_count: int, max_retries: int):
    """Log errors with retry information"""
    logger.error(f"Error (attempt {retry_count}/{max_retries}): {str(error)}")
    if retry_count < max_retries:
        logger.info(f"Retrying in {2**retry_count} seconds...")
    else:
        logger.error("Max retries exceeded. Manual intervention required.")