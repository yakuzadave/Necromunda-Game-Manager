import streamlit as st
from datetime import datetime
from common import LocalBattle, save_data

def show_battles():
    st.subheader("Battle Recording")
    with st.form("battle_form"):
        battle_scenario = st.text_input("Battle Scenario")
        gang_names = [g.gang_name for g in st.session_state.gangs]
        winner_gang = st.selectbox("Winning Gang", gang_names) if gang_names else ""
        winner_territory = st.text_input("Winning Territory (optional)")
        participating_gangs = st.multiselect("Participating Gangs", gang_names)
        submit_battle = st.form_submit_button("Record Battle")
        if submit_battle:
            if battle_scenario and winner_gang and participating_gangs:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_battle = LocalBattle(
                    battle_created_datetime=now_str,
                    battle_scenario=battle_scenario,
                    winner_gang=winner_gang,
                    winner_territory=winner_territory if winner_territory else None,
                    participating_gangs=participating_gangs
                )
                st.session_state.battles.append(new_battle)
                save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                st.success("Battle recorded!")
            else:
                st.error("Complete all battle details and select participants.")
    st.markdown("---")
    st.write("### Battle Log")
    if st.session_state.battles:
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

show_battles()
