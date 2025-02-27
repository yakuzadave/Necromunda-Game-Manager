import streamlit as st
import folium
from folium.raster_layers import ImageOverlay
from streamlit_folium import st_folium
import random
import os
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from io import BytesIO
import base64
from common import Territory, save_data
from utils.logger import log_info, log_error, log_debug, log_warning  # Added missing log_warning

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

st.title("Necromunda Territory Map Generator")

# --------------------- Helper Functions ---------------------
@st.cache_data
def assign_coordinates_if_missing(
    territory, 
    default_x_range=(0, 4096), 
    default_y_range=(0, 4096)
):
    """
    If the territory doesn't have x and/or y coordinates, assign random defaults within a grid.
    This function is cached to ensure consistent coordinates between reruns.
    """
    if territory.x is None:
        territory.x = random.uniform(*default_x_range)
    if territory.y is None:
        territory.y = random.uniform(*default_y_range)
    return territory

@st.cache_data
def generate_placeholder_map(width=4096, height=4096):
    """
    Generate a placeholder grid map when no base map is available.
    This is cached to avoid regenerating the image on every rerun.
    """
    try:
        # Create a blank white image
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw a grid
        grid_spacing = 512
        
        # Draw vertical lines
        for x in range(0, width, grid_spacing):
            draw.line([(x, 0), (x, height)], fill=(200, 200, 200), width=2)
        
        # Draw horizontal lines
        for y in range(0, height, grid_spacing):
            draw.line([(0, y), (width, y)], fill=(200, 200, 200), width=2)
        
        # Draw a border
        draw.rectangle([0, 0, width-1, height-1], outline=(0, 0, 0), width=5)
        
        # Add title text
        draw.text((width//2-150, height//2), "Necromunda Territory Map", fill=(0, 0, 0))
        draw.text((width//2-130, height//2+30), "Generated Grid", fill=(0, 0, 0))
        
        # Convert to bytes for folium
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        log_error(f"Error generating placeholder map: {e}", exc_info=True)
        # Return a fallback minimal image if there's an error
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAIAAAB7GkOtAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5QcJEAolVPdz6wAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAABFklEQVR42u3BMQEAAADCoPVPbQlPoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADgYtJQAAE49thhAAAAAElFTkSuQmCC"

# --------------------- Define color generator function ---------------------
@st.cache_data
def generate_distinct_colors(n):
    """Generate visually distinct colors for territories"""
    color_list = [
        "#e6194B", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", 
        "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990", "#dcbeff",
        "#9A6324", "#800000", "#aaffc3", "#808000", "#000075", "#a9a9a9",
        "#FF00FF", "#2F4F4F", "#FF8C00", "#00CED1", "#8A2BE2", "#00FF7F"
    ]
    # If we need more colors than in our predefined list, generate them
    if n > len(color_list):
        import colorsys
        for i in range(n - len(color_list)):
            # Generate HSV colors with good separation
            h = i / n
            s = 0.7 + (i % 3) * 0.1  # Vary saturation slightly
            v = 0.8 + (i % 2) * 0.1  # Vary brightness slightly
            # Convert to RGB and then to hex
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            color_list.append(f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}")
    return color_list[:n]

# --------------------- Calculate Map Statistics ---------------------
@st.cache_data
def calculate_territory_stats(territories):
    """Calculate statistics about territory control and distribution"""
    stats = {
        "total": len(territories),
        "claimed": 0,
        "unclaimed": 0,
        "faction_counts": {},
        "type_counts": {}
    }
    
    for t in territories:
        # Count by control status
        if t.controlled_by:
            stats["claimed"] += 1
            # Count by faction
            if t.controlled_by not in stats["faction_counts"]:
                stats["faction_counts"][t.controlled_by] = 0
            stats["faction_counts"][t.controlled_by] += 1
        else:
            stats["unclaimed"] += 1
        
        # Count by territory type
        if t.type not in stats["type_counts"]:
            stats["type_counts"][t.type] = 0
        stats["type_counts"][t.type] += 1
    
    return stats

# --------------------- Calculate Distance Between Points ---------------------
def calculate_distance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points"""
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# --------------------- Initialize Territories ---------------------
tab1, tab2, tab3, tab4 = st.tabs(["Interactive Map", "Territory Management", "Map Settings", "Statistics"])

with tab1:
    st.header("Interactive Necromunda Map")
    
    # Ensure territories exist in session state
    if "territories" not in st.session_state:
        st.session_state.territories = []

    # For demonstration, if no territories exist, create some sample territories
    if not st.session_state.territories:
        log_info("No territories found, creating sample territories")
        st.session_state.territories = [
            Territory(name="Psi-Syndica Sector", type="Trading Post", controlled_by="Genestealer Cult", x=1000, y=3000),
            Territory(name="Raucous Raccoon Saloon", type="Mineral Deposits", controlled_by="House Goliath", x=2500, y=3500),
            Territory(name="Trade Nexus", type="Archaeotech Site", controlled_by="House Escher")  # Missing coordinates intentionally
        ]

    # Ensure every territory has valid coordinates
    for t in st.session_state.territories:
        t = assign_coordinates_if_missing(t)

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
    with st.expander("Map Controls", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            show_grid = st.checkbox("Show Grid Lines", value=True)
            show_labels = st.checkbox("Show Territory Labels", value=True)
            show_faction_lines = st.checkbox("Show Faction Connection Lines", value=True)
            
        with col2:
            marker_size = st.slider("Territory Marker Size", 5, 20, 10)
            label_size = st.slider("Label Size", 8, 24, 12)
            map_opacity = st.slider("Map Opacity", 0.1, 1.0, 1.0, 0.1)

    # --------------------- Color Mapping ---------------------
    try:
        # Extract unique controlling factions from the territories
        factions = sorted(set(t.controlled_by for t in st.session_state.territories if t.controlled_by))
        
        # Use our improved color generation function
        color_list = generate_distinct_colors(len(factions))
        
        faction_color_mapping = {faction: color_list[i] for i, faction in enumerate(factions)}
        default_color = "gray"

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

    # --------------------- Folium Map Setup ---------------------
    try:
        m = folium.Map(
            location=[2048, 2048],
            zoom_start=1,
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
        m.get_root().html.add_child(folium.Element(legend_html))

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
        m.get_root().html.add_child(folium.Element(scale_html))

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

        # Add a measurement tool
        measure = folium.plugins.MeasureControl(
            position='topright',
            primary_length_unit='pixels',
            secondary_length_unit=None,
            primary_area_unit=None
        )
        m.add_child(measure)

        # Render the Folium map in Streamlit
        st_data = st_folium(m, width=800, height=800)
        
        # Handle map click events to capture coordinates
        if st_data and st_data.get("last_clicked"):
            st.session_state.last_clicked_y = st_data["last_clicked"]["lat"]
            st.session_state.last_clicked_x = st_data["last_clicked"]["lng"]
            st.success(f"Selected coordinates: X={st.session_state.last_clicked_x:.1f}, Y={st.session_state.last_clicked_y:.1f}")
            
            # Show nearest territory to clicked point
            nearest_territory = None
            min_distance = float('inf')
            for t in st.session_state.territories:
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
                    st.experimental_rerun()
                
    except Exception as e:
        log_error(f"Error rendering map: {e}", exc_info=True)
        st.error("There was an error rendering the map. Please ensure all required libraries are installed.")
        st.error(f"Error details: {str(e)}")

with tab2:
    st.header("Territory Management")
    
    # --------------------- Territory Management Interface ---------------------
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add New Territory")
        
        territory_name_input = st.text_input("New Territory Name", key="territory_name")
        territory_type_input = st.selectbox("Territory Type", [
            "Trading Post", "Mineral Deposits", "Archaeotech Site", 
            "Promethium Cache", "Water Still", "Manufactory",
            "Holestead", "Settlement", "Mine"
        ], key="territory_type")
        
        # Get existing gang names from session state for dropdown
        gang_options = ["Unclaimed"] + [gang.gang_name for gang in st.session_state.get("gangs", [])]
        new_controlled_by = st.selectbox("Controlled By", gang_options, key="new_controlled_by")
        
        # Use clicked coordinates if available, otherwise use random coordinates
        x_val = st.session_state.get("last_clicked_x", random.uniform(0, 4096))
        y_val = st.session_state.get("last_clicked_y", random.uniform(0, 4096))
        
        new_x = st.number_input("X Coordinate", value=float(x_val), key="new_x")
        new_y = st.number_input("Y Coordinate", value=float(y_val), key="new_y")
        
        if st.button("Add Territory"):
            if territory_name_input:
                # Handle "Unclaimed" selection
                controller = None if new_controlled_by == "Unclaimed" else new_controlled_by
                
                new_territory = Territory(
                    name=territory_name_input,
                    type=territory_type_input,
                    controlled_by=controller,
                    x=new_x,
                    y=new_y
                )
                st.session_state.territories.append(new_territory)
                save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                log_info(f"Added new territory: {territory_name_input}")
                st.success(f"Added territory: {territory_name_input}")
                st.session_state.last_clicked_x = None
                st.session_state.last_clicked_y = None
                st.experimental_rerun()
            else:
                st.error("Please enter a territory name.")
    
    with col2:
        st.subheader("Territory Assignment")
        
        # Territory Assignment Section
        unassigned_territories = [t.name for t in st.session_state.territories if not t.controlled_by]
        gang_names = [g.gang_name for g in st.session_state.gangs] if "gangs" in st.session_state else []
        
        if unassigned_territories and gang_names:
            territory_to_assign = st.selectbox("Select Territory", unassigned_territories, key="assign_territory")
            gang_to_assign = st.selectbox("Select Gang", gang_names, key="assign_gang")
            
            if st.button("Assign Territory"):
                for territory in st.session_state.territories:
                    if territory.name == territory_to_assign:
                        territory.controlled_by = gang_to_assign
                        break
                for gang in st.session_state.gangs:
                    if gang.gang_name == gang_to_assign and territory_to_assign not in gang.territories:
                        gang.territories.append(territory_to_assign)
                        break
                save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                log_info(f"Assigned {territory_to_assign} to {gang_to_assign}")
                st.success(f"Assigned {territory_to_assign} to {gang_to_assign}")
                st.experimental_rerun()
        else:
            st.info("Ensure unassigned territories and registered gangs exist.")
    
    # Display current territories with edit/delete options
    st.subheader("Current Territories")
    territory_df = pd.DataFrame([{
        "Name": t.name,
        "Type": t.type,
        "Controlled By": t.controlled_by if t.controlled_by else "Unclaimed",
        "X": t.x,
        "Y": t.y
    } for t in st.session_state.territories])
    
    edited_df = st.data_editor(
        territory_df,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        column_config={
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Type": st.column_config.SelectboxColumn(
                "Type",
                options=[
                    "Trading Post", "Mineral Deposits", "Archaeotech Site", 
                    "Promethium Cache", "Water Still", "Manufactory",
                    "Holestead", "Settlement", "Mine"
                ],
                width="medium"
            ),
            "Controlled By": st.column_config.TextColumn("Controlled By", width="medium"),
            "X": st.column_config.NumberColumn("X", format="%.1f", width="small"),
            "Y": st.column_config.NumberColumn("Y", format="%.1f", width="small")
        }
    )
    
    # Apply changes from the editor
    if not edited_df.equals(territory_df):
        try:
            # Update territories in session state
            updated_territories = []
            for _, row in edited_df.iterrows():
                territory = Territory(
                    name=row["Name"],
                    type=row["Type"],
                    controlled_by=None if row["Controlled By"] == "Unclaimed" else row["Controlled By"],
                    x=float(row["X"]),
                    y=float(row["Y"])
                )
                updated_territories.append(territory)
            
            st.session_state.territories = updated_territories
            save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
            log_info("Updated territories from data editor")
            st.success("Territory data updated")
        except Exception as e:
            log_error(f"Error updating territories: {str(e)}", exc_info=True)
            st.error(f"Error updating territories: {str(e)}")

    # Add an "Export Territories" button to allow users to download territory data
    st.subheader("Export/Import Territory Data")
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        if st.button("Export Territories as CSV"):
            try:
                # Create a dataframe with the territory data
                export_data = []
                for t in st.session_state.territories:
                    export_data.append({
                        "Name": t.name,
                        "Type": t.type,
                        "Controlled By": t.controlled_by if t.controlled_by else "",
                        "X": t.x,
                        "Y": t.y,
                        "Lat": t.lat,
                        "Lng": t.lng,
                        "Elevation": t.elevation
                    })
                
                if export_data:
                    df = pd.DataFrame(export_data)
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name="necromunda_territories.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No territories to export")
            except Exception as e:
                log_error(f"Error exporting territories: {e}", exc_info=True)
                st.error(f"Error exporting territories: {str(e)}")
    
    with col_exp2:
        # Add an "Import Territories from CSV" option
        uploaded_csv = st.file_uploader("Import territories from CSV", type=["csv"])
        if uploaded_csv is not None:
            try:
                df = pd.read_csv(uploaded_csv)
                if st.button("Process Imported Territories"):
                    # Convert DataFrame back to Territory objects
                    imported_territories = []
                    for _, row in df.iterrows():
                        # Handle null values
                        controlled_by = row.get("Controlled By", None)
                        if pd.isna(controlled_by):
                            controlled_by = None
                        
                        x = row.get("X", None)
                        if pd.isna(x):
                            x = None
                            
                        y = row.get("Y", None)
                        if pd.isna(y):
                            y = None
                            
                        lat = row.get("Lat", None)
                        if pd.isna(lat):
                            lat = None
                            
                        lng = row.get("Lng", None)
                        if pd.isna(lng):
                            lng = None
                            
                        elevation = row.get("Elevation", None)
                        if pd.isna(elevation):
                            elevation = None
                        
                        territory = Territory(
                            name=row["Name"],
                            type=row["Type"],
                            controlled_by=controlled_by,
                            x=x,
                            y=y,
                            lat=lat,
                            lng=lng,
                            elevation=elevation
                        )
                        imported_territories.append(territory)
                    
                    # Update session state with imported territories
                    st.session_state.territories = imported_territories
                    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                    log_info(f"Imported {len(imported_territories)} territories")
                    st.success(f"Imported {len(imported_territories)} territories")
                    st.experimental_rerun()
            except Exception as e:
                log_error(f"Error importing territories: {e}", exc_info=True)
                st.error(f"Error importing territories: {str(e)}")

# --------------------- Map Settings Tab ---------------------
with tab3:
    st.header("Map Settings")
    
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

# --------------------- Statistics Tab ---------------------
with tab4:
    st.header("Territory Statistics")
    
    # Calculate and display statistics
    try:
        territory_stats = calculate_territory_stats(st.session_state.territories)
        
        # Display overall counts
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Territories", territory_stats["total"])
        with col2:
            st.metric("Claimed Territories", territory_stats["claimed"])
        with col3:
            st.metric("Unclaimed Territories", territory_stats["unclaimed"])
        
        # Display faction control chart
        if territory_stats["faction_counts"]:
            st.subheader("Territory Control by Faction")
            faction_df = pd.DataFrame({
                "Faction": list(territory_stats["faction_counts"].keys()),
                "Territories": list(territory_stats["faction_counts"].values())
            })
            st.bar_chart(faction_df.set_index("Faction"))
        
        # Display territory types chart
        if territory_stats["type_counts"]:
            st.subheader("Territory Types")
            type_df = pd.DataFrame({
                "Type": list(territory_stats["type_counts"].keys()),
                "Count": list(territory_stats["type_counts"].values())
            })
            st.bar_chart(type_df.set_index("Type"))
            
        # Display territory density heatmap
        st.subheader("Territory Density Map")
        
        # Create a 2D histogram for territory locations
        if len(st.session_state.territories) > 1:
            x_coords = [t.x for t in st.session_state.territories if t.x is not None]
            y_coords = [t.y for t in st.session_state.territories if t.y is not None]
            
            if x_coords and y_coords:
                # Create grid for heatmap
                x_bins = np.linspace(0, 4096, 20)
                y_bins = np.linspace(0, 4096, 20)
                
                heatmap_data, _, _ = np.histogram2d(x_coords, y_coords, bins=[x_bins, y_bins])
                
                # Display the heatmap
                st.write("Areas with more territories appear darker:")
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.imshow(heatmap_data.T, origin='lower', extent=[0, 4096, 0, 4096], 
                          cmap='viridis', interpolation='gaussian')
                ax.set_xlabel("X Coordinate")
                ax.set_ylabel("Y Coordinate")
                ax.set_title("Territory Density Heatmap")
                st.pyplot(fig)
        else:
            st.info("Need at least 2 territories with coordinates to generate a density map.")
    
    except Exception as e:
        log_error(f"Error generating statistics: {e}", exc_info=True)
        st.error(f"Error generating statistics: {str(e)}")
```
