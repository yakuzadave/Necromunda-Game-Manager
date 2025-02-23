import streamlit as st
from datetime import datetime
from common import Gang  # Replace 'common' with the module where your Gang model is defined

def to_gang_obj(g):
    """
    Convert a gang entry (possibly a dict) into a Gang model instance.
    """
    if isinstance(g, dict):
        try:
            return Gang(**g)
        except Exception as e:
            st.error(f"Conversion error for gang '{g.get('gang_name', 'Unknown')}': {e}")
            return None
    return g

def show_dashboard():
    st.subheader("Dashboard")
    # Convert all gangs from session state to model instances (skipping any that fail)
    gang_objects = []
    for g in st.session_state.gangs:
        gang_obj = to_gang_obj(g)
        if gang_obj is not None:
            gang_objects.append(gang_obj)

    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("Total Gangs", len(gang_objects))
    with col4:
        total_credits = sum(g.credits for g in gang_objects)
        st.metric("Total Credits", total_credits)
    with col5:
        if gang_objects:
            top_gang = max(gang_objects, key=lambda g: g.reputation)
            st.metric("Top Gang", f"{top_gang.gang_name} ({top_gang.reputation} rep)")

    if st.session_state.battles:
        with st.expander("Battle Log"):
            for battle in st.session_state.battles:
                st.write(f"**{battle.battle_scenario}** on {battle.battle_created_datetime}")
                win_info = f"Winner: {battle.winner_gang}"
                if battle.winner_territory:
                    win_info += f" (Territory: {battle.winner_territory})"
                st.write(win_info)
                st.write(f"Participants: {', '.join(battle.participating_gangs)}")
                st.markdown("---")
    else:
        st.info("No battles recorded yet.")

show_dashboard()
