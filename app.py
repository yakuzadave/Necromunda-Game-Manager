import streamlit as st
import os
import json
from common import (
    DATA_FILE, Gang, load_data
)

# Set page config (this must be the very first Streamlit command)
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

# Display quick metrics if data exists
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
