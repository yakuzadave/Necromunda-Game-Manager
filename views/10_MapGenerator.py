"""
Territory Map Generator for Necromunda Campaign Manager

This module provides a graphical interface for managing territories in Necromunda campaigns.
It includes interactive maps, territory management, map settings, statistics, and advanced features.
"""
import os
import sys
import traceback
import datetime

import streamlit as st

from common import Territory, save_data
from utils.logger import log_info, log_error, log_warning

# Import the split modules for different map functionalities
from views.territory_map.interactive_map import render_interactive_map
from views.territory_map.territory_management import render_territory_management
from views.territory_map.map_settings import render_map_settings
from views.territory_map.territory_statistics import render_territory_statistics
from views.territory_map.advanced_territory import render_advanced_territory
from views.territory_map.map_config import get_map_settings

def ensure_directories_exist():
    """Create necessary directories for map resources if they don't exist"""
    try:
        # Create static directory if it doesn't exist
        os.makedirs("static", exist_ok=True)

        # Create map_templates directory
        os.makedirs(os.path.join("static", "map_templates"), exist_ok=True)
        
        # Create config directory if it doesn't exist
        os.makedirs("config", exist_ok=True)
    except Exception as e:
        log_error(f"Error creating directories: {e}", exc_info=True)
        st.error(f"Failed to create directories: {str(e)}")

def initialize_session_state():
    """Initialize session state variables needed for the map generator"""
    if "show_distance_matrix" not in st.session_state:
        st.session_state.show_distance_matrix = False

    if "map_center" not in st.session_state:
        st.session_state.map_center = [2048, 2048]
        
    if "territories" not in st.session_state:
        log_info("No territories found in session state, initializing empty list")
        st.session_state.territories = []
    
    # Ensure map config is loaded
    if "map_config" not in st.session_state:
        st.session_state.map_config = get_map_settings()

def render_map_generator():
    """Main entry point for the Territory Map Generator view"""
    try:
        st.title("Necromunda Territory Map Generator")
        
        # Create directories and initialize session state
        ensure_directories_exist()
        initialize_session_state()

        # Define tabs for the different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Interactive Map",
            "Territory Management",
            "Map Settings",
            "Statistics",
            "Advanced"
        ])
            
        # Render each tab's content
        with tab1:
            render_interactive_map()

        with tab2:
            render_territory_management()

        with tab3:
            render_map_settings()
            
        with tab4:
            render_territory_statistics()

        with tab5:
            render_advanced_territory()
            
    except Exception as e:
        log_error(f"Error rendering map generator: {e}", exc_info=True)
        st.error("An error occurred while rendering the map generator.")
        
        # Show detailed error info in expandable section
        with st.expander("Error Details"):
            st.code(traceback.format_exc())

# If this script is run directly, display the territory map generator
if __name__ == "__main__":
    render_map_generator()