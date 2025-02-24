import streamlit as st
import folium
from folium.raster_layers import ImageOverlay
from streamlit_folium import st_folium
import random
from common import Territory, save_data

# --------------------- Helper Function ---------------------
def assign_coordinates_if_missing(
    territory, 
    default_x_range=(0, 4096), 
    default_y_range=(0, 4096)
):
    """
    If the territory doesn't have x and/or y coordinates, assign random defaults within a 4096x4096 grid.
    This assumes your base_map is 4096 x 4096 in size, with (0,0) at the bottom-left and (4096,4096) at the top-right.
    """
    if territory.x is None:
        territory.x = random.uniform(*default_x_range)
    if territory.y is None:
        territory.y = random.uniform(*default_y_range)
    return territory

# --------------------- Initialize Territories ---------------------
st.title("Necromunda Territories - Folium with Simple CRS (4096x4096)")

# Ensure territories exist in session state.
if "territories" not in st.session_state:
    st.session_state.territories = []

# For demonstration, if no territories exist, create some sample territories.
# Coordinates here are in the 0..4096 range (x,y).
if not st.session_state.territories:
    st.session_state.territories = [
        Territory(name="Psi-Syndica Sector", type="Trading Post", controlled_by="Genestealer Cult", x=1000, y=3000),
        Territory(name="Raucous Raccoon Saloon", type="Mineral Deposits", controlled_by="House Goliath", x=2500, y=3500),
        Territory(name="Trade Nexus", type="Archaeotech Site", controlled_by="House Escher")  # Missing coordinates intentionally.
    ]

# Ensure every territory has valid coordinates within 4096x4096.
for t in st.session_state.territories:
    t = assign_coordinates_if_missing(t)

# --------------------- Static Base Image & Bounds ---------------------
# Path to your static grid image (4096x4096).
STATIC_IMAGE_PATH = "static/base_map.jpg"
# Since the image is 4096x4096, set the bounds from (0,0) to (4096,4096).
image_bounds = [[0, 0], [4096, 4096]]

# --------------------- Color Mapping (Optional) ---------------------
# Extract unique controlling factions from the territories.
factions = sorted({t.controlled_by for t in st.session_state.territories if t.controlled_by})
# Define a list of colors to cycle through.
color_list = ["red", "blue", "purple", "green", "orange", "brown"]
faction_color_mapping = {faction: color_list[i % len(color_list)] for i, faction in enumerate(factions)}
default_color = "gray"

# Prepare territory data for map markers.
territory_data = []
for t in st.session_state.territories:
    faction = t.controlled_by if t.controlled_by else "Unclaimed"
    color = faction_color_mapping.get(faction, default_color)
    territory_data.append({
        "name": t.name,
        "controlled_by": faction,
        "x": t.x,
        "y": t.y,
        "color": color
    })

# --------------------- Folium Map Setup (CRS=Simple) ---------------------
# We'll center the map near (2048, 2048) to be roughly in the middle of the 4096x4096 image.
m = folium.Map(
    location=[2048, 2048],    # [y, x] in "Simple" CRS
    zoom_start=1,            # Adjust as needed
    crs="Simple",            # This is crucial to avoid Earth-based distortion
    min_zoom=-2,             # Allows zooming out further if desired
    max_zoom=5               # Allows zooming in more if needed
)

# Add the static image overlay.
ImageOverlay(
    image=STATIC_IMAGE_PATH,
    bounds=image_bounds,  # Matches the image's pixel size
    origin="lower",       # Ensures (0,0) is bottom-left
    opacity=1,
    interactive=True,
    cross_origin=False,
    zindex=1
).add_to(m)

# Add markers for each territory.
# In CRS=Simple, Folium expects [y, x] for location (i.e., location=[territory_y, territory_x]).
for td in territory_data:
    popup_text = f"{td['name']}<br>Controlled by: {td['controlled_by']}"
    folium.CircleMarker(
        location=[td["y"], td["x"]],  # (y, x)
        radius=10,
        color=td["color"],
        fill=True,
        fill_color=td["color"],
        popup=popup_text
    ).add_to(m)

# Render the Folium map in Streamlit.
st.markdown("### Necromunda Map (4096x4096)")
st_folium(m, width=800, height=800)

# --------------------- Territory Management Interface ---------------------
st.markdown("---")
st.subheader("Territory Management")

# Form to add a new territory.
territory_name_input = st.text_input("New Territory Name", key="territory_name")
territory_type_input = st.selectbox("Territory Type", [
    "Trading Post", "Mineral Deposits", "Archaeotech Site", 
    "Promethium Cache", "Water Still", "Manufactory"
], key="territory_type")
new_controlled_by = st.text_input("Controlled By", key="new_controlled_by")

# Default random coordinates in [0..4096].
new_x = st.number_input("X Coordinate", value=random.uniform(0, 4096), key="new_x")
new_y = st.number_input("Y Coordinate", value=random.uniform(0, 4096), key="new_y")

if st.button("Add Territory"):
    if territory_name_input and new_controlled_by:
        new_territory = Territory(
            name=territory_name_input,
            type=territory_type_input,
            controlled_by=new_controlled_by,
            x=new_x,
            y=new_y
        )
        st.session_state.territories.append(new_territory)
        save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
        st.experimental_rerun()
    else:
        st.error("Please enter both the territory name and the controlling faction.")

# Display current territories.
st.markdown("---")
st.write("### Current Territories")
for territory in st.session_state.territories:
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.write(f"**{territory.name}**")
    with col2:
        st.write(f"Type: {territory.type}")
    with col3:
        status = "Controlled" if territory.controlled_by else "Unassigned"
        st.write(f"Status: {status}")

# Territory Assignment Section.
st.markdown("---")
st.write("### Assign Territory to Gang")

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
        st.success(f"Assigned {territory_to_assign} to {gang_to_assign}")
else:
    st.info("Ensure unassigned territories and registered gangs exist.")
