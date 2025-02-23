
import streamlit as st
import pandas as pd
import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
import uuid

# # Set page config must be the first Streamlit command
# st.set_page_config(
#     page_title="Necromunda Campaign Manager",
#     page_icon="🎮",
#     layout="wide"
# )

# Models
class Equipment(BaseModel):
    equipment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    qty: int
    cost: int = 0
    traits: str = ""

class GangFighter(BaseModel):
    ganger_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label_id: Optional[str] = ""
    name: str
    type: str
    m: int
    ws: int
    bs: int
    s: int
    t: int
    w: int
    i: int
    a: int
    ld: int
    cl: int
    wil: int
    intelligence: int = Field(..., alias="int")
    cost: int
    xp: int
    kills: int
    advance_count: int
    equipment: List[Equipment] = []
    skills: List[str] = []
    injuries: List[str] = []
    image: Optional[str] = None
    status: str
    notes: str
    datetime_added: str
    datetime_updated: str

    class Config:
        allow_population_by_field_name = True

class Gang(BaseModel):
    gang_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gang_name: str
    gang_type: str
    campaign: str = ""
    credits: int
    reputation: int
    territories: List[str] = []
    gangers: List[GangFighter] = []

# Initialize session state
if 'gangs' not in st.session_state:
    if os.path.exists('campaign_data.json'):
        with open('campaign_data.json', 'r') as f:
            data = json.load(f)
            st.session_state.gangs = [Gang(**g) for g in data.get('gangs', [])]
    else:
        st.session_state.gangs = []

if 'territories' not in st.session_state:
    st.session_state.territories = []

if 'battles' not in st.session_state:
    st.session_state.battles = []

if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []

# Display welcome message
st.title("Welcome to the Necromunda Campaign Manager")
st.write("Use the sidebar to navigate between pages.")

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
