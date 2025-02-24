
import streamlit as st
import logging
from datetime import datetime
import os
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
import inspect
import traceback

def setup_logger():
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure custom theme
    custom_theme = Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "red",
        "debug": "grey70"
    })
    
    console = Console(theme=custom_theme)
    
    # Configure logger
    logger = logging.getLogger('NecromundaApp')
    logger.setLevel(logging.DEBUG)
    
    # Rich handler for console output
    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        markup=True
    )
    rich_handler.setLevel(logging.INFO)
    
    # File handler for persistent logs with detailed formatting
    file_handler = logging.FileHandler(
        f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Formatters
    rich_formatter = logging.Formatter('%(message)s')
    file_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(module)s:%(lineno)d - %(message)s')
    
    rich_handler.setFormatter(rich_formatter)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(rich_handler)
    logger.addHandler(file_handler)
    
    return logger

def get_caller_info():
    """Get information about the calling function"""
    stack = inspect.stack()
    caller = stack[2]  # Index 2 gets the caller of our logging function
    return f"{caller.filename}:{caller.lineno} in {caller.function}"

# Initialize logger in session state
if 'logger' not in st.session_state:
    st.session_state.logger = setup_logger()

def log_debug(msg):
    caller = get_caller_info()
    st.session_state.logger.debug(f"{caller} - {msg}")

def log_info(msg):
    caller = get_caller_info()
    st.session_state.logger.info(f"{caller} - {msg}")

def log_warning(msg):
    caller = get_caller_info()
    st.session_state.logger.warning(f"{caller} - {msg}")

def log_error(msg, exc_info=None):
    caller = get_caller_info()
    if exc_info:
        st.session_state.logger.error(f"{caller} - {msg}\n{traceback.format_exc()}", exc_info=True)
    else:
        st.session_state.logger.error(f"{caller} - {msg}")

def log_function_call(func):
    """Decorator to log function entry and exit"""
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        log_debug(f"Entering function {func_name}")
        try:
            result = func(*args, **kwargs)
            log_debug(f"Exiting function {func_name}")
            return result
        except Exception as e:
            log_error(f"Error in function {func_name}: {str(e)}", exc_info=True)
            raise
    return wrapper
