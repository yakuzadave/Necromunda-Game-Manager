import streamlit as st
import os
import json
from common import (
    DATA_FILE, FULL_CAMPAIGN_DATA_FILE,
    Equipment, GangFighter, Gang, Territory, LocalBattle,
    Member, CampaignGang, CampaignTerritory, BattleGang, Battle, Campaign,
    load_data, save_data, assign_territory, to_gang_obj, load_full_campaign
)


# Set page config (only once, in main.py)
st.set_page_config(
    page_title="Necromunda Campaign Manager",
    page_icon="🎮",
    layout="wide"
)

# -------------------- Session State Initialization --------------------
if 'gangs' not in st.session_state:
    gangs, territories, battles = load_data()
    st.session_state.gangs = gangs
    st.session_state.territories = territories
    st.session_state.battles = battles
if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []

# -------------------- Main Page Content --------------------
st.title("Welcome to Necromunda Campaign Manager")
st.markdown("""
## Getting Started
Use the sidebar to navigate between different sections:
- **Dashboard**: Overview of your campaign statistics
- **Gangs**: Manage your gangs and fighters
- **Territories**: Control territory distribution
- **Battles**: Record battle outcomes
- **Equipment**: Manage your equipment library
- **Full Campaign Overview**: View imported campaign data
- **Export Campaign**: Export your campaign data
""")

if st.session_state.gangs or st.session_state.territories or st.session_state.battles:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Gangs", len(st.session_state.gangs))
    with col2:
        st.metric("Total Territories", len(st.session_state.territories))
    with col3:
        st.metric("Battles Fought", len(st.session_state.battles))
else:
    st.info("Start by adding your first gang in the Gangs section!")

# -------------------- Sidebar Navigation --------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Dashboard", "Gangs", "Territories", "Battles", "Equipment", "Full Campaign Overview", "Export Campaign"
])

if st.sidebar.button("Reset Campaign"):
    st.session_state.gangs = []
    st.session_state.territories = []
    st.session_state.battles = []
    st.session_state.equipment_list = []
    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
    st.sidebar.warning("Campaign reset!")
    st.experimental_rerun()

# -------------------- Render Selected Page --------------------
# In a full multi-page app these pages would live in the 'pages/' folder.
# For now, we'll simply indicate which page the user should navigate to.
# if page == "Dashboard":
#     st.write("Go to the Dashboard page (in the pages folder).")
# elif page == "Gangs":
#     st.write("Go to the Gangs page (in the pages folder).")
# elif page == "Territories":
#     st.write("Go to the Territories page (in the pages folder).")
# elif page == "Battles":
#     st.write("Go to the Battles page (in the pages folder).")
# elif page == "Equipment":
#     st.write("Go to the Equipment page (in the pages folder).")
# elif page == "Full Campaign Overview":
#     st.write("Go to the Full Campaign Overview page (in the pages folder).")
# elif page == "Export Campaign":
#     st.write("Go to the Export Campaign page (in the pages folder).")
