import streamlit as st
import pydeck as pdk
import random

# Set local tile server URL
TILE_URL = "http://0.0.0.0:3001/tiles/{z}/{x}/{y}.png"

# Helper function to assign coordinates if missing
def assign_coordinates_if_missing(territory, default_x_range=(-122.5, -122.3), default_y_range=(37.75, 37.8)):
    """
    If the territory doesn't have x and/or y coordinates, assign random default values.
    """
    if territory.x is None:
        territory.x = random.uniform(*default_x_range)
    if territory.y is None:
        territory.y = random.uniform(*default_y_range)
    return territory

# Initialize session state for territories if needed.
if 'territories' not in st.session_state:
    st.session_state.territories = []

# For demonstration, if there are no territories, create some mock ones.
if not st.session_state.territories:
    st.session_state.territories = [
        {"name": "Psi-Syndica Sector", "controlled_by": "Genestealer Cult", "x": -122.42, "y": 37.77},
        {"name": "Raucous Raccoon Saloon", "controlled_by": "House Goliath", "x": -122.43, "y": 37.76},
        {"name": "Trade Nexus", "controlled_by": "House Escher"}  # Missing coordinates intentionally
    ]

# Convert session state territories to PyDeck format,
# assigning coordinates if missing.
territory_data = []
for t in st.session_state.territories:
    # Ensure coordinates are assigned if missing.
    t = assign_coordinates_if_missing(t)
    territory_data.append({
        "name": t.name,
        "controlled_by": t.controlled_by if t.controlled_by else "Unclaimed",
        "coordinates": [t.x, t.y]
    })

# Create a custom PyDeck ScatterplotLayer for the territories.
territory_layer = pdk.Layer(
    "ScatterplotLayer",
    data=territory_data,
    get_position="coordinates",
    get_color="[200, 30, 0, 160]",  # Red color for territories
    get_radius=500,
    pickable=True,
    auto_highlight=True,
)

# Optionally add a custom tile layer if TILE_URL is provided.
layers = [territory_layer]
if TILE_URL.strip():
    tile_layer = pdk.Layer(
        "TileLayer",
        data=None,
        tile_size=256,
        get_tile_url=TILE_URL,
    )
    layers.insert(0, tile_layer)

# Define the initial view state.
view_state = pdk.ViewState(
    latitude=37.77,    # Center on your desired region
    longitude=-122.42,
    zoom=12,           # Adjust zoom level as needed
    pitch=30,
    bearing=0
)

# Create the deck with custom configuration
deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    tooltip={"text": "{name} - Controlled by {controlled_by}"},
    map_provider="custom",
    map_style=""
)

# Render the map in Streamlit.
st.title("Necromunda Territories")
st.pydeck_chart(deck)

# Sidebar form to add a new territory.
st.sidebar.header("Add New Territory")
new_territory_name = st.sidebar.text_input("Territory Name")
new_controlled_by = st.sidebar.text_input("Controlled By")
new_x = st.sidebar.number_input("X Coordinate", value=random.uniform(-122.5, -122.3))
new_y = st.sidebar.number_input("Y Coordinate", value=random.uniform(37.75, 37.8))

if st.sidebar.button("Add Territory"):
    if new_territory_name and new_controlled_by:
        new_territory = {
            "name": new_territory_name,
            "controlled_by": new_controlled_by,
            "x": new_x,
            "y": new_y
        }
        st.session_state.territories.append(new_territory)
        st.experimental_rerun()
    else:
        st.sidebar.error("Please enter both the territory name and the controlling faction.")
