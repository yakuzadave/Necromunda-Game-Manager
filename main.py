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

# Define visible navigation pages
home_page = st.Page("pages/Home.py", title="Home", icon="🏠")
dashboard_page = st.Page("pages/1_Dashboard.py", title="Dashboard", icon=":material/dashboard:")
gangs_page = st.Page("pages/2_Gangs.py", title="Gangs", icon=":material/group:")
territories_page = st.Page("pages/3_Territories.py", title="Territories", icon=":material/map:")
battles_page = st.Page("pages/4_Battles.py", title="Battles", icon=":material/swords:")
equipment_page = st.Page("pages/7_Equipment.py", title="Equipment", icon=":material/sword_rose:")
import_yak_page = st.Page("pages/8_ImportYaktribe.py", title="Import Yaktribe Data", icon=":material/cloud:")
rebuild_page = st.Page("pages/Rebuild_Campaign.py", title="Rebuild Campaign", icon="🔄")

# Hidden pages (not in navigation, but accessible via st.switch_page)
hidden_pages = {
    "pages/FighterDetails.py"
}

# Navigation
pg = st.navigation([home_page, dashboard_page, gangs_page, territories_page, battles_page, equipment_page, import_yak_page])

pg.run()

# Add a button to navigate to the hidden Fighter Details page
if "selected_fighter_id" in st.session_state and "selected_gang_id" in st.session_state:
    if st.button("View Fighter Details"):
        st.switch_page("views/FighterDetails.py")


# Initialize session state
if 'gangs' not in st.session_state:
    gangs, territories, battles = load_data()
    st.session_state.gangs = gangs
    st.session_state.territories = territories
    st.session_state.battles = battles
if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []

# # Main page content
# st.title("Welcome to Necromunda Campaign Manager")
# st.markdown("""
# ## Getting Started
# Use the sidebar to navigate between different sections:
# - **Dashboard**: Overview of your campaign statistics
# - **Gangs**: Manage your gangs and fighters
# - **Territories**: Control territory distribution
# - **Battles**: Record battle outcomes
# - **Equipment**: Manage your equipment library
# - **Full Campaign Overview**: View imported campaign data
# - **Export Campaign**: Export your campaign data
# """)

# Display metrics
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