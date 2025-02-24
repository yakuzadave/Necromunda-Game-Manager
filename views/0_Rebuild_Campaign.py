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

st.title("🔄 Rebuild & Save Campaign Data")

st.write("Use the buttons below to either reload all campaign data from the JSON files or save the current session data back to disk.")

# Ensure directories exist
for directory in [GANGS_DIR, TERRITORIES_DIR, BATTLES_DIR, EQUIPMENT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# -------------------- Loading Functions --------------------
def load_json_files(directory, model_class):
    objects = []
    for file_path in directory.glob("*.json"):
        try:
            data = json.loads(file_path.read_text())
            objects.append(model_class(**data))
        except Exception as e:
            st.error(f"⚠️ Error loading {file_path.name}: {e}")
    return objects

# -------------------- Saving Functions --------------------
def save_all_data():
    # Save gangs individually
    for gang in st.session_state.gangs:
        file_path = GANGS_DIR / f"{gang.gang_id}.json"
        with open(file_path, "w") as f:
            json.dump(gang.dict(), f, indent=4)
    # Save territories individually
    for territory in st.session_state.territories:
        # Here, using territory name as filename; ensure names are unique or consider adding an ID.
        file_path = TERRITORIES_DIR / f"{territory.name}.json"
        with open(file_path, "w") as f:
            json.dump(territory.dict(), f, indent=4)
    # Save battles individually
    for battle in st.session_state.battles:
        file_path = BATTLES_DIR / f"{battle.battle_id}.json"
        with open(file_path, "w") as f:
            json.dump(battle.dict(), f, indent=4)
    # Save equipment individually
    for eq in st.session_state.equipment_list:
        file_path = EQUIPMENT_DIR / f"{eq.equipment_id}.json"
        with open(file_path, "w") as f:
            json.dump(eq.dict(), f, indent=4)

# -------------------- Buttons --------------------
# Button to reload campaign data from JSON files into session state
if st.button("🔄 Rebuild Campaign Data"):
    log_info("Starting campaign data rebuild")
    try:
        st.session_state.gangs = load_json_files(GANGS_DIR, Gang)
        log_debug(f"Loaded {len(st.session_state.gangs)} gangs")
        st.session_state.territories = load_json_files(TERRITORIES_DIR, Territory)
        log_debug(f"Loaded {len(st.session_state.territories)} territories")
        st.session_state.battles = load_json_files(BATTLES_DIR, LocalBattle)
        log_debug(f"Loaded {len(st.session_state.battles)} battles")
        st.session_state.equipment_list = load_json_files(EQUIPMENT_DIR, Equipment)
        log_debug(f"Loaded {len(st.session_state.equipment_list)} equipment items")
        log_info("Campaign data rebuild completed successfully")
        st.success("✅ Campaign data successfully reloaded!")
    except Exception as e:
        log_error("Failed to rebuild campaign data", exc_info=True)
        st.error("Failed to rebuild campaign data")

# Button to save current session data into the respective JSON files
if st.button("💾 Save Campaign Data"):
    save_all_data()
    st.success("✅ Campaign data successfully saved!")

# -------------------- Display Campaign Statistics --------------------
st.markdown("---")
st.write("### 📊 Current Campaign Data Summary")

st.metric("Total Gangs", len(st.session_state.get("gangs", [])))
st.metric("Total Territories", len(st.session_state.get("territories", [])))
st.metric("Total Battles", len(st.session_state.get("battles", [])))
st.metric("Total Equipment Items", len(st.session_state.get("equipment_list", [])))

# Option to clear session state
if st.button("🗑️ Clear Session State"):
    st.session_state.clear()
    st.success("✅ Session state cleared! Reload campaign data to continue.")
