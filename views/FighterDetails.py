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
from utils.logger import log_info, log_error, log_debug

def show_fighter_details():
    """Display detailed fighter information and edit options"""
    
    # Check if selected fighter data is available
    if "selected_fighter_id" not in st.session_state or "selected_gang_id" not in st.session_state:
        st.error("No fighter selected. Please select a fighter from the Fighters page.")
        if st.button("Return to Fighters"):
            st.switch_page("views/5_FighterManagement.py")
        return
    
    # Get the selected gang and fighter
    selected_gang = None
    selected_fighter = None
    
    # Find the gang and fighter in session state
    for gang in st.session_state.gangs:
        if gang.gang_id == st.session_state.selected_gang_id:
            selected_gang = gang
            for fighter in gang.gangers:
                if fighter.ganger_id == st.session_state.selected_fighter_id:
                    selected_fighter = fighter
                    break
            break
    
    if not selected_gang or not selected_fighter:
        st.error("Selected fighter or gang not found.")
        if st.button("Return to Fighters"):
            st.switch_page("views/5_FighterManagement.py")
        return
    
    # ---- Show Fighter Details ----
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.title(f"{selected_fighter.name}")
        st.markdown(f"**{selected_fighter.type}** from ***{selected_gang.gang_name}***")
        
        # Status pills
        status_color = "green"
        if "Injured" in selected_fighter.status:
            status_color = "orange"
        if "Dead" in selected_fighter.status:
            status_color = "red"
        st.markdown(f"<span style='background-color:{status_color};padding:5px;border-radius:5px;color:white'>{selected_fighter.status}</span>", unsafe_allow_html=True)
        
        # Visualization of character stats using a radar chart
        categories = ['M', 'WS', 'BS', 'S', 'T', 'W', 'I', 'A', 'Ld', 'Cl', 'Wil', 'Int']
        values = [
            selected_fighter.m, selected_fighter.ws, selected_fighter.bs, 
            selected_fighter.s, selected_fighter.t, selected_fighter.w,
            selected_fighter.i, selected_fighter.a, selected_fighter.ld,
            selected_fighter.cl, selected_fighter.wil, selected_fighter.intelligence
        ]
        
        # Create radar chart
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=selected_fighter.name,
            line_color='darkblue',
            fillcolor='rgba(65, 105, 225, 0.4)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) + 2]
                )
            ),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Display fighter image
        if selected_fighter.image:
            try:
                image = Image.open(io.BytesIO(base64.b64decode(selected_fighter.image.split(',')[1])))
                st.image(image, caption=f"{selected_fighter.name}", use_column_width=True)
            except Exception as e:
                st.warning(f"Could not load fighter image: {e}")
                # Use placeholder image
                st.image("https://via.placeholder.com/300x400?text=No+Image", caption="No image available")
        else:
            # Use placeholder image
            st.image("https://via.placeholder.com/300x400?text=No+Image", caption="No image available")
            
        # Upload new image
        with st.expander("Upload New Image"):
            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                try:
                    # Process and save the image
                    bytes_data = uploaded_file.getvalue()
                    image_str = f"data:image/jpeg;base64,{base64.b64encode(bytes_data).decode()}"
                    
                    # Update the fighter image in session state
                    for g in st.session_state.gangs:
                        if g.gang_id == selected_gang.gang_id:
                            for f in g.gangers:
                                if f.ganger_id == selected_fighter.ganger_id:
                                    f.image = image_str
                                    break
                            break
                    
                    # Save changes
                    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                    st.success("Image updated!")
                    # Refresh page
                    st.rerun()
                except Exception as e:
                    log_error(f"Error uploading image: {e}", exc_info=True)
                    st.error(f"Error uploading image: {str(e)}")
    
    # Fighter stats in a table
    st.subheader("Stats")
    stats_df = pd.DataFrame({
        "Attribute": ["Movement", "Weapon Skill", "Ballistic Skill", "Strength", "Toughness", 
                     "Wounds", "Initiative", "Attacks", "Leadership", "Cool", "Willpower", "Intelligence"],
        "Value": [selected_fighter.m, selected_fighter.ws, selected_fighter.bs, 
                 selected_fighter.s, selected_fighter.t, selected_fighter.w,
                 selected_fighter.i, selected_fighter.a, selected_fighter.ld,
                 selected_fighter.cl, selected_fighter.wil, selected_fighter.intelligence],
        "Code": ["M", "WS", "BS", "S", "T", "W", "I", "A", "Ld", "Cl", "Wil", "Int"]
    })
    
    st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    # Fighter career
    st.subheader("Career")
    career_col1, career_col2, career_col3 = st.columns(3)
    with career_col1:
        st.metric("Experience", selected_fighter.xp)
    with career_col2:
        st.metric("Kills", selected_fighter.kills)
    with career_col3:
        st.metric("Advancements", selected_fighter.advance_count)
        
    # Skills and abilities
    if selected_fighter.skills:
        with st.expander("Skills & Abilities", expanded=True):
            for skill in selected_fighter.skills:
                st.markdown(f"- **{skill}**")
    
    # Injuries
    if selected_fighter.injuries:
        with st.expander("Injuries", expanded=True):
            for injury in selected_fighter.injuries:
                st.markdown(f"- **{injury}**")
    
    # Equipment
    st.subheader("Equipment")
    if selected_fighter.equipment:
        equipment_data = []
        for equip in selected_fighter.equipment:
            equipment_data.append({
                "Item": equip.name,
                "Qty": equip.qty,
                "Cost": equip.cost,
                "Traits": equip.traits
            })
        equipment_df = pd.DataFrame(equipment_data)
        st.dataframe(equipment_df, use_container_width=True, hide_index=True)
    else:
        st.info("No equipment assigned to this fighter.")
    
    # Fighter notes with editing capability
    st.subheader("Notes")
    new_notes = st.text_area("Edit fighter notes:", value=selected_fighter.notes, height=150)
    
    if new_notes != selected_fighter.notes:
        if st.button("Save Notes"):
            # Update fighter notes in session state
            for g in st.session_state.gangs:
                if g.gang_id == selected_gang.gang_id:
                    for f in g.gangers:
                        if f.ganger_id == selected_fighter.ganger_id:
                            f.notes = new_notes
                            f.datetime_updated = datetime.now().isoformat()
                            break
                    break
            
            # Save changes
            save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
            st.success("Notes updated!")
            log_info(f"Updated notes for fighter {selected_fighter.name}")
            
    # Status update
    st.subheader("Update Status")
    
    status_options = ["Active", "Injured", "Dead", "Captured", "Missing"]
    new_status = st.selectbox("Select Status:", status_options, 
                             index=status_options.index(selected_fighter.status) if selected_fighter.status in status_options else 0)
    
    if new_status != selected_fighter.status:
        if st.button("Update Status"):
            # Update fighter status in session state
            for g in st.session_state.gangs:
                if g.gang_id == selected_gang.gang_id:
                    for f in g.gangers:
                        if f.ganger_id == selected_fighter.ganger_id:
                            f.status = new_status
                            f.datetime_updated = datetime.now().isoformat()
                            break
                    break
            
            # Save changes
            save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
            st.success(f"Status updated to {new_status}!")
            log_info(f"Updated status for fighter {selected_fighter.name} to {new_status}")
            
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Fighters"):
            st.switch_page("views/5_FighterManagement.py")
    with col2:
        if st.button("Go to Gang"):
            st.session_state.current_gang = selected_gang
            st.switch_page("views/2_Gangs.py")

# Call the function to display fighter details
show_fighter_details()
