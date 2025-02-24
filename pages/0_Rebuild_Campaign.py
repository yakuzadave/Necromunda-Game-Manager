import streamlit as st
import os
import json
from pathlib import Path
from common import Gang, Territory, LocalBattle, Equipment  # Import models

# Define the data directories
DATA_DIR = "data"
GANGS_DIR = os.path.join(DATA_DIR, "gangs")
TERRITORIES_DIR = os.path.join(DATA_DIR, "territories")
BATTLES_DIR = os.path.join(DATA_DIR, "battles")
EQUIPMENT_DIR = os.path.join(DATA_DIR, "equipment")

st.title("🔄 Rebuild Campaign Data")

st.write("This page will reload all gangs, territories, battles, and equipment from individual JSON files.")

# Ensure directories exist
for directory in [GANGS_DIR, TERRITORIES_DIR, BATTLES_DIR, EQUIPMENT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Function to load all gangs
def load_gangs():
    gangs = []
    for file_path in Path(GANGS_DIR).glob("*.json"):
        with open(file_path, "r") as f:
            try:
                gang_data = json.load(f)
                gangs.append(Gang(**gang_data))
            except Exception as e:
                st.error(f"⚠️ Error loading {file_path.name}: {e}")
    return gangs

# Function to load all territories
def load_territories():
    territories = []
    for file_path in Path(TERRITORIES_DIR).glob("*.json"):
        with open(file_path, "r") as f:
            try:
                territory_data = json.load(f)
                territories.append(Territory(**territory_data))
            except Exception as e:
                st.error(f"⚠️ Error loading {file_path.name}: {e}")
    return territories

# Function to load all battles
def load_battles():
    battles = []
    for file_path in Path(BATTLES_DIR).glob("*.json"):
        with open(file_path, "r") as f:
            try:
                battle_data = json.load(f)
                battles.append(LocalBattle(**battle_data))
            except Exception as e:
                st.error(f"⚠️ Error loading {file_path.name}: {e}")
    return battles

# Function to load all equipment
def load_equipment():
    equipment_list = []
    for file_path in Path(EQUIPMENT_DIR).glob("*.json"):
        with open(file_path, "r") as f:
            try:
                equipment_data = json.load(f)
                equipment_list.append(Equipment(**equipment_data))
            except Exception as e:
                st.error(f"⚠️ Error loading {file_path.name}: {e}")
    return equipment_list

# Button to reload session state
if st.button("🔄 Rebuild Campaign Data"):
    st.session_state.gangs = load_gangs()
    st.session_state.territories = load_territories()
    st.session_state.battles = load_battles()
    st.session_state.equipment_list = load_equipment()
    st.success("✅ Campaign data successfully reloaded!")

# Display campaign statistics
st.markdown("---")
st.write("### 📊 Current Campaign Data Summary")

if "gangs" in st.session_state:
    st.metric("Total Gangs", len(st.session_state.gangs))
else:
    st.warning("⚠️ No gangs loaded.")

if "territories" in st.session_state:
    st.metric("Total Territories", len(st.session_state.territories))
else:
    st.warning("⚠️ No territories loaded.")

if "battles" in st.session_state:
    st.metric("Total Battles", len(st.session_state.battles))
else:
    st.warning("⚠️ No battles loaded.")

if "equipment_list" in st.session_state:
    st.metric("Total Equipment Items", len(st.session_state.equipment_list))
else:
    st.warning("⚠️ No equipment loaded.")

# Option to clear session state
if st.button("🗑️ Clear Session State"):
    st.session_state.clear()
    st.success("✅ Session state cleared! Reload campaign data to continue.")
