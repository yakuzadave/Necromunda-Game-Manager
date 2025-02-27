"""
Necromunda Campaign Manager - Main Application Entry Point

This module serves as the main entry point for the Necromunda Campaign Manager 
Streamlit application.
It handles initial setup, session state management, and displays the main landing page.
"""
import streamlit as st
import os
import json
import logging
from datetime import datetime
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

# Setup logger first
if 'logger' not in st.session_state:
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
    logger = logging.getLogger('NecromundaApp')
    logger.setLevel(logging.DEBUG)
    
    rich_handler = RichHandler(console=console, rich_tracebacks=True, markup=True)
    rich_handler.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler.setLevel(logging.DEBUG)
    
    rich_formatter = logging.Formatter('%(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    rich_handler.setFormatter(rich_formatter)
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(rich_handler)
    logger.addHandler(file_handler)
    
    st.session_state.logger = logger

from common import (
    DATA_FILE, FULL_CAMPAIGN_DATA_FILE,
    Equipment, GangFighter, Gang, Territory, LocalBattle,
    Member, CampaignGang, CampaignTerritory, BattleGang, Battle, Campaign,
    load_data, save_data, assign_territory, to_gang_obj, load_full_campaign
)
from utils.logger import log_debug, log_error, log_info

# Set page config **before anything else**
st.set_page_config(
    page_title="Necromunda Campaign Manager",
    page_icon="🎮",
    layout="wide"
)

# -------------------- Define Grouped Navigation --------------------
# Create page groups as a dictionary. Each key is a section header, and its value is a list of pages.
page_groups = {
    "Overview": [
        st.Page("views/Home.py", title="Home", icon="🏠"),
        st.Page("views/1_Dashboard.py", title="Dashboard", icon="📊"),
        st.Page("views/9_GangsDataFrame.py", title="Gang Stats", icon="📈"),
    ],
    "Gang Management": [
        st.Page("views/2_Gangs.py", title="Gangs", icon="👥"),
        st.Page("views/5_FighterManagement.py", title="Fighters", icon="⚔️"),
        st.Page("views/7_Equipment.py", title="Equipment", icon="🔧"),
    ],
    "Campaign": [
        st.Page("views/3_Territories.py", title="Territories", icon="🗺️"),
        st.Page("views/4_Battles.py", title="Battles", icon="⚔️"),
        st.Page("views/6_InteractivemMap.py", title="Map", icon="🌍"),
    ],
    "Tools": [
        st.Page("views/8_ImportYaktribe.py", title="Import Yaktribe", icon="☁️"),
        st.Page("views/10_MapGenerator.py", title="Map Generator", icon="🎨"),
        st.Page("views/11_MermaidCharts.py", title="Campaign Charts", icon="📊"),
        st.Page("views/0_Rebuild_Campaign.py", title="Rebuild Campaign", icon="🔄"),
    ]
}

# Hidden page that won't appear in the menu but can be switched to
hidden_pages = {
    "Hidden": [
        st.Page("views/FighterDetails.py", title="Fighter Details", icon="🔍")
    ]
}

# Combine all pages for navigation
all_pages = page_groups.copy()
all_pages.update(hidden_pages)

# Create navigation using the combined dictionary
nav = st.navigation(all_pages)
nav.run()

# -------------------- Session State Initialization --------------------
from backup_manager import BackupManager

# Initialize backup manager
if 'backup_manager' not in st.session_state:
    st.session_state.backup_manager = BackupManager()

if "gangs" not in st.session_state:
    log_info("Initializing session state with game data")
    try:
        log_debug("Loading data from storage")
        gangs, territories, battles = load_data()
        st.session_state.gangs = gangs
        log_debug(f"Loaded {len(gangs)} gangs")
        st.session_state.territories = territories
        log_debug(f"Loaded {len(territories)} territories")
        st.session_state.battles = battles
        log_debug(f"Loaded {len(battles)} battles")
        
        log_info("Creating backup")
        st.session_state.backup_manager.create_backup()
        log_info("Initial data load and backup completed successfully")
    except Exception as e:
        log_error("Failed to initialize session state", exc_info=True)
        raise

if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []

# If a fighter is selected, show a button to navigate to the hidden Fighter Details page
if "selected_fighter_id" in st.session_state and "selected_gang_id" in st.session_state:
    if st.button("View Fighter Details"):
        st.switch_page("views/FighterDetails.py")