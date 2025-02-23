# pages/Gangs.py

import streamlit as st
from datetime import datetime
from pydantic import ValidationError
from common import Gang, GangFighter, save_data  # Adjust your import as needed

def show_gangs():
    st.subheader("Gangs")
    col1, col2 = st.columns([2, 3])

    # --- Left Column: Register New Gang ---
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
                    new_gang = Gang(
                        gang_name=gang_name_input,
                        gang_type=gang_type_input,
                        campaign=campaign_input,
                        credits=credits_input,
                        reputation=reputation_input
                    )
                    st.session_state.gangs.append(new_gang)
                    # Save the updated data
                    save_data(
                        st.session_state.gangs,
                        st.session_state.territories,
                        st.session_state.battles
                    )
                    st.success(f"Registered {gang_name_input}!")
                except ValidationError as e:
                    st.error(f"Error creating gang: {e}")
            else:
                st.error("Please enter a gang name.")

    # --- Right Column: Active Gangs & Fighter Management ---
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

                    # Optional: Quick Battle button
                    if st.button("Record Battle (Quick)", key=f"battle_{idx}"):
                        gang.reputation += 5
                        gang.credits += 100
                        save_data(
                            st.session_state.gangs,
                            st.session_state.territories,
                            st.session_state.battles
                        )
                        st.success("Battle recorded!")

                    # Remove Gang button
                    if st.button("Remove Gang", key=f"remove_{idx}"):
                        st.session_state.gangs.pop(idx)
                        save_data(
                            st.session_state.gangs,
                            st.session_state.territories,
                            st.session_state.battles
                        )
                        st.experimental_rerun()

                    # Display fighters
                    st.write("**Fighters:**")
                    if gang.gangers:
                        for fighter in gang.gangers:
                            # Show a concise summary
                            summary = (f"{fighter.name} ({fighter.type}) "
                                       f"- M:{fighter.m}, WS:{fighter.ws}, BS:{fighter.bs}")
                            st.write(summary)

                            # "View Details" button for dedicated FighterDetails page
                            if st.button(f"View {fighter.name} Details", key=f"view_{fighter.ganger_id}"):
                                st.session_state.selected_fighter_id = fighter.ganger_id
                                st.session_state.selected_gang_id = gang.gang_id
                                # Here we set a session var or direct nav
                                # If you're using a multi-page app with pages/ structure,
                                # you might do:
                                st.session_state.page = "Fighter Details"
                                st.experimental_rerun()
                    else:
                        st.info("No fighters found for this gang.")

                    # Add Fighter form
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
                                    new_fighter = GangFighter(
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
                                    save_data(
                                        st.session_state.gangs,
                                        st.session_state.territories,
                                        st.session_state.battles
                                    )
                                    st.success(f"Added fighter {fighter_name}!")
                                except ValidationError as e:
                                    st.error(f"Error: {e}")
                            else:
                                st.error("Provide both fighter name and type.")
        else:
            st.info("No gangs registered yet.")

def run_gangs_page():
    show_gangs()
