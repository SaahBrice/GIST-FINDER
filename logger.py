import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime
from rich.console import Console
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from contextlib import contextmanager

# Rich console for beautiful terminal output
console = Console()

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Setup comprehensive logging with daily rotation
def setup_logger(name):
    """
    Setup logger with daily rotating files
    Format: logs/gistme_YYYY-MM-DD.log
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Daily rotating file handler
    log_filename = f"logs/gistme_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = TimedRotatingFileHandler(
        filename=log_filename,
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days of logs
        encoding='utf-8'
    )
    file_handler.suffix = "%Y-%m-%d"
    
    # Detailed formatter with filename and function
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logger('gistme')

# Custom log levels
SUCCESS = 25  # Between INFO and WARNING
logging.addLevelName(SUCCESS, 'SUCCESS')

def log_info(message, module=""):
    """Log info level"""
    logger.info(f"[{module}] {message}" if module else message)
    console.print(f"ℹ️  [cyan]{message}[/cyan]")

def log_success(message, module=""):
    """Log success level"""
    logger.log(SUCCESS, f"[{module}] {message}" if module else message)
    console.print(f"✅ [green]{message}[/green]")

def log_warning(message, module=""):
    """Log warning level"""
    logger.warning(f"[{module}] {message}" if module else message)
    console.print(f"⚠️  [yellow]{message}[/yellow]")

def log_error(message, module=""):
    """Log error level"""
    logger.error(f"[{module}] {message}" if module else message)
    console.print(f"❌ [red]{message}[/red]")

@contextmanager
def spinner(text):
    """Context manager for spinner animation"""
    with console.status(f"[bold cyan]{text}...", spinner="dots") as status:
        yield status

def create_progress_bar(total, description):
    """Create a progress bar for batch processing"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    )
