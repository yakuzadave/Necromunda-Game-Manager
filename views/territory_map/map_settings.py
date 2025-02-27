import os
import random
import shutil
import streamlit as st
import numpy as np
from PIL import Image

from common import Territory, save_data
from utils.logger import log_error, log_info, log_warning
from views.territory_map.map_config import get_map_settings, save_map_config, update_map_setting, reset_map_config

def render_map_settings():
    """Render the map settings tab content"""
    st.header("Map Settings")
    
    # Get current map settings
    map_config = get_map_settings()
    
    # Create tabs for different settings categories
    settings_tab1, settings_tab2, settings_tab3, settings_tab4 = st.tabs([
        "Map Appearance", "Map Background", "Territory Generation", "Advanced Layout"
    ])
    
    with settings_tab1:
        st.subheader("Visual Settings")
        
        # Grid and label settings
        col1, col2 = st.columns(2)
        with col1:
            show_grid = st.checkbox("Show Grid Lines", value=map_config["show_grid"])
            if show_grid != map_config["show_grid"]:
                update_map_setting("show_grid", show_grid)
                
            show_labels = st.checkbox("Show Territory Labels", value=map_config["show_labels"])
            if show_labels != map_config["show_labels"]:
                update_map_setting("show_labels", show_labels)
                
            show_faction_lines = st.checkbox("Show Faction Connection Lines", value=map_config["show_faction_lines"])
            if show_faction_lines != map_config["show_faction_lines"]:
                update_map_setting("show_faction_lines", show_faction_lines)
        
        with col2:
            marker_size = st.slider("Territory Marker Size", 5, 20, map_config["marker_size"])
            if marker_size != map_config["marker_size"]:
                update_map_setting("marker_size", marker_size)
                
            label_size = st.slider("Label Size", 8, 24, map_config["label_size"]) 
            if label_size != map_config["label_size"]:
                update_map_setting("label_size", label_size)
                
            map_opacity = st.slider("Map Opacity", 0.1, 1.0, map_config["map_opacity"], 0.1)
            if map_opacity != map_config["map_opacity"]:
                update_map_setting("map_opacity", map_opacity)
        
        # Advanced visualization settings
        st.subheader("Advanced Visualization")
        col3, col4 = st.columns(2)
        
        with col3:
            clustering_enabled = st.checkbox("Enable Territory Clustering", value=map_config["clustering_enabled"])
            if clustering_enabled != map_config["clustering_enabled"]:
                update_map_setting("clustering_enabled", clustering_enabled)
                
            if clustering_enabled:
                cluster_distance = st.slider("Cluster Distance", 100, 1000, map_config["cluster_distance"], 50)
                if cluster_distance != map_config["cluster_distance"]:
                    update_map_setting("cluster_distance", cluster_distance)
        
        with col4:
            show_adjacent_lines = st.checkbox("Show Adjacent Territory Lines", value=map_config["show_adjacent_lines"])
            if show_adjacent_lines != map_config["show_adjacent_lines"]:
                update_map_setting("show_adjacent_lines", show_adjacent_lines)
                
            if show_adjacent_lines:
                adjacency_threshold = st.slider("Adjacency Threshold", 100, 1000, map_config["adjacency_threshold"], 50)
                if adjacency_threshold != map_config["adjacency_threshold"]:
                    update_map_setting("adjacency_threshold", adjacency_threshold)
        
    with settings_tab2:
        # Allow users to upload their own map image
        st.subheader("Custom Map Background")
        
        uploaded_file = st.file_uploader("Upload a custom map image (recommended size 4096x4096)", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            try:
                # Create static directory if it doesn't exist
                os.makedirs("static", exist_ok=True)
                
                # Save the uploaded file
                with open("static/base_map.jpg", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Display preview
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Map Image", width=400)
                st.success("Custom map uploaded successfully! Refresh the Interactive Map tab to see the changes.")
                log_info("Custom map image uploaded and saved")
            except Exception as e:
                log_error(f"Error saving custom map: {str(e)}", exc_info=True)
                st.error(f"Error saving custom map: {str(e)}")

        # Add map image gallery option
        st.subheader("Map Gallery")
        st.write("Select from pre-made map designs or upload your own.")
        
        # Show map templates if we create a maps directory with templates
        MAP_TEMPLATE_DIR = os.path.join("static", "map_templates")
        os.makedirs(MAP_TEMPLATE_DIR, exist_ok=True)
        
        # Check if we have any template maps
        template_files = [f for f in os.listdir(MAP_TEMPLATE_DIR) if f.endswith((".jpg", ".png"))]
        
        if template_files:
            st.write("Select a map template:")
            template_cols = st.columns(min(len(template_files), 3))
            
            for i, template_file in enumerate(template_files):
                with template_cols[i % len(template_cols)]:
                    template_path = os.path.join(MAP_TEMPLATE_DIR, template_file)
                    st.image(Image.open(template_path), caption=template_file, width=150)
                    if st.button(f"Use {template_file}", key=f"use_template_{i}"):
                        # Copy the selected template to be the main map
                        shutil.copy(template_path, os.path.join("static", "base_map.jpg"))
                        st.success(f"Map changed to {template_file}. Refresh the Interactive Map tab.")
        else:
            st.info("No map templates found. Upload some templates to the 'static/map_templates' directory.")
            
            # Allow users to upload template maps
            template_upload = st.file_uploader("Upload a map template:", type=["jpg", "jpeg", "png"])
            if template_upload is not None:
                try:
                    template_name = template_upload.name
                    template_path = os.path.join(MAP_TEMPLATE_DIR, template_name)
                    
                    with open(template_path, "wb") as f:
                        f.write(template_upload.getbuffer())
                    
                    st.success(f"Template '{template_name}' uploaded successfully!")
                except Exception as e:
                    log_error(f"Error uploading template: {e}", exc_info=True)
                    st.error(f"Error uploading template: {str(e)}")

    with settings_tab3:
        # Map generation settings
        st.subheader("Auto-Generate Territories")
        
        num_territories = st.slider("Number of Territories to Generate", 5, 50, 10)
        
        if st.button("Generate Random Territories"):
            try:
                # Define territory types
                territory_types = [
                    "Trading Post", "Mineral Deposits", "Archaeotech Site", 
                    "Promethium Cache", "Water Still", "Manufactory",
                    "Holestead", "Settlement", "Mine"
                ]
                
                # Generate unique territory names
                territory_prefixes = [
                    "Northern", "Southern", "Eastern", "Western", "Central",
                    "Upper", "Lower", "Ancient", "Ruined", "Abandoned", "Hidden",
                    "Forbidden", "Sacred", "Cursed", "Blessed", "Forgotten"
                ]
                
                territory_suffixes = [
                    "District", "Sector", "Zone", "Ruins", "Wasteland", "Outpost",
                    "Settlement", "Hub", "Market", "Nexus", "Hideout", "Enclave",
                    "Stronghold", "Dome", "Tunnels", "Caverns", "Heights"
                ]
                
                # Generate random territories
                new_territories = []
                for i in range(num_territories):
                    name = f"{random.choice(territory_prefixes)} {random.choice(territory_suffixes)} {i+1}"
                    territory_type = random.choice(territory_types)
                    
                    # Random coordinates in a grid pattern to avoid excessive overlap
                    grid_size = int(np.sqrt(num_territories)) + 1
                    cell_width = 4096 / grid_size
                    cell_height = 4096 / grid_size
                    
                    grid_x = i % grid_size
                    grid_y = i // grid_size
                    
                    x = grid_x * cell_width + random.uniform(0, cell_width)
                    y = grid_y * cell_height + random.uniform(0, cell_height)
                    
                    new_territory = Territory(
                        name=name,
                        type=territory_type,
                        controlled_by=None,  # Start uncontrolled
                        x=x,
                        y=y
                    )
                    new_territories.append(new_territory)
                
                # Add to existing territories
                st.session_state.territories.extend(new_territories)
                save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                log_info(f"Generated {num_territories} random territories")
                st.success(f"Generated {num_territories} random territories. View them in the Interactive Map tab.")
            except Exception as e:
                log_error(f"Error generating territories: {str(e)}", exc_info=True)
                st.error(f"Error generating territories: {str(e)}")
                
    with settings_tab4:
        st.subheader("Advanced Layout Options")
        
        # Label placement settings
        st.write("Label Placement Strategy")
        label_placement = st.radio(
            "How should territory labels be positioned?",
            options=["Simple Offset", "Radial", "Smart Placement"],
            index=0,  # Default to simple offset
            horizontal=True,
            help="Simple Offset places labels above territories. Radial places labels around territories. Smart Placement tries to avoid overlaps."
        )
        
        # Map the user-friendly names to the internal strategies
        strategy_mapping = {
            "Simple Offset": "offset",
            "Radial": "radial", 
            "Smart Placement": "smart"
        }
        
        selected_strategy = strategy_mapping[label_placement]
        if selected_strategy != map_config.get("label_placement_strategy", "offset"):
            update_map_setting("label_placement_strategy", selected_strategy)
        
        # Label offset setting
        label_offset = st.slider(
            "Label Offset Distance", 
            min_value=20,
            max_value=100, 
            value=map_config.get("label_offset", 50),
            help="Distance between territory marker and its label"
        )
        
        if label_offset != map_config.get("label_offset", 50):
            update_map_setting("label_offset", label_offset)
            
        # Territory styling options
        st.subheader("Territory Styling")
        
        col_style1, col_style2 = st.columns(2)
        
        with col_style1:
            territory_opacity = st.slider(
                "Territory Opacity",
                min_value=0.3,
                max_value=1.0,
                value=map_config.get("territory_opacity", 0.7),
                step=0.1,
                help="Opacity of territory markers"
            )
            
            if territory_opacity != map_config.get("territory_opacity", 0.7):
                update_map_setting("territory_opacity", territory_opacity)
        
        with col_style2:
            border_width = st.slider(
                "Territory Border Width",
                min_value=0,
                max_value=5,
                value=map_config.get("territory_border_width", 1),
                help="Width of the border around territory markers"
            )
            
            if border_width != map_config.get("territory_border_width", 1):
                update_map_setting("territory_border_width", border_width)
        
        # Add viewport settings
        st.subheader("Viewport Settings")
        
        auto_fit = st.checkbox(
            "Auto-fit Map on New Territory Creation", 
            value=map_config.get("auto_fit_new_territories", True),
            help="When enabled, the map will automatically center on newly created territories"
        )
        
        if auto_fit != map_config.get("auto_fit_new_territories", True):
            update_map_setting("auto_fit_new_territories", auto_fit)
        
        # Label placement strategy settings
        st.subheader("Label Placement Strategy")
        
        placement_options = {
            "Simple Offset": "offset",
            "Radial": "radial",
            "Smart Placement": "smart"
        }
        
        current_strategy = map_config.get("label_placement_strategy", "offset")
        current_option = next(
            (k for k, v in placement_options.items() if v == current_strategy), 
            "Simple Offset"
        )
        
        selected_option = st.radio(
            "Label Placement",
            options=list(placement_options.keys()),
            index=list(placement_options.keys()).index(current_option),
            help="Choose how labels are positioned relative to territory markers",
            horizontal=True
        )
        
        if placement_options[selected_option] != current_strategy:
            update_map_setting("label_placement_strategy", placement_options[selected_option])
        
        # Sample visualization of label placement strategies
        st.caption("Label placement strategies:")
        placement_examples = {
            "Simple Offset": "↑ Labels are placed directly above territory markers",
            "Radial": "○ Labels are placed in a circle around territory markers",
            "Smart Placement": "⚙️ Labels are placed to minimize overlapping"
        }
        
        for option, description in placement_examples.items():
            if option == selected_option:
                st.info(f"**{description}**")
