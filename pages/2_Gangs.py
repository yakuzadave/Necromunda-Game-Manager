# pages/2_Gangs.py

import streamlit as st
from datetime import datetime
from pydantic import ValidationError
from common import Gang, GangFighter, save_data, load_data # Added load_data import

st.title("Gangs Management")

# Initialize session state if needed
if 'gangs' not in st.session_state:
    gangs, territories, battles = load_data()
    st.session_state.gangs = gangs
    st.session_state.territories = territories
    st.session_state.battles = battles

col1, col2 = st.columns([2, 3])

# --- Register New Gang ---
with col1:
    st.write("### Register New Gang")
    gang_name_input = st.text_input("Gang Name")
    gang_type_input = st.selectbox("Gang Type", [
        "House Orlock", "House Goliath", "House Escher",
        "House Van Saar", "House Delaque", "House Cawdor",
        "Enforcers", "Genestealer Cults", "Squat Prospectors",
        "Chaos Cults", "Corpse Grinder Cults", "Venators (Bounty Hunters)",
        "Slave Ogryns", "Ash Waste Nomads", "Outcast Gangs"
    ])
    campaign_input = st.text_input("Campaign", value="Power Play")
    credits_input = st.number_input("Starting Credits", min_value=0, value=160)
    reputation_input = st.number_input("Reputation", min_value=0, value=6)

    if st.button("Register Gang"):
        if gang_name_input:
            try:
                new_gang = Gang(
                    gang_name=gang_name_input,
                    gang_type=gang_type_input,
                    campaign=campaign_input,
                    credits=credits_input,
                    reputation=reputation_input
                )
                st.session_state.gangs.append(new_gang)
                save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                st.success(f"Registered {gang_name_input}!")
            except ValidationError as e:
                st.error(f"Error creating gang: {e}")
        else:
            st.error("Please enter a gang name.")

# --- Display Gangs & Fighter Management ---
with col2:
    st.write("### Active Gangs & Fighter Management")
    for idx, gang in enumerate(st.session_state.gangs):
        with st.expander(f"{gang.gang_name} ({gang.gang_type})"):
            st.write(f"**Credits**: {gang.credits}")
            st.write(f"**Reputation**: {gang.reputation}")
            st.write(f"**Territories**: {len(gang.territories)}")

            # Display fighters
            st.write("**Fighters:**")
            for fighter in gang.gangers:
                st.write(f"**{fighter.name}** (Type: {fighter.type})")
                if st.button(f"View Details", key=f"view_{fighter.ganger_id}"):
                    st.session_state.selected_fighter_id = fighter.ganger_id
                    st.session_state.selected_gang_id = gang.gang_id
                    st.session_state.page = "Fighter Details"
                    st.experimental_rerun()

            # Add Fighter Form
            st.write("### Add a New Fighter")
            with st.form(key=f"fighter_form_{idx}"):
                fighter_name = st.text_input("Fighter Name", key=f"name_{idx}")
                fighter_type = st.text_input("Fighter Type", key=f"type_{idx}")

                col_stats1, col_stats2 = st.columns(2)
                with col_stats1:
                    m = st.number_input("M", min_value=1, value=5, key=f"m_{idx}")
                    ws = st.number_input("WS", min_value=1, value=4, key=f"ws_{idx}")
                    bs = st.number_input("BS", min_value=1, value=3, key=f"bs_{idx}")
                    s = st.number_input("S", min_value=1, value=3, key=f"s_{idx}")
                with col_stats2:
                    t = st.number_input("T", min_value=1, value=3, key=f"t_{idx}")
                    w = st.number_input("W", min_value=1, value=1, key=f"w_{idx}")
                    i = st.number_input("I", min_value=1, value=4, key=f"i_{idx}")
                    a = st.number_input("A", min_value=1, value=1, key=f"a_{idx}")

                if st.form_submit_button("Add Fighter"):
                    if fighter_name and fighter_type:
                        try:
                            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            new_fighter = GangFighter(
                                name=fighter_name,
                                type=fighter_type,
                                m=m, ws=ws, bs=bs, s=s, t=t, w=w, i=i, a=a,
                                ld=7, cl=5, wil=6, intelligence=8,
                                cost=300, xp=0, kills=0, advance_count=0,
                                status="Alive", notes="",
                                datetime_added=now_str,
                                datetime_updated=now_str
                            )
                            gang.gangers.append(new_fighter)
                            save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                            st.success(f"Added fighter {fighter_name}!")
                        except ValidationError as e:
                            st.error(f"Error creating fighter: {e}")
                    else:
                        st.error("Provide both fighter name and fighter type.")

def run_gangs_page():
    show_gangs()

