import streamlit as st
import json, os
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
import uuid

# Set page config for the whole app
st.set_page_config(page_title="Necromunda Campaign Manager", layout="wide")

# You can also initialize common session state here if needed.
if 'gangs' not in st.session_state:
    st.session_state.gangs = []   # List of local Gang objects
if 'territories' not in st.session_state:
    st.session_state.territories = []   # List of Territory objects
if 'battles' not in st.session_state:
    st.session_state.battles = []  # List of LocalBattle objects

# Optionally, display a welcome message.
st.title("Welcome to the Necromunda Campaign Manager")
st.write("Use the sidebar to navigate between pages.")
