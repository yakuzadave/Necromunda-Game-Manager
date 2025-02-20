
import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Necromunda Manager", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'gangs' not in st.session_state:
    st.session_state.gangs = []
if 'territories' not in st.session_state:
    st.session_state.territories = []

# Main title with styling
st.title("⚔️ Necromunda Campaign Manager")

# Create two columns for the main layout
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("Register New Gang")
    gang_name = st.text_input("Gang Name")
    house = st.selectbox("House", [
        'Goliath', 'Escher', 'Van Saar', 'Orlock', 'Cawdor', 'Delaque',
        'Corpse Grinders', 'Palanite Enforcers', 'Other'
    ])
    credits = st.number_input("Starting Credits", 1000, 2000, 1000)
    reputation = st.number_input("Reputation", 0, 100, 0)
    
    if st.button("Register Gang"):
        if gang_name:
            new_gang = {
                'name': gang_name,
                'house': house,
                'credits': credits,
                'reputation': reputation,
                'territories': [],
                'resources': 0
            }
            st.session_state.gangs.append(new_gang)
            st.success(f"Registered {gang_name} to the campaign!")

with col2:
    st.subheader("Active Gangs")
    if st.session_state.gangs:
        for idx, gang in enumerate(st.session_state.gangs):
            with st.expander(f"{gang['name']} ({gang['house']})"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"Credits: {gang['credits']}")
                    st.write(f"Reputation: {gang['reputation']}")
                with col_b:
                    st.write(f"Territories: {len(gang['territories'])}")
                    st.write(f"Resources: {gang['resources']}")
                
                if st.button("Record Battle", key=f"battle_{idx}"):
                    gang['reputation'] += 5
                    gang['credits'] += 100
                    st.success("Battle recorded!")
                
                if st.button("Remove Gang", key=f"remove_{idx}"):
                    st.session_state.gangs.pop(idx)
                    st.rerun()
    else:
        st.info("No gangs registered yet. Register your first gang!")

# Sidebar for territory management
st.sidebar.title("Territory Control")
territory_name = st.sidebar.text_input("Territory Name")
territory_type = st.sidebar.selectbox("Territory Type", [
    'Trading Post', 'Mineral Deposits', 'Archaeotech Site', 
    'Promethium Cache', 'Water Still', 'Manufactory'
])

if st.sidebar.button("Add Territory"):
    if territory_name:
        new_territory = {
            'name': territory_name,
            'type': territory_type,
            'controlled_by': None
        }
        st.session_state.territories.append(new_territory)
        st.sidebar.success(f"Added {territory_name} to territories!")

# Campaign Statistics
if st.session_state.gangs:
    st.subheader("Campaign Statistics")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.metric("Total Gangs", len(st.session_state.gangs))
    
    with col4:
        total_credits = sum(gang['credits'] for gang in st.session_state.gangs)
        st.metric("Total Credits in Campaign", total_credits)
    
    with col5:
        top_gang = max(st.session_state.gangs, key=lambda x: x['reputation'])
        st.metric("Top Gang", f"{top_gang['name']} ({top_gang['reputation']} rep)")
