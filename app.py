import streamlit as st
import os
import json
from common import (
    DATA_FILE, Gang, load_data
)

# # Set page config (this must be the very first Streamlit command)
# st.set_page_config(
#     page_title="Necromunda Campaign Manager",
#     page_icon="🎮",
#     layout="wide"
# )

# -------------------- Session State Initialization --------------------
if 'gangs' not in st.session_state:
    gangs, territories, battles = load_data()
    st.session_state.gangs = gangs
    st.session_state.territories = territories
    st.session_state.battles = battles

if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []


