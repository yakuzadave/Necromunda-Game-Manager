import os
import datetime
import tempfile
import math  # Added for zoom calculation
import folium
import folium.plugins
import pandas as pd
import streamlit as st
from folium.raster_layers import ImageOverlay
from streamlit_folium import st_folium

from common import Territory
from utils.logger import log_debug, log_error, log_info, log_warning
from utils.map_utils import (
    calculate_distance,
    calculate_territory_adjacency,
    cluster_territories,
    generate_distinct_colors,
    generate_placeholder_map,
    get_random_coordinates,
)
from views.territory_map.map_config import get_map_settings
from views.territory_map.label_placement import optimize_label_placement

def fit_map_to_territories(territories, padding=0.1):
    """
    Calculate bounds to fit all territories in view
    
    Args:
        territories: List of territories to include in the view
        padding: Extra padding as a percentage of the total size
    
    Returns:
        tuple: (center coordinates [y, x], zoom level)
    """
    if not territories:
        return [2048, 2048], 1  # Default center and zoom if no territories
    
    # Extract valid coordinates
    valid_coords = [(t.y, t.x) for t in territories if t.x is not None and t.y is not None]
    
    if not valid_coords:
        return [2048, 2048], 1
    
    # Find bounds
    min_y = min(coord[0] for coord in valid_coords)
    max_y = max(coord[0] for coord in valid_coords)
    min_x = min(coord[1] for coord in valid_coords)
    max_x = max(coord[1] for coord in valid_coords)
    
    # Add padding
    y_padding = (max_y - min_y) * padding
    x_padding = (max_x - min_x) * padding
    
    # Calculate center
    center_y = (min_y + max_y) / 2
    center_x = (min_x + max_x) / 2
    
    # Calculate zoom level (approximate)
    y_diff = max_y - min_y + 2 * y_padding
    x_diff = max_x - min_x + 2 * x_padding
    max_diff = max(y_diff, x_diff)
    
    # A simple formula to estimate the zoom level
    if max_diff <= 0:
        zoom_level = 1
    else:
        zoom_level = max(0, min(5, 5 - math.log(max_diff / 1000, 2)))
    
    return [center_y, center_x], zoom_level

