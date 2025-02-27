# pages/FighterDetails.py

import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import io
import base64
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

from common import Gang, GangFighter, Equipment, save_data
from utils.logger import log_info, log_error, log_debug, log_function_call

@log_function_call
def show_fighter_details():
    """Display detailed information for a selected fighter"""
    
    st.title("Fighter Details")
    
    # Check if we have a selected fighter and gang in session state
    if "selected_fighter_id" not in st.session_state or "selected_gang_id" not in st.session_state:
        st.error("No fighter selected. Please select a fighter first.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Fighters", use_container_width=True):
                st.switch_page("views/5_FighterManagement.py")  # Fixed path reference
        with col2:
            if st.button("Go to Dashboard", use_container_width=True):
                st.switch_page("views/1_Dashboard.py")  # Fixed path reference
        return
    
    # Find the gang and fighter in session state with better error handling
    try:
        fighter_id = st.session_state.selected_fighter_id
        gang_id = st.session_state.selected_gang_id
        
        selected_gang = next((gang for gang in st.session_state.gangs if gang.gang_id == gang_id), None)
        if not selected_gang:
            raise ValueError(f"Gang with ID {gang_id} not found")
            
        selected_fighter = next((fighter for fighter in selected_gang.gangers if fighter.ganger_id == fighter_id), None)
        if not selected_fighter:
            raise ValueError(f"Fighter with ID {fighter_id} not found in gang {selected_gang.gang_name}")
    
    except Exception as e:
        st.error(f"Error locating fighter data: {str(e)}")
        log_error(f"Error loading fighter details: {e}", exc_info=True)
        if st.button("Return to Fighters"):
            st.switch_page("views/5_FighterManagement.py")  # Fixed path reference
        return
    
    # Display fighter header with portrait if available
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Display fighter image if available, otherwise a placeholder
        if selected_fighter.image:
            st.image(selected_fighter.image, caption=selected_fighter.name)
        else:
            st.image("https://via.placeholder.com/150?text=No+Image", caption=selected_fighter.name)
    
    with col2:
        # Fighter name and type header
        st.header(f"{selected_fighter.name}")
        st.subheader(f"{selected_fighter.type} - {selected_gang.gang_name}")
        
        # Status badge with improved color coding
        status_color = "green"
        if "Injured" in selected_fighter.status:
            status_color = "orange"
        elif "Out of action" in selected_fighter.status:
            status_color = "red"
        elif "Dead" in selected_fighter.status:
            status_color = "darkred"
        
        st.markdown(
            f"<span style='background-color:{status_color};padding:5px;border-radius:5px;color:white;font-weight:bold'>"
            f"{selected_fighter.status}</span>", 
            unsafe_allow_html=True
        )
        
        # Experience and kills with more metrics
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("XP", selected_fighter.xp)
        with col_b:
            st.metric("Kills", selected_fighter.kills)
        with col_c:
            st.metric("Advances", selected_fighter.advance_count)
        
        # Last updated
        if hasattr(selected_fighter, "datetime_updated") and selected_fighter.datetime_updated:
            try:
                update_date = datetime.fromisoformat(selected_fighter.datetime_updated)
                st.caption(f"Last updated: {update_date.strftime('%Y-%m-%d %H:%M')}")
            except:
                st.caption(f"Last updated: {selected_fighter.datetime_updated}")
    
    # Tabs for different categories of information
    tabs = st.tabs(["Stats", "Equipment", "Skills", "Injuries", "History", "Notes"])
    
    # Stats Tab
    with tabs[0]:
        st.subheader("Characteristics")
        
        # Create a radar chart for the fighter's stats
        stats_data = {
            "Stat": ["M", "WS", "BS", "S", "T", "W", "I", "A", "Ld", "Cl", "Wil", "Int"],
            "Value": [
                selected_fighter.m, selected_fighter.ws, selected_fighter.bs,
                selected_fighter.s, selected_fighter.t, selected_fighter.w,
                selected_fighter.i, selected_fighter.a, selected_fighter.ld,
                selected_fighter.cl, selected_fighter.wil, selected_fighter.intelligence
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        
        # Create radar chart
        fig = px.line_polar(
            stats_df, r="Value", theta="Stat", line_close=True,
            range_r=[0, max(10, max(stats_df["Value"]))],
            title=f"{selected_fighter.name}'s Stats"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display stats in a more readable format with columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Movement (M)", selected_fighter.m)
            st.metric("Strength (S)", selected_fighter.s)
            st.metric("Initiative (I)", selected_fighter.i)
            st.metric("Leadership (Ld)", selected_fighter.ld)
        with col2:
            st.metric("Weapon Skill (WS)", selected_fighter.ws)
            st.metric("Toughness (T)", selected_fighter.t)
            st.metric("Attacks (A)", selected_fighter.a)
            st.metric("Cool (Cl)", selected_fighter.cl)
        with col3:
            st.metric("Ballistic Skill (BS)", selected_fighter.bs)
            st.metric("Wounds (W)", selected_fighter.w)
            st.metric("Willpower (Wil)", selected_fighter.wil)
            st.metric("Intelligence (Int)", selected_fighter.intelligence)
        
        # Add a button to modify stats
        with st.expander("Modify Stats"):
            stat_cols1 = st.columns(4)
            with stat_cols1[0]:
                new_m = st.number_input("M", value=selected_fighter.m, min_value=1)
            with stat_cols1[1]:
                new_ws = st.number_input("WS", value=selected_fighter.ws, min_value=1)
            with stat_cols1[2]:
                new_bs = st.number_input("BS", value=selected_fighter.bs, min_value=1)
            with stat_cols1[3]:
                new_s = st.number_input("S", value=selected_fighter.s, min_value=1)
                
            stat_cols2 = st.columns(4)
            with stat_cols2[0]:
                new_t = st.number_input("T", value=selected_fighter.t, min_value=1)
            with stat_cols2[1]:
                new_w = st.number_input("W", value=selected_fighter.w, min_value=1)
            with stat_cols2[2]:
                new_i = st.number_input("I", value=selected_fighter.i, min_value=1)
            with stat_cols2[3]:
                new_a = st.number_input("A", value=selected_fighter.a, min_value=1)
                
            stat_cols3 = st.columns(4)
            with stat_cols3[0]:
                new_ld = st.number_input("Ld", value=selected_fighter.ld, min_value=1)
            with stat_cols3[1]:
                new_cl = st.number_input("Cl", value=selected_fighter.cl, min_value=1)
            with stat_cols3[2]:
                new_wil = st.number_input("Wil", value=selected_fighter.wil, min_value=1)
            with stat_cols3[3]:
                new_int = st.number_input("Int", value=selected_fighter.intelligence, min_value=1)
                
            if st.button("Update Stats"):
                try:
                    # Update fighter stats
                    for gang in st.session_state.gangs:
                        if gang.gang_id == gang_id:
                            for fighter in gang.gangers:
                                if fighter.ganger_id == fighter_id:
                                    fighter.m = new_m
                                    fighter.ws = new_ws
                                    fighter.bs = new_bs
                                    fighter.s = new_s
                                    fighter.t = new_t
                                    fighter.w = new_w
                                    fighter.i = new_i
                                    fighter.a = new_a
                                    fighter.ld = new_ld
                                    fighter.cl = new_cl
                                    fighter.wil = new_wil
                                    fighter.intelligence = new_int
                                    fighter.datetime_updated = datetime.now().isoformat()
                                    break
                            
                    # Save data
                    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                    log_info(f"Updated stats for fighter {selected_fighter.name}")
                    st.success("Stats updated successfully!")
                    st.rerun()
                except Exception as e:
                    log_error(f"Error updating stats: {e}", exc_info=True)
                    st.error(f"Error updating stats: {str(e)}")
    
    # Equipment Tab
    with tabs[1]:
        st.subheader("Equipment")
        
        if selected_fighter.equipment and len(selected_fighter.equipment) > 0:
            # Display equipment in a table
            equipment_data = []
            for item in selected_fighter.equipment:
                equipment_data.append({
                    "Name": item.name,
                    "Quantity": item.qty,
                    "Cost": item.cost,
                    "Traits": item.traits
                })
            
            # Create a dataframe for the equipment
            equipment_df = pd.DataFrame(equipment_data)
            
            # Show the equipment table
            st.dataframe(equipment_df, use_container_width=True)
            
            # Add option to remove equipment
            with st.expander("Remove Equipment"):
                equipment_names = [item.name for item in selected_fighter.equipment]
                selected_item = st.selectbox("Select item to remove", equipment_names)
                qty_to_remove = st.number_input("Quantity to remove", min_value=1, value=1, step=1)
                
                if st.button("Remove Equipment"):
                    try:
                        # Find the item in the fighter's equipment
                        for i, item in enumerate(selected_fighter.equipment):
                            if item.name == selected_item:
                                if item.qty <= qty_to_remove:
                                    # Remove the item completely
                                    selected_fighter.equipment.pop(i)
                                    log_info(f"Removed {item.name} from {selected_fighter.name}")
                                else:
                                    # Reduce the quantity
                                    selected_fighter.equipment[i].qty -= qty_to_remove
                                    log_info(f"Reduced {item.name} quantity by {qty_to_remove} for {selected_fighter.name}")
                                break
                        
                        # Update the fighter's datetime
                        selected_fighter.datetime_updated = datetime.now().isoformat()
                        
                        # Add item back to gang's stash
                        for gang in st.session_state.gangs:
                            if gang.gang_id == gang_id:
                                # Check if the item is already in stash
                                item_in_stash = False
                                for stash_item in gang.stash:
                                    if stash_item.name == selected_item:
                                        stash_item.qty += qty_to_remove
                                        item_in_stash = True
                                        break
                                
                                # If item not in stash, add it
                                if not item_in_stash:
                                    for fighter_item in selected_fighter.equipment:
                                        if fighter_item.name == selected_item:
                                            new_stash_item = Equipment(
                                                equipment_id=fighter_item.equipment_id,
                                                name=fighter_item.name,
                                                qty=qty_to_remove,
                                                cost=fighter_item.cost,
                                                traits=fighter_item.traits
                                            )
                                            gang.stash.append(new_stash_item)
                                            break
                                break
                        
                        # Save changes
                        save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                        st.success(f"Equipment removed and added back to gang stash")
                        st.rerun()
                    except Exception as e:
                        log_error(f"Error removing equipment: {e}", exc_info=True)
                        st.error(f"Error: {str(e)}")
        else:
            st.info("This fighter has no equipment")
            
        # Button to add equipment from gang stash
        st.subheader("Add Equipment")
        if st.button("Equip from Gang Stash"):
            st.session_state.from_fighter_details = True
            st.switch_page("views/7_Equipment.py")
    
    # Skills Tab
    with tabs[2]:
        st.subheader("Skills")
        
        if selected_fighter.skills and len(selected_fighter.skills) > 0:
            # Display skills in a list
            for skill in selected_fighter.skills:
                st.markdown(f"- **{skill}**")
        else:
            st.info("This fighter has no skills")
            
        # Add new skill
        with st.expander("Add Skill"):
            new_skill = st.text_input("Skill Name")
            if st.button("Add Skill"):
                if new_skill and new_skill not in selected_fighter.skills:
                    selected_fighter.skills.append(new_skill)
                    selected_fighter.datetime_updated = datetime.now().isoformat()
                    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                    log_info(f"Added skill {new_skill} to {selected_fighter.name}")
                    st.success(f"Added skill: {new_skill}")
                    st.rerun()
    
    # Injuries Tab
    with tabs[3]:
        st.subheader("Injuries")
        
        if selected_fighter.injuries and len(selected_fighter.injuries) > 0:
            # Display injuries in a better formatted list
            for i, injury in enumerate(selected_fighter.injuries):
                with st.container():
                    cols = st.columns([3, 1])
                    with cols[0]:
                        st.markdown(f"**Injury {i+1}:** {injury}")
                    with cols[1]:
                        if st.button("Remove", key=f"remove_injury_{i}"):
                            selected_fighter.injuries.pop(i)
                            selected_fighter.datetime_updated = datetime.now().isoformat()
                            
                            # Update status if no injuries left
                            if not selected_fighter.injuries:
                                selected_fighter.status = "Active"
                                
                            save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                            log_info(f"Removed injury from {selected_fighter.name}")
                            st.success("Injury removed")
                            st.rerun()
        else:
            st.info("This fighter has no injuries")
            
        # Add new injury with improved injury types
        with st.expander("Add Injury"):
            injury_type = st.selectbox("Injury Type", [
                "Flesh Wound", "Back Injury", "Arm Wound", 
                "Leg Wound", "Head Injury", "Eye Injury", 
                "Chest Wound", "Disoriented", "Custom"
            ])
            
            if injury_type == "Custom":
                new_injury = st.text_input("Injury Description")
            else:
                new_injury = injury_type
                
            injury_severity = st.select_slider("Severity", options=["Minor", "Major", "Critical"])
            
            new_injury_desc = f"{new_injury} ({injury_severity})"
            
            if st.button("Add Injury"):
                if new_injury and new_injury_desc not in selected_fighter.injuries:
                    selected_fighter.injuries.append(new_injury_desc)
                    selected_fighter.datetime_updated = datetime.now().isoformat()
                    
                    # Update status if not already injured
                    if "Injured" not in selected_fighter.status:
                        selected_fighter.status = "Injured"
                    
                    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                    log_info(f"Added injury {new_injury_desc} to {selected_fighter.name}")
                    st.success(f"Added injury: {new_injury_desc}")
                    st.rerun()
    
    # History Tab
    with tabs[4]:
        st.subheader("Battle History")
        
        # Improved battle history feature with participation tracking
        battles_participated = []
        for battle in st.session_state.battles:
            if selected_gang.gang_name in battle.participating_gangs:
                battle_result = "Victory" if battle.winner_gang == selected_gang.gang_name else "Defeat"
                battles_participated.append({
                    "Date": datetime.fromisoformat(battle.battle_created_datetime),
                    "Scenario": battle.battle_scenario,
                    "Result": battle_result
                })
        
        if battles_participated:
            # Convert to dataframe and display
            battle_history_df = pd.DataFrame(battles_participated)
            st.dataframe(battle_history_df, use_container_width=True)
            
            # Create a simple win/loss chart
            battle_counts = battle_history_df["Result"].value_counts()
            fig = px.pie(names=battle_counts.index, values=battle_counts.values, 
                      title=f"{selected_fighter.name}'s Battle Record", 
                      color=battle_counts.index,
                      color_discrete_map={"Victory": "green", "Defeat": "red"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("This fighter hasn't participated in any recorded battles yet.")
    
    # Notes Tab
    with tabs[5]:
        st.subheader("Notes")
        
        # Display current notes
        current_notes = selected_fighter.notes if hasattr(selected_fighter, "notes") and selected_fighter.notes else ""
        
        # Edit notes
        new_notes = st.text_area("Fighter Notes", value=current_notes, height=200)
        
        if st.button("Save Notes"):
            selected_fighter.notes = new_notes
            selected_fighter.datetime_updated = datetime.now().isoformat()
            save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
            log_info(f"Updated notes for {selected_fighter.name}")
            st.success("Notes saved successfully")
    
    # Buttons at the bottom
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Return to Fighters"):
            st.switch_page("views/5_FighterManagement.py")  # Fixed path reference
    
    with col2:
        if st.button("Return to Gang"):
            st.session_state.current_gang_id = gang_id
            st.switch_page("views/2_Gangs.py")  # Fixed path reference
    
    with col3:
        # Improved confirm dialog for deleting fighter
        delete_pressed = st.button("Delete Fighter", type="primary", use_container_width=True)
        if delete_pressed:
            st.error("Are you sure you want to delete this fighter? This cannot be undone.")
            col3a, col3b = st.columns(2)
            with col3a:
                if st.button("Cancel"):
                    st.rerun()
            with col3b:
                if st.button("Confirm Delete", type="primary"):
                    # Find and remove the fighter
                    for gang in st.session_state.gangs:
                        if gang.gang_id == gang_id:
                            for i, fighter in enumerate(gang.gangers):
                                if fighter.ganger_id == fighter_id:
                                    gang.gangers.pop(i)
                                    break
                            break
                    
                    # Save changes
                    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                    log_info(f"Deleted fighter {selected_fighter.name} from {selected_gang.gang_name}")
                    
                    # Clear session state and redirect
                    if "selected_fighter_id" in st.session_state:
                        del st.session_state.selected_fighter_id
                    if "selected_gang_id" in st.session_state:
                        del st.session_state.selected_gang_id
                    
                    st.success(f"Fighter {selected_fighter.name} deleted")
                    st.switch_page("views/5_FighterManagement.py")  # Fixed path reference

# Call the function to display fighter details
show_fighter_details()
