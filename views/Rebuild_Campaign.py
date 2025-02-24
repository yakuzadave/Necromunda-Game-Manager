import streamlit as st
import os
import json
from pathlib import Path
from common import Gang, Territory, LocalBattle, Equipment  # Import models

# Define data directories
DATA_DIR = Path("data")
GANGS_DIR = DATA_DIR / "gangs"
TERRITORIES_DIR = DATA_DIR / "territories"
BATTLES_DIR = DATA_DIR / "battles"
EQUIPMENT_DIR = DATA_DIR / "equipment"

st.title("🔄 Rebuild Campaign Data")

st.write("Reload all gangs, territories, battles, and equipment from individual JSON files.")

# Ensure directories exist
for directory in [GANGS_DIR, TERRITORIES_DIR, BATTLES_DIR, EQUIPMENT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Function to load JSON data from files
def load_json_files(directory, model_class):
    objects = []
    for file_path in directory.glob("*.json"):
        try:
            data = json.loads(file_path.read_text())
            objects.append(model_class(**data))
        except Exception as e:
            st.error(f"⚠️ Error loading {file_path.name}: {e}")
    return objects

# Button to rebuild campaign data
if st.button("🔄 Rebuild Campaign Data"):
    st.session_state.gangs = load_json_files(GANGS_DIR, Gang)
    st.session_state.territories = load_json_files(TERRITORIES_DIR, Territory)
    st.session_state.battles = load_json_files(BATTLES_DIR, LocalBattle)
    st.session_state.equipment_list = load_json_files(EQUIPMENT_DIR, Equipment)
    st.success("✅ Campaign data successfully reloaded!")


# Display campaign statistics
st.markdown("---")
st.write("### 📊 Current Campaign Data Summary")

st.metric("Total Gangs", len(st.session_state.get("gangs", [])))
st.metric("Total Territories", len(st.session_state.get("territories", [])))
st.metric("Total Battles", len(st.session_state.get("battles", [])))
st.metric("Total Equipment Items", len(st.session_state.get("equipment_list", [])))

# Clear session state button
if st.button("🗑️ Clear Session State"):
    st.session_state.clear()
    st.success("✅ Session state cleared! Reload campaign data to continue.")
