import streamlit as st
import os
import json
from common import (
    DATA_FILE, FULL_CAMPAIGN_DATA_FILE,
    Equipment, GangFighter, Gang, Territory, LocalBattle,
    Member, CampaignGang, CampaignTerritory, BattleGang, Battle, Campaign,
    load_data, save_data, assign_territory, to_gang_obj, load_full_campaign
)

# Set page config
st.set_page_config(
    page_title="Necromunda Campaign Manager",
    page_icon="🎮",
    layout="wide"
)

# Initialize session state
if 'gangs' not in st.session_state:
    gangs, territories, battles = load_data()
    st.session_state.gangs = gangs
    st.session_state.territories = territories
    st.session_state.battles = battles
if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []

# Main page content
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