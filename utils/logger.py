
import streamlit as st
import logging
from datetime import datetime
import os

def setup_logger():
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger('NecromundaApp')
    logger.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler.setLevel(logging.DEBUG)
    
    # Stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
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
