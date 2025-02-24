
import streamlit as st
import logging
from datetime import datetime
import os
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

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
    
    # File handler for persistent logs
    file_handler = logging.FileHandler(
        f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Formatters
    rich_formatter = logging.Formatter('%(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    rich_handler.setFormatter(rich_formatter)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(rich_handler)
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger in session state
if 'logger' not in st.session_state:
    st.session_state.logger = setup_logger()

def log_debug(msg):
    st.session_state.logger.debug(msg)

def log_info(msg):
    st.session_state.logger.info(msg)

def log_warning(msg):
    st.session_state.logger.warning(msg)

def log_error(msg):
    st.session_state.logger.error(msg)
