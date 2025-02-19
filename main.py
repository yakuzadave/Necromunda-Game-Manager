
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_chat import message

# Page configuration
st.set_page_config(page_title="Tabletop Manager", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'games' not in st.session_state:
    st.session_state.games = []
if 'players' not in st.session_state:
    st.session_state.players = []

# Main title with styling
st.title("🎲 Tabletop Manager")

# Create two columns for the main layout
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("Add New Game")
    game_name = st.text_input("Game Name")
    game_type = st.selectbox("Game Type", ['Board Game', 'Card Game', 'RPG'])
    min_players = st.number_input("Minimum Players", 1, 10, 2)
    max_players = st.number_input("Maximum Players", min_players, 10, 4)
    game_duration = st.slider("Estimated Duration (minutes)", 15, 240, 60)
    
    if st.button("Add Game"):
        if game_name:
            new_game = {
                'name': game_name,
                'type': game_type,
                'min_players': min_players,
                'max_players': max_players,
                'duration': game_duration
            }
            st.session_state.games.append(new_game)
            st.success(f"Added {game_name} to the collection!")

with col2:
    st.subheader("Game Collection")
    if st.session_state.games:
        for idx, game in enumerate(st.session_state.games):
            with st.expander(f"{game['name']} ({game['type']})"):
                st.write(f"Players: {game['min_players']} - {game['max_players']}")
                st.write(f"Duration: {game['duration']} minutes")
                if st.button("Remove Game", key=f"remove_{idx}"):
                    st.session_state.games.pop(idx)
                    st.rerun()
    else:
        st.info("No games added yet. Add your first game!")

# Sidebar for player management
st.sidebar.title("Player Management")
player_name = st.sidebar.text_input("Player Name")
if st.sidebar.button("Add Player"):
    if player_name and player_name not in st.session_state.players:
        st.session_state.players.append(player_name)
        st.sidebar.success(f"Added {player_name} to players list!")

st.sidebar.subheader("Current Players")
for player in st.session_state.players:
    st.sidebar.write(f"• {player}")

# Game Statistics
if st.session_state.games:
    st.subheader("Collection Statistics")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.metric("Total Games", len(st.session_state.games))
    
    with col4:
        game_types = [game['type'] for game in st.session_state.games]
        most_common = max(set(game_types), key=game_types.count)
        st.metric("Most Common Type", most_common)
    
    with col5:
        avg_duration = sum(game['duration'] for game in st.session_state.games) / len(st.session_state.games)
        st.metric("Average Duration", f"{int(avg_duration)} min")

