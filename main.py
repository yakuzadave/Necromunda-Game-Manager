import streamlit as st
import os
import json

from common import (
    DATA_FILE, FULL_CAMPAIGN_DATA_FILE,
    Equipment, GangFighter, Gang, Territory, LocalBattle,
    Member, CampaignGang, CampaignTerritory, BattleGang, Battle, Campaign,
    load_data, save_data, assign_territory, to_gang_obj, load_full_campaign
)

# Set page config **before anything else**
st.set_page_config(
    page_title="Necromunda Campaign Manager",
    page_icon="🎮",
    layout="wide"
)

# Define pages in the 'views/' directory
home_page = st.Page("views/Home.py", title="Home", icon="🏠")
dashboard_page = st.Page("views/1_Dashboard.py", title="Dashboard", icon=":material/dashboard:")
gangs_page = st.Page("views/2_Gangs.py", title="Gangs", icon=":material/group:")
territories_page = st.Page("views/3_Territories.py", title="Territories", icon=":material/map:")
battles_page = st.Page("views/4_Battles.py", title="Battles", icon=":material/swords:")
fighter_page = st.Page("views/5_FighterManagement.py", title="Fighters", icon=":material/swords:")
equipment_page = st.Page("views/7_Equipment.py", title="Equipment", icon=":material/sword_rose:")
import_yak_page = st.Page("views/8_ImportYaktribe.py", title="Import Yaktribe Data", icon=":material/cloud:")

# Optionally, if you want Rebuild Campaign in the navigation:
rebuild_page = st.Page("views/0_Rebuild_Campaign.py", title="Rebuild Campaign", icon="🔄")

# If you want Rebuild Campaign to appear in the navigation:
pages_list = [
    home_page, 
    dashboard_page, 
    gangs_page,
    fighter_page,
    territories_page, 
    battles_page, 
    equipment_page, 
    import_yak_page,
    rebuild_page
]

# If you'd rather hide Rebuild Campaign from the menu, omit `rebuild_page` from the list
# and use st.switch_page("views/0_Rebuild_Campaign.py") programmatically.

# Hidden page(s) that won't appear in the menu but can be switched to:
hidden_pages = {
    "views/FighterDetails.py"  # For example
}

# Define navigation
pg = st.navigation(pages_list)
pg.run()

# If a fighter is selected, show a button to navigate to the hidden Fighter Details page
if "selected_fighter_id" in st.session_state and "selected_gang_id" in st.session_state:
    if st.button("View Fighter Details"):
        st.switch_page("views/FighterDetails.py")

# Initialize session state for Gangs, Territories, Battles, Equipment if needed
if "gangs" not in st.session_state:
    gangs, territories, battles = load_data()
    st.session_state.gangs = gangs
    st.session_state.territories = territories
    st.session_state.battles = battles

if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []

# Quick metrics (optional)
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
