# pages/FighterDetails.py

import streamlit as st
from common import Gang, GangFighter

def show_fighter_details():
    st.subheader("Fighter Details")

    # Debug: print session state keys to help ensure the required keys are set
    st.write("Session state keys:", list(st.session_state.keys()))

    # Check for selected fighter and gang IDs
    if "selected_fighter_id" not in st.session_state or "selected_gang_id" not in st.session_state:
        st.error("No fighter selected. Please go back to Gangs and select a fighter.")
        return

    fighter_id = st.session_state.selected_fighter_id
    gang_id = st.session_state.selected_gang_id

    # Find the matching gang using next()
    target_gang = next((g for g in st.session_state.gangs if g.gang_id == gang_id), None)
    if not target_gang:
        st.error("Selected gang not found.")
        return

    # Find the matching fighter within the gang
    target_fighter = next((f for f in target_gang.gangers if f.ganger_id == fighter_id), None)
    if not target_fighter:
        st.error("Selected fighter not found.")
        return

    # Display fighter header
    st.markdown(f"## {target_fighter.name} ({target_fighter.type})")
    st.markdown("---")

    # Display fighter stats in two columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Movement (M):** {target_fighter.m}")
        st.markdown(f"**Weapon Skill (WS):** {target_fighter.ws}")
        st.markdown(f"**Ballistic Skill (BS):** {target_fighter.bs}")
        st.markdown(f"**Strength (S):** {target_fighter.s}")
        st.markdown(f"**Toughness (T):** {target_fighter.t}")
        st.markdown(f"**Wounds (W):** {target_fighter.w}")
        st.markdown(f"**Initiative (I):** {target_fighter.i}")
    with col2:
        st.markdown(f"**Attacks (A):** {target_fighter.a}")
        st.markdown(f"**Leadership (Ld):** {target_fighter.ld}")
        st.markdown(f"**Cool (Cl):** {target_fighter.cl}")
        st.markdown(f"**Will (Wil):** {target_fighter.wil}")
        st.markdown(f"**Int (Int):** {target_fighter.intelligence}")
        st.markdown(f"**Cost:** {target_fighter.cost}")
        st.markdown(f"**XP:** {target_fighter.xp}")
        st.markdown(f"**Kills:** {target_fighter.kills}")
        st.markdown(f"**Advance Count:** {target_fighter.advance_count}")

    st.markdown("---")
    st.markdown("#### Equipment")
    if target_fighter.equipment:
        for eq in target_fighter.equipment:
            st.markdown(f"- **{eq.name}** (Qty: {eq.qty})")
    else:
        st.markdown("_None_")

    st.markdown("#### Skills")
    if target_fighter.skills:
        st.markdown(", ".join(target_fighter.skills))
    else:
        st.markdown("_None_")

    st.markdown("#### Injuries")
    if target_fighter.injuries:
        st.markdown(", ".join(target_fighter.injuries))
    else:
        st.markdown("_None_")

    st.markdown(f"**Status:** {target_fighter.status}")
    if target_fighter.notes:
        st.markdown(f"**Notes:** {target_fighter.notes}")
    st.markdown(f"**Last Updated:** {target_fighter.datetime_updated}")

    # Back button to return to the Gangs page
    if st.button("Back to Gangs"):
        st.session_state.pop("selected_fighter_id", None)
        st.session_state.pop("selected_gang_id", None)
        st.session_state.page = "Gangs"
        st.experimental_rerun()

def run_fighter_details_page():
    show_fighter_details()
