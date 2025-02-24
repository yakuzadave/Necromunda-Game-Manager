import streamlit as st
from datetime import datetime
from pydantic import ValidationError
from common import Gang, GangFighter, save_data, load_data

# Initialize session state if needed
if 'gangs' not in st.session_state:
    gangs, territories, battles = load_data()
    st.session_state.gangs = gangs
    st.session_state.territories = territories
    st.session_state.battles = battles

# Ensure a container for selected fighter exists
if "selected_fighter" not in st.session_state:
    st.session_state.selected_fighter = None

st.title("Gangs Management")

col1, col2 = st.columns([2, 3])

### Left Column: Gang & Fighter List
with col1:
    st.header("Active Gangs & Fighters")
    if not st.session_state.gangs:
        st.info("No gangs registered yet.")
    else:
        for gang in st.session_state.gangs:
            with st.expander(f"{gang.gang_name} ({gang.gang_type})"):
                st.write(f"**Credits:** {gang.credits} | **Reputation:** {gang.reputation}")
                st.write(f"**Territories:** {len(gang.territories)}")
                st.write("**Fighters:**")
                if gang.gangers:
                    for fighter in gang.gangers:
                        st.write(f"- {fighter.name} ({fighter.type})")
                        if st.button(f"View {fighter.name} Details", key=f"view_{fighter.ganger_id}"):
                            # Store both fighter and its gang in session state
                            st.session_state.selected_fighter = {"fighter": fighter, "gang": gang}
                            st.experimental_rerun()
                else:
                    st.info("No fighters found for this gang.")
                st.markdown("---")

    st.markdown("### Add New Gang")
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

### Right Column: Selected Fighter Details
with col2:
    st.header("Fighter Details")
    if st.session_state.selected_fighter is not None:
        fighter_info = st.session_state.selected_fighter
        fighter = fighter_info["fighter"]
        gang = fighter_info["gang"]

        st.markdown(f"## {fighter.name} ({fighter.type})")
        st.markdown("---")

        # Two-column layout for fighter stats
        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"**Movement (M):** {fighter.m}")
            st.markdown(f"**Weapon Skill (WS):** {fighter.ws}")
            st.markdown(f"**Ballistic Skill (BS):** {fighter.bs}")
            st.markdown(f"**Strength (S):** {fighter.s}")
            st.markdown(f"**Toughness (T):** {fighter.t}")
            st.markdown(f"**Wounds (W):** {fighter.w}")
            st.markdown(f"**Initiative (I):** {fighter.i}")
        with colB:
            st.markdown(f"**Attacks (A):** {fighter.a}")
            st.markdown(f"**Leadership (Ld):** {fighter.ld}")
            st.markdown(f"**Cool (Cl):** {fighter.cl}")
            st.markdown(f"**Will (Wil):** {fighter.wil}")
            st.markdown(f"**Int (Int):** {fighter.intelligence}")
            st.markdown(f"**Cost:** {fighter.cost}")
            st.markdown(f"**XP:** {fighter.xp}")
            st.markdown(f"**Kills:** {fighter.kills}")
            st.markdown(f"**Advance Count:** {fighter.advance_count}")

        st.markdown("---")
        st.markdown("#### Equipment")
        if fighter.equipment:
            for eq in fighter.equipment:
                st.markdown(f"- **{eq.name}** (Qty: {eq.qty})")
        else:
            st.markdown("_None_")

        st.markdown("#### Skills")
        if fighter.skills:
            st.markdown(", ".join(fighter.skills))
        else:
            st.markdown("_None_")

        st.markdown("#### Injuries")
        if fighter.injuries:
            st.markdown(", ".join(fighter.injuries))
        else:
            st.markdown("_None_")

        st.markdown(f"**Status:** {fighter.status}")
        if fighter.notes:
            st.markdown(f"**Notes:** {fighter.notes}")
        st.markdown(f"**Last Updated:** {fighter.datetime_updated}")

        if st.button("Clear Selection"):
            st.session_state.selected_fighter = None
            st.experimental_rerun()
    else:
        st.info("Select a fighter from the left to view details.")