def render_interactive_map():
    """Render the interactive map tab content"""
    st.header("Interactive Necromunda Map")
    
    # Get map configuration
    map_config = get_map_settings()
    
    # Add search functionality to find territories
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_query = st.text_input("🔍 Search territories", "")
    with search_col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing for alignment
        if st.button("Clear", key="clear_search"):
            search_query = ""
            
    # Filter territories based on search
    if search_query:
        search_results = [
            t for t in st.session_state.territories 
            if search_query.lower() in t.name.lower() or 
               (t.controlled_by and search_query.lower() in t.controlled_by.lower()) or
               search_query.lower() in t.type.lower()
        ]
        
        if search_results:
            st.success(f"Found {len(search_results)} matching territories")
            # Allow jumping to a territory
            selected_territory = st.selectbox(
                "Jump to territory", 
                options=[t.name for t in search_results],
                format_func=lambda x: f"{x} ({next((t.type for t in search_results if t.name == x), '')})"
            )
            
            if selected_territory and st.button("Center on Selected"):
                territory = next((t for t in search_results if t.name == selected_territory), None)
                if territory and territory.x is not None and territory.y is not None:
                    st.session_state.map_center = [territory.y, territory.x]
                    st.session_state.last_clicked_x = territory.x
                    st.session_state.last_clicked_y = territory.y
                    st.rerun()
        else:
            st.warning(f"No territories found matching '{search_query}'")
    
    # Ensure territories exist in session state
    if "territories" not in st.session_state:
        st.session_state.territories = []
        
        # For demonstration, if no territories exist, create some sample territories
        if not st.session_state.territories:
            log_info("No territories found, creating sample territories")
            st.session_state.territories = [
                Territory(
                    name="Psi-Syndica Sector",
                    type="Trading Post",
                    controlled_by="Genestealer Cult",
                    x=1000,
                    y=3000
                ),
                Territory(
                    name="Raucous Raccoon Saloon",
                    type="Mineral Deposits",
                    controlled_by="House Goliath",
                    x=2500,
                    y=3500
                ),
                Territory(
                    name="Trade Nexus",
                    type="Archaeotech Site",
                    controlled_by="House Escher",
                    x=1500,
                    y=2000
                )
            ]

    # Ensure every territory has valid coordinates
    for i, t in enumerate(st.session_state.territories):
        if t.x is None or t.y is None:
            # Generate coordinates using the cacheable function
            x, y = get_random_coordinates(seed=f"{t.name}_{i}")
            
            # Update territory with new coordinates
            territory_dict = {
                "name": t.name,
                "type": t.type,
                "controlled_by": t.controlled_by,
                "x": t.x if t.x is not None else x,
                "y": t.y if t.y is not None else y,
                "lat": t.lat,
                "lng": t.lng,
                "elevation": t.elevation
            }
            
            # Replace the territory in the list with updated version
            st.session_state.territories[i] = Territory(**territory_dict)

    # Add territory filtering
    filter_expander = st.expander("Territory Filters", expanded=False)
    with filter_expander:
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            # Get unique territory types and factions for filtering
            territory_types = sorted(set(t.type for t in st.session_state.territories))
            selected_types = st.multiselect(
                "Filter by Territory Type",
                options=territory_types,
                default=[]
            )
        
        with col_filter2:
            factions = sorted(set(t.controlled_by for t in st.session_state.territories 
                            if t.controlled_by))
            selected_factions = st.multiselect(
                "Filter by Faction",
                options=["Unclaimed"] + factions,
                default=[]
            )
        
        with col_filter3:
            show_all = st.checkbox("Show All Territories", value=True)
            
            # Add a button to fit map to all territories
            if st.button("Fit Map to All Territories"):
                center, zoom = fit_map_to_territories(st.session_state.territories)
                st.session_state.map_center = center
                st.session_state.map_zoom = zoom
                st.rerun()
        
    # Filter territories based on selections
    filtered_territories = st.session_state.territories
    if not show_all:
        if selected_types:
            filtered_territories = [t for t in filtered_territories if t.type in selected_types]
        if selected_factions:
            filtered_territories = [
                t for t in filtered_territories 
                if (t.controlled_by in selected_factions) or 
                   (not t.controlled_by and "Unclaimed" in selected_factions)
            ]

    # --------------------- Static Base Image & Bounds ---------------------
    # Path to static grid image
    STATIC_IMAGE_PATH = os.path.join("static", "base_map.jpg")
    image_bounds = [[0, 0], [4096, 4096]]

    # Check if the image file exists, if not, generate a placeholder
    if os.path.exists(STATIC_IMAGE_PATH):
        base_map_image = STATIC_IMAGE_PATH
    else:
        st.warning(f"Base map image not found at {STATIC_IMAGE_PATH}. Using generated grid instead.")
        log_warning(f"Base map image not found at {STATIC_IMAGE_PATH}")
        base_map_image = generate_placeholder_map()

    # --------------------- Map Controls ---------------------
    map_controls_col1, map_controls_col2 = st.columns([2, 1])
    
    with map_controls_col1:
        view_options = st.expander("Map View Options", expanded=False)
        with view_options:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                show_grid = st.checkbox("Show Grid Lines", value=map_config["show_grid"])
                show_labels = st.checkbox("Show Territory Labels", value=map_config["show_labels"])
                show_faction_lines = st.checkbox(
                    "Show Faction Connection Lines", value=map_config["show_faction_lines"]
                )
                
            with col2:
                marker_size = st.slider("Territory Marker Size", 5, 20, map_config["marker_size"])
                label_size = st.slider("Label Size", 8, 24, map_config["label_size"])
                map_opacity = st.slider("Map Opacity", 0.1, 1.0, map_config["map_opacity"], 0.1)
                
            with col3:
                clustering_enabled = st.checkbox("Enable Clustering", value=map_config["clustering_enabled"])
                if clustering_enabled:
                    cluster_distance = st.slider("Cluster Distance", 100, 1000, map_config["cluster_distance"])
                else:
                    cluster_distance = map_config["cluster_distance"]
                    
                show_adjacent_lines = st.checkbox("Show Adjacent Territories", value=map_config["show_adjacent_lines"])
                if show_adjacent_lines:
                    adjacency_threshold = st.slider("Adjacency Threshold", 100, 1000, map_config["adjacency_threshold"])
                else:
                    adjacency_threshold = map_config["adjacency_threshold"]
            
            # Add viewport fitting options
            st.subheader("Viewport Controls")
            viewport_col1, viewport_col2 = st.columns(2)
            
            with viewport_col1:
                if st.button("Fit to All Territories"):
                    center, zoom = fit_map_to_territories(st.session_state.territories)
                    st.session_state.map_center = center
                    st.session_state.map_zoom = zoom
                    st.rerun()
                    
                if filtered_territories and st.button("Fit to Filtered Territories"):
                    center, zoom = fit_map_to_territories(filtered_territories)
                    st.session_state.map_center = center
                    st.session_state.map_zoom = zoom
                    st.rerun()
            
            with viewport_col2:
                auto_fit = st.checkbox("Auto-fit on Territory Creation", 
                                       value=st.session_state.get("auto_fit_new_territories", False))
                if auto_fit != st.session_state.get("auto_fit_new_territories", False):
                    st.session_state.auto_fit_new_territories = auto_fit
    
    with map_controls_col2:
        st.caption("Map Controls")
        # Add buttons for common map operations
        map_actions_col1, map_actions_col2 = st.columns(2)
        
        with map_actions_col1:
            if st.button("📏 Reset Zoom"):
                st.session_state.map_zoom = 1
                st.rerun()
            
            if st.button("📸 Export Map"):
                st.session_state.show_export_dialog = True
                st.rerun()
                
        with map_actions_col2:
            if st.button("🔄 Recenter Map"):
                st.session_state.map_center = [2048, 2048]
                st.rerun()
            
            if st.button("🗺️ Distance Matrix"):
                st.session_state.show_distance_matrix = True
                st.rerun()

    # --------------------- Color Mapping ---------------------
    faction_color_mapping = {}
    try:
        # Extract unique controlling factions from the territories
        factions = sorted(set(t.controlled_by for t in st.session_state.territories if t.controlled_by))
        
        # Use our improved color generation function
        color_list = generate_distinct_colors(len(factions))
        
        default_color = "gray"
        faction_color_mapping = {faction: color_list[i] for i, faction in enumerate(factions)}

        # Prepare territory data for map markers
        territory_data = []
        for t in st.session_state.territories:
            faction = t.controlled_by if t.controlled_by else "Unclaimed"
            color = faction_color_mapping.get(faction, default_color)
            territory_data.append({
                "name": t.name,
                "type": t.type,
                "controlled_by": faction,
                "x": t.x,
                "y": t.y,
                "color": color
            })
    except Exception as e:
        log_error(f"Error preparing territory data: {e}", exc_info=True)
        st.error(f"Error preparing territory data: {str(e)}")
        territory_data = []
        default_color = "gray"  # Ensure default_color is defined even in case of an error

    # Apply territory filtering to territory_data
    if not show_all and territory_data:
        territory_data = [td for td in territory_data 
                        if any(t.name == td["name"] for t in filtered_territories)]

    # --------------------- Folium Map Setup ---------------------
    try:
        # Use the zoom level from session state if available, otherwise default to 1
        zoom_start = st.session_state.get("map_zoom", 1)
        
        m = folium.Map(
            location=st.session_state.map_center,
            zoom_start=zoom_start,
            crs="Simple",
            min_zoom=-2,
            max_zoom=5
        )

        # Add the static image overlay or generated placeholder
        ImageOverlay(
            image=base_map_image,
            bounds=image_bounds,
            origin="lower",
            opacity=map_opacity,  # Use the slider value
            interactive=True,
            cross_origin=False,
            zindex=1
        ).add_to(m)

        # Add grid lines conditionally
        if show_grid:
            grid_step = 512  # Grid cell size
            for x in range(0, 4096, grid_step):
                folium.PolyLine(
                    locations=[[0, x], [4096, x]],
                    color="lightgray",
                    weight=1,
                    opacity=0.5,
                    dash_array="5,5"
                ).add_to(m)
                
                folium.PolyLine(
                    locations=[[x, 0], [x, 4096]],
                    color="lightgray",
                    weight=1,
                    opacity=0.5,
                    dash_array="5,5"
                ).add_to(m)

        # Add legend to map
        legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; 
                        border:2px solid grey; z-index:9999; 
                        background-color:white;
                        padding:10px;
                        border-radius:5px;
                        font-size:14px;">
            <p style="margin-bottom:5px; font-weight:bold;">Territory Control</p>
        '''
        
        # Add each faction to the legend
        for faction, color in faction_color_mapping.items():
            legend_html += f'''
                <div>
                <span style="background-color:{color}; 
                            border-radius:50%;
                            display:inline-block;
                            height:10px;
                            width:10px;
                            margin-right:5px;"></span>
                {faction}
                </div>
            '''
        
        # Add unclaimed territories to legend
        legend_html += f'''
            <div>
            <span style="background-color:{default_color}; 
                        border-radius:50%;
                        display:inline-block;
                        height:10px;
                        width:10px;
                        margin-right:5px;"></span>
            Unclaimed
            </div>
        '''
        
        legend_html += '</div>'
        m.get_root().add_child(folium.Element(legend_html))

        # Add scale bar (approximate since we're using Simple CRS)
        scale_html = '''
            <div style="position: fixed; 
                        bottom: 50px; right: 50px; 
                        border:2px solid grey; z-index:9999; 
                        background-color:white;
                        padding:10px;
                        border-radius:5px;
                        font-size:14px;">
            <p style="margin:0; font-weight:bold;">Scale (approx)</p>
            <div style="display: flex; align-items: center;">
                <div style="height: 5px; width: 100px; background-color: black; margin-right: 5px;"></div>
                <span>1000 units</span>
            </div>
            </div>
        '''
        m.get_root().add_child(folium.Element(scale_html))

        # Add markers for each territory
        for td in territory_data:
            popup_text = f"<b>{td['name']}</b><br>Type: {td['type']}<br>Controlled by: {td['controlled_by']}"
            folium.CircleMarker(
                location=[td["y"], td["x"]],
                radius=marker_size,  # Use the slider value
                color=td["color"],
                fill=True,
                fill_color=td["color"],
                fill_opacity=0.7,
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(m)

            # Add territory name as a label if enabled
            if show_labels:
                folium.Marker(
                    location=[td["y"] + 50, td["x"]],  # Offset the label slightly
                    icon=folium.DivIcon(
                        icon_size=(150, 36),
                        icon_anchor=(75, 0),
                        html=f'<div style="font-size: {label_size}pt; color: black; text-shadow: 1px 1px white;">{td["name"]}</div>'
                    )
                ).add_to(m)

        # Add lines between territories controlled by the same faction if enabled
        if show_faction_lines:
            faction_territories = {}
            for td in territory_data:
                faction = td["controlled_by"]
                if faction != "Unclaimed":
                    if faction not in faction_territories:
                        faction_territories[faction] = []
                    faction_territories[faction].append((td["y"], td["x"]))
            
            for faction, coords in faction_territories.items():
                if len(coords) > 1:
                    folium.PolyLine(
                        locations=coords,
                        color=faction_color_mapping.get(faction, default_color),
                        weight=2,
                        opacity=0.7,
                        dash_array='5, 10'
                    ).add_to(m)

        # If clustering is enabled, show territory clusters
        if clustering_enabled and filtered_territories:
            clusters = cluster_territories(filtered_territories, cluster_distance)
            
            # Draw cluster boundaries
            for cluster_index, cluster in enumerate(clusters):
                if len(cluster) > 1:  # Only draw clusters with more than one territory
                    # Get coordinates for cluster
                    cluster_points = [(t.y, t.x) for t in cluster if t.x is not None and t.y is not None]
                    
                    # Calculate a convex hull or simpler boundary
                    if len(cluster_points) >= 3:  # Need at least 3 points for a polygon
                        # Draw a polygon around the cluster with some padding
                        folium.Polygon(
                            locations=cluster_points,
                            color='gray',
                            weight=2,
                            fill=True,
                            fill_color='gray',
                            fill_opacity=0.1,
                            popup=f"Cluster {cluster_index+1} - {len(cluster)} territories"
                        ).add_to(m)

        # If adjacency lines are enabled, show connections between nearby territories
        if show_adjacent_lines:
            adjacency = calculate_territory_adjacency(
                filtered_territories, adjacency_threshold
            )
            
            # Draw lines between adjacent territories
            for territory_name, adjacent_list in adjacency.items():
                # Find the source territory
                source_territory = next((t for t in filtered_territories if t.name == territory_name), None)
                if not source_territory or not source_territory.x or not source_territory.y:
                    continue
                
                for adj in adjacent_list:
                    # Find the target territory
                    target_territory = next((t for t in filtered_territories if t.name == adj["name"]), None)
                    if not target_territory or not target_territory.x or not target_territory.y:
                        continue
                    
                    # Draw a line between the territories
                    folium.PolyLine(
                        locations=[(source_territory.y, source_territory.x), 
                                  (target_territory.y, target_territory.x)],
                        color='gray',
                        weight=1,
                        opacity=0.4,
                        dash_array='3,3',
                        tooltip=f"Distance: {adj['distance']:.1f} units"
                    ).add_to(m)

        # Add a measurement tool
        try:
            measure = folium.plugins.MeasureControl(
                position='topright',
                primary_length_unit='pixels',
                secondary_length_unit='',
                primary_area_unit='sqmeters'
            )
            m.add_child(measure)
        except Exception as e:
            log_warning(f"Could not add measurement tool: {e}")

        # Render the Folium map in Streamlit with responsive sizing
        map_container = st.container()
        with map_container:
            # Allow users to select map size
            map_size_options = {
                "Small (600x600)": 600,
                "Medium (800x800)": 800,
                "Large (1000x800)": 1000
            }
            
            # Add a column layout to position the map size selector
            size_col1, size_col2 = st.columns([4, 1])
            with size_col2:
                selected_size_label = st.selectbox(
                    "Map Size",
                    options=list(map_size_options.keys()),
                    index=1  # Default to medium
                )
                selected_size = map_size_options[selected_size_label]
            
            with size_col1:
                # Use the selected width for the map
                st_data = st_folium(m, width=selected_size, height=min(selected_size, 800))
        
        # Store current zoom level
        if st_data and "zoom" in st_data:
            st.session_state.map_zoom = st_data["zoom"]
        
        # Handle map click events to capture coordinates
        if st_data and st_data.get("last_clicked"):
            st.session_state.last_clicked_y = st_data["last_clicked"]["lat"]
            st.session_state.last_clicked_x = st_data["last_clicked"]["lng"]
            st.success(f"Selected coordinates: X={st.session_state.last_clicked_x:.1f}, Y={st.session_state.last_clicked_y:.1f}")
            
            # Show nearest territory to clicked point
            nearest_territory = None
            min_distance = float('inf')
            for t in st.session_state.territories:
                if t.x is not None and t.y is not None:
                    distance = calculate_distance(
                        st.session_state.last_clicked_x, 
                        st.session_state.last_clicked_y,
                        t.x, t.y
                    )
                    if distance < min_distance:
                        min_distance = distance
                        nearest_territory = t
            
            if nearest_territory and min_distance < 500:  # Only show if reasonably close
                st.info(f"Nearest territory: {nearest_territory.name} ({min_distance:.1f} units away)")
                if st.button("Center Map on This Territory"):
                    # This will need a rerun to update the map center
                    st.session_state.map_center = [nearest_territory.y, nearest_territory.x]
                    st.rerun()
                
        # Add a new feature: shortest path calculation between territories
        path_calc = st.expander("Calculate Path Between Territories", expanded=False)
        with path_calc:
            col_path1, col_path2 = st.columns(2)
            with col_path1:
                source_territory = st.selectbox(
                    "From Territory",
                    options=[t.name for t in st.session_state.territories],
                    key="source_territory"
                )
            with col_path2:
                target_territory = st.selectbox(
                    "To Territory",
                    options=[t.name for t in st.session_state.territories],
                    key="target_territory" 
                )
                
            if st.button("Calculate Distance", key="calc_distance_btn"):
                source = next((t for t in st.session_state.territories if t.name == source_territory), None)
                target = next((t for t in st.session_state.territories if t.name == target_territory), None)
                
                if source and target and source.x and source.y and target.x and target.y:
                    dist = calculate_distance(source.x, source.y, target.x, target.y)
                    st.success(f"Distance from {source.name} to {target.name}: {dist:.1f} units")
                    
                    # Draw a line showing the path
                    folium.PolyLine(
                        locations=[(source.y, source.x), (target.y, target.x)],
                        color='red',
                        weight=3,
                        opacity=0.7,
                        tooltip=f"Path: {dist:.1f} units"
                    ).add_to(m)
                    
                    # Update the map
                    st_folium(m, width=800, height=800)
                else:
                    st.error("Could not calculate distance - coordinates unavailable")
                
    except Exception as e:
        log_error(f"Error rendering map: {e}", exc_info=True)
        st.error("There was an error rendering the map. Please ensure all required libraries are installed.")
        st.error(f"Error details: {str(e)}")

    # Add map export dialog
    if st.session_state.get("show_export_dialog", False):
        with st.form("export_map_form"):
            st.subheader("Export Map")
            
            export_col1, export_col2 = st.columns(2)
            
            with export_col1:
                export_width = st.number_input("Width", min_value=600, max_value=2000, value=1200)
                include_legend = st.checkbox("Include Legend", value=True)
                
            with export_col2:
                export_height = st.number_input("Height", min_value=600, max_value=2000, value=1200)
                include_grid = st.checkbox("Include Grid", value=True)
            
            export_submitted = st.form_submit_button("Export Map")
            
            if export_submitted:
                try:
                    # Configure the export map with selected options
                    export_map = folium.Map(
                        location=st.session_state.map_center,
                        zoom_start=st.session_state.get("map_zoom", 1),
                        crs="Simple",
                        min_zoom=-2,
                        max_zoom=5,
                        width=export_width,
                        height=export_height
                    )
                    
                    # Add the static image overlay
                    ImageOverlay(
                        image=base_map_image,
                        bounds=image_bounds,
                        origin="lower",
                        opacity=map_opacity,
                        interactive=True,
                        cross_origin=False,
                        zindex=1
                    ).add_to(export_map)
                    
                    # Add grid conditionally
                    if include_grid:
                        grid_step = 512  # Grid cell size
                        for x in range(0, 4096, grid_step):
                            folium.PolyLine(
                                locations=[[0, x], [4096, x]],
                                color="lightgray",
                                weight=1,
                                opacity=0.5,
                                dash_array="5,5"
                            ).add_to(export_map)
                            
                            folium.PolyLine(
                                locations=[[x, 0], [x, 4096]],
                                color="lightgray",
                                weight=1,
                                opacity=0.5,
                                dash_array="5,5"
                            ).add_to(export_map)
                    
                    # Add territories
                    for td in territory_data:
                        popup_text = f"<b>{td['name']}</b><br>Type: {td['type']}<br>Controlled by: {td['controlled_by']}"
                        folium.CircleMarker(
                            location=[td["y"], td["x"]],
                            radius=marker_size,
                            color=td["color"],
                            fill=True,
                            fill_color=td["color"],
                            fill_opacity=0.7,
                            popup=folium.Popup(popup_text, max_width=300)
                        ).add_to(export_map)
                        
                        # Add labels
                        if show_labels:
                            folium.Marker(
                                location=[td["y"] + 50, td["x"]],
                                icon=folium.DivIcon(
                                    icon_size=(150, 36),
                                    icon_anchor=(75, 0),
                                    html=f'<div style="font-size: {label_size}pt; color: black; text-shadow: 1px 1px white;">{td["name"]}</div>'
                                )
                            ).add_to(export_map)
                    
                    # Add legend
                    if include_legend:
                        legend_html = '''
                            <div style="position: fixed; 
                                        bottom: 50px; left: 50px; 
                                        border:2px solid grey; z-index:9999; 
                                        background-color:white;
                                        padding:10px;
                                        border-radius:5px;
                                        font-size:14px;">
                            <p style="margin-bottom:5px; font-weight:bold;">Territory Control</p>
                        '''
                        
                        for faction, color in faction_color_mapping.items():
                            legend_html += f'''
                                <div>
                                <span style="background-color:{color}; 
                                            border-radius:50%;
                                            display:inline-block;
                                            height:10px;
                                            width:10px;
                                            margin-right:5px;"></span>
                                {faction}
                                </div>
                            '''
                        
                        legend_html += f'''
                            <div>
                            <span style="background-color:{default_color}; 
                                        border-radius:50%;
                                        display:inline-block;
                                        height:10px;
                                        width:10px;
                                        margin-right:5px;"></span>
                            Unclaimed
                            </div>
                        '''
                        
                        legend_html += '</div>'
                        export_map.get_root().add_child(folium.Element(legend_html))
                    
                    # Create HTML for export
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmpfile:
                        html_content = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Necromunda Map Export</title>
                            <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
                        </head>
                        <body>
                            <div id="map" style="width:{export_width}px;height:{export_height}px">{export_map.get_root().render()}</div>
                            <script>
                                window.onload = function() {{
                                    html2canvas(document.getElementById('map')).then(function(canvas) {{
                                        var link = document.createElement('a');
                                        link.download = 'necromunda_map_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png';
                                        link.href = canvas.toDataURL();
                                        link.click();
                                    }});
                                }};
                            </script>
                        </body>
                        </html>
                        """
                        tmpfile.write(html_content.encode('utf-8'))
                    
                    st.success("Map export prepared! The download should start automatically.")
                    # Hide the export dialog after export
                    st.session_state.show_export_dialog = False
                    
                except Exception as e:
                    log_error(f"Error exporting map: {e}", exc_info=True)
                    st.error(f"Error exporting map: {str(e)}")
        
        # Add a cancel button for the export dialog
        if st.button("Cancel Export"):
            st.session_state.show_export_dialog = False
            st.rerun()

    # Show distance matrix if requested
    if st.session_state.get("show_distance_matrix", False):
        st.subheader("Territory Distance Matrix")
        
        # Create a matrix of distances between territories
        territories = [t for t in st.session_state.territories if t.x is not None and t.y is not None]
        
        if territories:
            # Create the distance DataFrame
            territory_names = [t.name for t in territories]
            distance_matrix = []
            
            for t1 in territories:
                row = []
                for t2 in territories:
                    if t1.name == t2.name:
                        row.append(0)
                    else:
                        row.append(round(calculate_distance(t1.x, t1.y, t2.x, t2.y), 1))
                distance_matrix.append(row)
                
            df_distances = pd.DataFrame(distance_matrix, index=territory_names, columns=territory_names)
            
            # Allow filtering to show only specific territories in the matrix
            if len(territories) > 10:
                selected_territories = st.multiselect(
                    "Select territories to show in matrix",
                    options=territory_names,
                    default=territory_names[:10],
                    help="Select specific territories to include in the distance matrix"
                )
                
                if selected_territories:
                    df_filtered = df_distances.loc[selected_territories, selected_territories]
                    st.dataframe(df_filtered, use_container_width=True)
                else:
                    st.info("Select at least one territory to show the matrix")
            else:
                st.dataframe(df_distances, use_container_width=True)
                
            # Option to hide the matrix
            if st.button("Hide Distance Matrix"):
                st.session_state.show_distance_matrix = False
                st.rerun()
        else:
            st.warning("No territories with valid coordinates found")
    
    # Update label placement with smart positioning
    territory_data_with_labels = territory_data.copy()
    
    if show_labels:
        # Get label positioning strategy from config
        label_strategy = map_config.get("label_placement_strategy", "offset")
        label_offset = map_config.get("label_offset", 50)
        
        # Generate list of territory positions for collision detection
        territory_positions = [(td["y"], td["x"], td["name"]) for td in territory_data]
        
        # Apply smart label placement to territory data
        try:
            from views.territory_map.label_placement import optimize_label_placement
            territory_data_with_labels = optimize_label_placement(territory_data, label_strategy)
        except Exception as e:
            log_warning(f"Smart label placement failed: {e}")
            territory_data_with_labels = territory_data
    
    # Update the label rendering code in the map setup section
    if show_labels:
        for td in territory_data_with_labels:
            # Use optimized label position if available, otherwise use default offset
            label_y = td.get("label_y", td["y"] + label_offset)
            label_x = td.get("label_x", td["x"])
            
            folium.Marker(
                location=[label_y, label_x],
                icon=folium.DivIcon(
                    icon_size=(150, 36),
                    icon_anchor=(75, 0),
                    html=f'<div style="font-size: {label_size}pt; color: black; text-shadow: 1px 1px white; text-align: center;">{td["name"]}</div>'
                )
            ).add_to(m)
    
    # When a new territory is created or viewed, check if we should auto-fit
    if st.session_state.get("auto_fit_new_territories", False) and st.session_state.get("new_territory_created", False):
        # Get the newly created territory
        new_territory = st.session_state.territories[-1]
        
        # Center on the new territory
        if new_territory.x is not None and new_territory.y is not None:
            st.session_state.map_center = [new_territory.y, new_territory.x]
            st.session_state.map_zoom = 2  # Medium zoom level for new territory
        
        # Reset the flag
        st.session_state.new_territory_created = False
