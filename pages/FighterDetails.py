# pages/FighterDetails.py

import streamlit as st
from common import Gang, GangFighter  # Adjust as needed

def show_fighter_details():
    st.subheader("Fighter Details")

    # If we don’t have a selected fighter, show an error or redirect
    if "selected_fighter_id" not in st.session_state or "selected_gang_id" not in st.session_state:
        st.error("No fighter selected. Please go back to Gangs and select a fighter.")
        return

    fighter_id = st.session_state.selected_fighter_id
    gang_id = st.session_state.selected_gang_id

    # Find the matching gang and fighter in session state
    target_gang = None
    target_fighter = None
    for g in st.session_state.gangs:
        if g.gang_id == gang_id:
            target_gang = g
            break
    if not target_gang:
        st.error("Selected gang not found.")
        return

    for f in target_gang.gangers:
        if f.ganger_id == fighter_id:
            target_fighter = f
            break
    if not target_fighter:
        st.error("Selected fighter not found.")
        return

    # Display fighter details
    st.write(f"**Name**: {target_fighter.name}")
    st.write(f"**Type**: {target_fighter.type}")
    st.write(f"**Movement (M)**: {target_fighter.m}")
    st.write(f"**Weapon Skill (WS)**: {target_fighter.ws}")
    st.write(f"**Ballistic Skill (BS)**: {target_fighter.bs}")
    st.write(f"**Strength (S)**: {target_fighter.s}")
    st.write(f"**Toughness (T)**: {target_fighter.t}")
    st.write(f"**Wounds (W)**: {target_fighter.w}")
    st.write(f"**Initiative (I)**: {target_fighter.i}")
    st.write(f"**Attacks (A)**: {target_fighter.a}")
    st.write(f"**Leadership (Ld)**: {target_fighter.ld}")
    st.write(f"**Cool (Cl)**: {target_fighter.cl}")
    st.write(f"**Will (Wil)**: {target_fighter.wil}")
    st.write(f"**Int (Int)**: {target_fighter.intelligence}")
    st.write(f"**Cost**: {target_fighter.cost}")
    st.write(f"**XP**: {target_fighter.xp}")
    st.write(f"**Kills**: {target_fighter.kills}")
    st.write(f"**Advance Count**: {target_fighter.advance_count}")

    st.write("**Equipment:**")
    if target_fighter.equipment:
        for eq in target_fighter.equipment:
            st.write(f"- {eq.name} (qty: {eq.qty})")
    else:
        st.write("_None_")

    st.write("**Skills:**")
    if target_fighter.skills:
        st.write(", ".join(target_fighter.skills))
    else:
        st.write("_None_")

    st.write("**Injuries:**")
    if target_fighter.injuries:
        st.write(", ".join(target_fighter.injuries))
    else:
        st.write("_None_")

    st.write(f"**Status**: {target_fighter.status}")
    if target_fighter.notes:
        st.write(f"**Notes:** {target_fighter.notes}")
    st.write(f"**Last Updated:** {target_fighter.datetime_updated}")

    if st.button("Back to Gangs"):
        # Clear selection and go back
        st.session_state.page = "Gangs"
        st.experimental_rerun()

# Then in your code that runs the page logic:
def run_fighter_details_page():
    show_fighter_details()
