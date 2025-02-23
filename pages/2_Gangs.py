import streamlit as st
from datetime import datetime
import uuid
from pydantic import ValidationError

# For brevity, we assume the Gang and GangFighter models have been defined in app.py
# You could also import them from a shared module, e.g.: 
# from common import Gang, GangFighter, save_data

def show_gangs():
    st.subheader("Gangs")
    col1, col2 = st.columns([2, 3])

    with col1:
        st.write("### Register New Gang")
        gang_name_input = st.text_input("Gang Name")
        gang_type_input = st.selectbox("Gang Type", [
            "House Orlock",
            "House Goliath",
            "House Escher",
            "House Van Saar",
            "House Delaque",
            "House Cawdor",
            "Enforcers",
            "Genestealer Cults",
            "Squat Prospectors",
            "Chaos Cults",
            "Corpse Grinder Cults",
            "Venators (Bounty Hunters)",
            "Slave Ogryns",
            "Ash Waste Nomads",
            "Outcast Gangs"
        ])
        campaign_input = st.text_input("Campaign", value="Power Play")
        credits_input = st.number_input("Starting Credits", min_value=0, value=160)
        reputation_input = st.number_input("Reputation", min_value=0, value=6)
        if st.button("Register Gang"):
            if gang_name_input:
                try:
                    new_gang = st.session_state.gangs[0].__class__(
                        gang_name=gang_name_input,
                        gang_type=gang_type_input,
                        campaign=campaign_input,
                        credits=credits_input,
                        reputation=reputation_input
                    )
                    st.session_state.gangs.append(new_gang)
                    st.success(f"Registered {gang_name_input}!")
                except ValidationError as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please enter a gang name.")

    with col2:
        st.write("### Active Gangs & Fighter Management")
        if st.session_state.gangs:
            for idx, gang in enumerate(st.session_state.gangs):
                with st.expander(f"{gang.gang_name} ({gang.gang_type})"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"Credits: {gang.credits}")
                        st.write(f"Reputation: {gang.reputation}")
                    with col_b:
                        st.write(f"Territories: {len(gang.territories)}")
                    # Display fighters
                    st.write("**Fighters:**")
                    if hasattr(gang, "gangers") and gang.gangers:
                        for fighter in gang.gangers:
                            st.write(f"**{fighter.name}** ({fighter.type}) - M: {fighter.m}, WS: {fighter.ws}, BS: {fighter.bs}")
                    # Add fighter form (download the fighter info and then update session state)
                    with st.form(key=f"fighter_form_{idx}"):
                        fighter_name = st.text_input("Fighter Name")
                        fighter_type = st.text_input("Fighter Type")
                        m_default = st.number_input("M", min_value=1, value=5, key=f"m_{idx}")
                        ws_default = st.number_input("WS", min_value=1, value=4, key=f"ws_{idx}")
                        bs_default = st.number_input("BS", min_value=1, value=3, key=f"bs_{idx}")
                        s_default = st.number_input("S", min_value=1, value=3, key=f"s_{idx}")
                        t_default = st.number_input("T", min_value=1, value=3, key=f"t_{idx}")
                        w_default = st.number_input("W", min_value=1, value=1, key=f"w_{idx}")
                        i_default = st.number_input("I", min_value=1, value=4, key=f"i_{idx}")
                        a_default = st.number_input("A", min_value=1, value=1, key=f"a_{idx}")
                        ld_default = st.number_input("Ld", min_value=1, value=7, key=f"ld_{idx}")
                        cl_default = st.number_input("Cl", min_value=1, value=5, key=f"cl_{idx}")
                        wil_default = st.number_input("Wil", min_value=1, value=6, key=f"wil_{idx}")
                        int_default = st.number_input("Int", min_value=1, value=8, key=f"int_{idx}")
                        submitted = st.form_submit_button("Add Fighter")
                        if submitted:
                            if fighter_name and fighter_type:
                                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                try:
                                    new_fighter = st.session_state.gangers[0].__class__(
                                        name=fighter_name,
                                        type=fighter_type,
                                        m=m_default,
                                        ws=ws_default,
                                        bs=bs_default,
                                        s=s_default,
                                        t=t_default,
                                        w=w_default,
                                        i=i_default,
                                        a=a_default,
                                        ld=ld_default,
                                        cl=cl_default,
                                        wil=wil_default,
                                        intelligence=int_default,
                                        cost=300,
                                        xp=0,
                                        kills=0,
                                        advance_count=0,
                                        status="Alive",
                                        notes="",
                                        datetime_added=now_str,
                                        datetime_updated=now_str
                                    )
                                    gang.gangers.append(new_fighter)
                                    st.success(f"Added fighter {fighter_name}!")
                                except ValidationError as e:
                                    st.error(f"Error: {e}")
                            else:
                                st.error("Provide both fighter name and type.")
        else:
            st.info("No gangs registered yet.")

show_gangs()
