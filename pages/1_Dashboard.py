import streamlit as st
from datetime import datetime

def show_dashboard():
    st.subheader("Dashboard")
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("Total Gangs", len(st.session_state.gangs))
    with col4:
        total_credits = sum(g.credits for g in st.session_state.gangs)
        st.metric("Total Credits", total_credits)
    with col5:
        if st.session_state.gangs:
            top_gang = max(st.session_state.gangs, key=lambda g: g.reputation)
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
