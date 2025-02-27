import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import plotly.express as px

from common import Gang, GangFighter, save_data
from utils.logger import log_info, log_error, log_debug

def show_fighter_management():
    """Display fighter management interface for all gangs"""
    
    st.title("Fighter Management")
    
    # Get all gangs
    gangs = st.session_state.gangs
    
    if not gangs:
        st.warning("No gangs found. Please create a gang first.")
        if st.button("Go to Gang Creation"):
            st.switch_page("views/2_Gangs.py")
        return
    
    # Select gang
    gang_names = [g.gang_name for g in gangs]
    selected_gang_name = st.selectbox("Select Gang", gang_names)
    
    # Get selected gang
    selected_gang = None
    for g in gangs:
        if g.gang_name == selected_gang_name:
            selected_gang = g
            break
    
    if not selected_gang:
        st.error("Selected gang not found")
        return
    
    # Display gang info
    st.subheader(f"{selected_gang.gang_name} ({selected_gang.gang_type})")
    
    # Key gang metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Credits", f"ⓒ{selected_gang.credits}")
    with col2:
        st.metric("Reputation", selected_gang.reputation)
    with col3:
        fighter_count = len(selected_gang.gangers) if selected_gang.gangers else 0
        st.metric("Fighters", fighter_count)
    
    # Add tabs for fighter management
    tab1, tab2, tab3 = st.tabs(["Fighter List", "Add Fighter", "Analytics"])
    
    # Tab 1: Fighter List
    with tab1:
        if selected_gang.gangers and len(selected_gang.gangers) > 0:
            # Prepare fighter data for display
            fighter_data = []
            for fighter in selected_gang.gangers:
                fighter_data.append({
                    "ID": fighter.ganger_id,
                    "Name": fighter.name,
                    "Type": fighter.type,
                    "XP": fighter.xp,
                    "Cost": fighter.cost,
                    "Status": fighter.status
                })
            
            # Convert to DataFrame
            df = pd.DataFrame(fighter_data)
            
            # Display fighters
            st.dataframe(
                df,
                column_config={
                    "ID": st.column_config.Column("ID", width="small", required=True),
                    "Name": st.column_config.Column("Name", width="medium"),
                    "Type": st.column_config.Column("Type", width="small"),
                    "XP": st.column_config.NumberColumn("XP"),
                    "Cost": st.column_config.NumberColumn("Cost"),
                    "Status": st.column_config.Column("Status", width="small"),
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Fighter selection for details view
            selected_fighter_id = st.selectbox(
                "Select fighter to view details",
                [f.ganger_id for f in selected_gang.gangers],
                format_func=lambda x: next((f.name for f in selected_gang.gangers if f.ganger_id == x), x)
            )
            
            # Save selection to session state
            if st.button("View Fighter Details"):
                st.session_state.selected_fighter_id = selected_fighter_id
                st.session_state.selected_gang_id = selected_gang.gang_id
                st.switch_page("views/FighterDetails.py")
                
            # Quick actions
            st.subheader("Quick Actions")
            action_cols = st.columns(4)
            
            with action_cols[0]:
                if st.button("Award XP"):
                    st.session_state.award_xp = True
                    st.rerun()
            
            with action_cols[1]:
                if st.button("Record Kill"):
                    st.session_state.record_kill = True
                    st.rerun()
            
            with action_cols[2]:
                if st.button("Change Status"):
                    st.session_state.change_status = True
                    st.rerun()
            
            with action_cols[3]:
                if st.button("Add Injury"):
                    st.session_state.add_injury = True
                    st.rerun()
            
            # Handle quick actions
            if "award_xp" in st.session_state and st.session_state.award_xp:
                st.subheader("Award XP")
                
                selected_fighter_for_xp = st.selectbox(
                    "Select fighter",
                    [f.ganger_id for f in selected_gang.gangers],
                    format_func=lambda x: next((f.name for f in selected_gang.gangers if f.ganger_id == x), x),
                    key="xp_fighter_select"
                )
                
                xp_amount = st.number_input("XP to award", min_value=1, value=1)
                
                if st.button("Award"):
                    try:
                        # Find fighter and award XP
                        for gang in st.session_state.gangs:
                            if gang.gang_id == selected_gang.gang_id:
                                for fighter in gang.gangers:
                                    if fighter.ganger_id == selected_fighter_for_xp:
                                        fighter.xp += xp_amount
                                        fighter.datetime_updated = datetime.now().isoformat()
                                        break
                        
                        # Save data
                        save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                        log_info(f"Awarded {xp_amount} XP to fighter")
                        st.success(f"XP awarded successfully!")
                        
                        # Clear state and refresh
                        del st.session_state.award_xp
                        st.rerun()
                    except Exception as e:
                        log_error(f"Error awarding XP: {e}", exc_info=True)
                        st.error(f"Error: {str(e)}")
                
                if st.button("Cancel", key="cancel_xp"):
                    del st.session_state.award_xp
                    st.rerun()
            
            # Similar handlers for other quick actions (record_kill, change_status, add_injury)
            # ...
                
        else:
            st.info("This gang has no fighters. Add some fighters first.")
    
    # Tab 2: Add Fighter
    with tab2:
        with st.form("add_fighter_form"):
            st.subheader("Add New Fighter")
            
            # Basic info
            fighter_name = st.text_input("Fighter Name")
            fighter_type = st.selectbox("Fighter Type", [
                "Leader", "Champion", "Ganger", "Juve", "Heavy", 
                "Specialist", "Prospect", "Hired Gun", "Exotic Beast"
            ])
            
            # Stats in columns for better layout
            st.subheader("Characteristics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                m = st.number_input("M", value=4, min_value=1)
                s = st.number_input("S", value=3, min_value=1)
                i = st.number_input("I", value=4, min_value=1)
            
            with col2:
                ws = st.number_input("WS", value=3, min_value=1)
                t = st.number_input("T", value=3, min_value=1)
                a = st.number_input("A", value=1, min_value=1)
            
            with col3:
                bs = st.number_input("BS", value=3, min_value=1)
                w = st.number_input("W", value=1, min_value=1)
                ld = st.number_input("Ld", value=7, min_value=1)
            
            with col4:
                cl = st.number_input("Cl", value=7, min_value=1)
                wil = st.number_input("Wil", value=7, min_value=1)
                intelligence = st.number_input("Int", value=7, min_value=1)
            
            # Other attributes
            st.subheader("Other Details")
            cost = st.number_input("Cost (credits)", value=0, min_value=0)
            xp = st.number_input("Starting XP", value=0, min_value=0)
            status = st.selectbox("Status", ["Active", "Injured", "Out of action", "Dead"])
            notes = st.text_area("Notes")
            
            # Submit button
            submitted = st.form_submit_button("Add Fighter")
            
            # Process form submission
            if submitted and fighter_name:
                try:
                    # Create new fighter
                    new_fighter = GangFighter(
                        ganger_id=str(uuid.uuid4()),
                        name=fighter_name,
                        type=fighter_type,
                        m=m, ws=ws, bs=bs, s=s, t=t, w=w, 
                        i=i, a=a, ld=ld, cl=cl, wil=wil, 
                        int=intelligence,  # using the alias
                        cost=cost,
                        xp=xp,
                        kills=0,
                        advance_count=0,
                        status=status,
                        notes=notes,
                        datetime_added=datetime.now().isoformat(),
                        datetime_updated=datetime.now().isoformat()
                    )
                    
                    # Add fighter to gang
                    for gang in st.session_state.gangs:
                        if gang.gang_id == selected_gang.gang_id:
                            if not gang.gangers:
                                gang.gangers = []
                            gang.gangers.append(new_fighter)
                            break
                    
                    # Save data
                    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                    log_info(f"Added new fighter {fighter_name} to {selected_gang.gang_name}")
                    st.success(f"Added {fighter_name} to {selected_gang.gang_name}")
                    
                    # Refresh
                    st.rerun()
                except Exception as e:
                    log_error(f"Error adding fighter: {e}", exc_info=True)
                    st.error(f"Error adding fighter: {str(e)}")
    
    # Tab 3: Analytics
    with tab3:
        if selected_gang.gangers and len(selected_gang.gangers) > 0:
            st.subheader("Fighter Analytics")
            
            # XP distribution chart
            xp_data = [{"Fighter": f.name, "XP": f.xp} for f in selected_gang.gangers]
            if xp_data:
                df = pd.DataFrame(xp_data)
                fig = px.bar(
                    df, x="Fighter", y="XP", 
                    title="Fighter XP Distribution",
                    color="XP",
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Fighter type distribution
            type_counts = {}
            for fighter in selected_gang.gangers:
                if fighter.type in type_counts:
                    type_counts[fighter.type] += 1
                else:
                    type_counts[fighter.type] = 1
            
            type_data = [{"Type": t, "Count": c} for t, c in type_counts.items()]
            if type_data:
                df = pd.DataFrame(type_data)
                fig = px.pie(df, names="Type", values="Count", title="Fighter Types")
                st.plotly_chart(fig, use_container_width=True)
            
            # Status breakdown
            status_counts = {}
            for fighter in selected_gang.gangers:
                if fighter.status in status_counts:
                    status_counts[fighter.status] += 1
                else:
                    status_counts[fighter.status] = 1
            
            status_data = [{"Status": s, "Count": c} for s, c in status_counts.items()]
            if status_data:
                df = pd.DataFrame(status_data)
                fig = px.pie(
                    df, names="Status", values="Count", 
                    title="Fighter Status",
                    color="Status",
                    color_discrete_map={
                        "Active": "green",
                        "Injured": "orange",
                        "Out of action": "red",
                        "Dead": "black"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add fighters to see analytics.")

# Call the function to display fighter management
show_fighter_management()
