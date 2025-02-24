import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
from common import Gang, load_data, Territory, LocalBattle  # Import required models

def to_gang_obj(g):
    """Convert a gang entry to a Gang model instance with error handling"""
    if isinstance(g, dict):
        try:
            return Gang(**g)
        except Exception as e:
            st.error(f"Conversion error for gang '{g.get('gang_name', 'Unknown')}': {e}")
            return None
    return g

def show_dashboard():
    st.title("Campaign Dashboard")

    # Load all data
    gangs, territories, battles = load_data()
    gang_objects = [g for g in (to_gang_obj(g) for g in gangs) if g is not None]

    # ---- Key Metrics ----
    st.subheader("Campaign Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        try:
            total_fighters = sum(len(g.gangers) for g in gang_objects)
            st.metric("Total Fighters", total_fighters)
        except Exception as e:
            st.error(f"Error calculating fighters: {e}")

    with col2:
        try:
            avg_reputation = sum(g.reputation for g in gang_objects) / len(gang_objects) if gang_objects else 0
            st.metric("Average Reputation", f"{avg_reputation:.1f}")
        except Exception as e:
            st.error(f"Error calculating reputation: {e}")

    with col3:
        try:
            active_territories = len([t for t in territories if t.controlled_by])
            st.metric("Controlled Territories", f"{active_territories}/{len(territories)}")
        except Exception as e:
            st.error(f"Error calculating territories: {e}")

    with col4:
        try:
            injured_fighters = sum(
                len([f for f in g.gangers if "Injured" in f.status]) 
                for g in gang_objects
            )
            st.metric("Injured Fighters", injured_fighters)
        except Exception as e:
            st.error(f"Error calculating injuries: {e}")

    # ---- Visualizations ----
    st.subheader("Visual Analytics")

    # Gang Reputation Chart
    try:
        rep_data = [{"Gang": g.gang_name, "Reputation": g.reputation} for g in gang_objects]
        if rep_data:
            df = pd.DataFrame(rep_data)
            fig = px.bar(df, x="Gang", y="Reputation", title="Gang Reputation Rankings",
                        color="Gang", height=300)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not generate reputation chart: {e}")

    # Credit Distribution Pie Chart
    try:
        credit_data = [{"Gang": g.gang_name, "Credits": g.credits} for g in gang_objects]
        if credit_data:
            df = pd.DataFrame(credit_data)
            fig = px.pie(df, names="Gang", values="Credits", 
                        title="Credit Distribution Among Gangs", height=300)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not generate credit chart: {e}")

    # Battle Outcomes Timeline
    try:
        battle_data = []
        for b in battles:
            battle_data.append({
                "Date": datetime.fromisoformat(b.battle_created_datetime),
                "Winner": b.winner_gang,
                "Scenario": b.battle_scenario
            })
        if battle_data:
            df = pd.DataFrame(battle_data)
            fig = px.scatter(df, x="Date", y="Winner", color="Winner",
                           hover_data=["Scenario"],
                           title="Battle Outcomes Timeline", height=300)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not generate battle timeline: {e}")

    # Gang Win Rate
    try:
        win_counts = {}
        participation_counts = {}
        for b in battles:
            win_counts[b.winner_gang] = win_counts.get(b.winner_gang, 0) + 1
            for gang in b.participating_gangs:
                participation_counts[gang] = participation_counts.get(gang, 0) + 1
        
        win_rate_data = []
        for gang in gang_objects:
            wins = win_counts.get(gang.gang_name, 0)
            participations = participation_counts.get(gang.gang_name, 0)
            win_rate = (wins / participations * 100) if participations > 0 else 0
            win_rate_data.append({
                "Gang": gang.gang_name,
                "Win Rate %": win_rate,
                "Total Battles": participations
            })
        
        if win_rate_data:
            df = pd.DataFrame(win_rate_data)
            fig = px.bar(df, x="Gang", y="Win Rate %",
                        hover_data=["Total Battles"],
                        title="Gang Win Rates", height=300)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not generate win rate chart: {e}")

    # ---- Territory Control Section ----
    st.subheader("Territory Control")

    # Territory Map (abstract or geolocated)
    if any(t.lat and t.lng for t in territories):
        try:
            map_df = pd.DataFrame([t.dict() for t in territories])
            st.map(map_df[["lat", "lng", "name", "controlled_by"]].dropna())
        except Exception as e:
            st.error(f"Could not render territory map: {e}")
    else:
        # Abstract grid visualization
        cols = st.columns(4)
        for i, territory in enumerate(territories):
            with cols[i % 4]:
                controller = territory.controlled_by or "Unclaimed"
                st.markdown(f"""
                    **{territory.name}**  
                    *Type:* {territory.type}  
                    *Controller:* {controller}
                """)

    # ---- Battle History ----
    st.subheader("Battle History")

    # Battle filters
    col_left, col_right = st.columns(2)
    with col_left:
        filter_scenario = st.text_input("Filter by Scenario")
    with col_right:
        min_date = min((datetime.fromisoformat(b.battle_created_datetime) for b in battles), default=None)
        date_filter = st.date_input("Filter by Date", 
                                  min_value=min_date,
                                  max_value=datetime.now()) if min_date else None

    # Filtered battles
    filtered_battles = []
    for b in battles:
        battle_date = datetime.fromisoformat(b.battle_created_datetime).date()
        matches_scenario = filter_scenario.lower() in b.battle_scenario.lower()
        matches_date = not date_filter or battle_date == date_filter

        if matches_scenario and matches_date:
            filtered_battles.append(b)

    # Battle list with details
    if filtered_battles:
        st.subheader("Battle Log")
        for battle in filtered_battles:
            with st.container():
                # Battle header
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{battle.battle_scenario}**")
                    st.caption(f"🕒 {battle.battle_created_datetime}")
                with col2:
                    st.markdown(f"🏆 **{battle.winner_gang}**")

                # Battle details
                st.markdown(f"**Participants:** {', '.join(battle.participating_gangs)}")
                if battle.winner_territory:
                    st.markdown(f"**Territory Won:** {battle.winner_territory}")
                if hasattr(battle, 'xp_awards'):
                    st.markdown("**XP Awards:**")
                    st.json(battle.xp_awards)
                if hasattr(battle, 'credit_awards'):
                    st.markdown("**Credit Awards:**")
                    st.json(battle.credit_awards)
                st.markdown("---")
    else:
        st.info("No battles found matching filters")

    # ---- Gang Summary ----
    st.subheader("Gang Overview")

    for gang in gang_objects:
        with st.expander(f"{gang.gang_name} ({gang.gang_type})", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Credits", f"ⓒ{gang.credits}")
                st.metric("Reputation", gang.reputation)

            with col2:
                st.metric("Fighters", len(gang.gangers))
                st.metric("Territories", len(gang.territories))

            with col3:
                if gang.stash:
                    equipment_count = sum(e.qty for e in gang.stash)
                    st.metric("Equipment Items", equipment_count)
                else:
                    st.metric("Equipment Items", 0)

            # Quick action buttons
            if st.button("View Details", key=f"view_{gang.gang_id}"):
                st.session_state.current_gang = gang
                st.switch_page("pages/2_Gangs.py")  # Assuming you have a gang detail page



show_dashboard()