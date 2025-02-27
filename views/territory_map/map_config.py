import json
import os
from typing import Dict, Any, Optional

import streamlit as st
from utils.logger import log_error, log_info

# Constants
CONFIG_DIR = "config"
MAP_CONFIG_FILE = os.path.join(CONFIG_DIR, "map_settings.json")

# Default map configuration
DEFAULT_MAP_CONFIG = {
    # Visual settings
    "show_grid": True,
    "show_labels": True, 
    "show_faction_lines": True,
    "marker_size": 10,
    "label_size": 12,
    "map_opacity": 1.0,
    
    # Advanced visualization
    "clustering_enabled": False,
    "cluster_distance": 300,
    "show_adjacent_lines": False,
    "adjacency_threshold": 400,
    
    # Label placement
    "label_placement_strategy": "offset",
    "label_offset": 50,
    
    # Map display
    "default_map_width": 800,
    "default_map_height": 800,
    "responsive_map": True,
    
    # Territory styling
    "territory_border_width": 1,
    "territory_border_color": "white",
    "territory_opacity": 0.7,
    
    # Map controls 
    "show_measurement_tool": True,
    "show_fullscreen_control": True,
    
    # Feature toggles
    "enable_smart_label_placement": False,
    "auto_fit_new_territories": True,
    "enable_territory_clustering": False
}

def load_map_config() -> Dict[str, Any]:
    """Load map configuration from file or return defaults"""
    try:
        # Create config directory if it doesn't exist
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Check if config file exists
        if os.path.exists(MAP_CONFIG_FILE):
            with open(MAP_CONFIG_FILE, 'r') as f:
                config = json.load(f)
            log_info("Map configuration loaded successfully")
            return config
        else:
            log_info("No map configuration file found, using defaults")
            return DEFAULT_MAP_CONFIG
    except Exception as e:
        log_error(f"Error loading map configuration: {e}", exc_info=True)
        return DEFAULT_MAP_CONFIG

def save_map_config(config: Dict[str, Any]) -> bool:
    """Save map configuration to file"""
    try:
        # Create config directory if it doesn't exist
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        with open(MAP_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        log_info("Map configuration saved successfully")
        return True
    except Exception as e:
        log_error(f"Error saving map configuration: {e}", exc_info=True)
        return False

def get_map_settings() -> Dict[str, Any]:
    """Get map settings from session state or load from file"""
    if "map_config" not in st.session_state:
        st.session_state.map_config = load_map_config()
    return st.session_state.map_config

def update_map_setting(setting_name: str, value: Any) -> None:
    """Update a single map setting in session state and save to file"""
    if "map_config" not in st.session_state:
        st.session_state.map_config = load_map_config()
    
    st.session_state.map_config[setting_name] = value
    save_map_config(st.session_state.map_config)

def reset_map_config() -> None:
    """Reset map configuration to default values"""
    st.session_state.map_config = DEFAULT_MAP_CONFIG.copy()
    save_map_config(st.session_state.map_config)
    log_info("Map configuration reset to defaults")
