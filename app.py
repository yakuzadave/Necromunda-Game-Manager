
import streamlit as st
import json, os
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
import uuid

# Models
class Equipment(BaseModel):
    name: str
    qty: int

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

# Set page config for the whole app
st.set_page_config(page_title="Necromunda Campaign Manager", layout="wide")

# Initialize session state with proper Gang objects
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

# Display welcome message
st.title("Welcome to the Necromunda Campaign Manager")
st.write("Use the sidebar to navigate between pages.")
