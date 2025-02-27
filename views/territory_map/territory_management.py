import random
import pandas as pd
import streamlit as st

from common import Territory, save_data
from utils.logger import log_info, log_error

def render_territory_management():
    """Render the territory management tab content"""
    st.header("Territory Management")
    
    # --------------------- Territory Management Interface ---------------------
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add New Territory")
        
        territory_name_input = st.text_input("New Territory Name", key="territory_name")
        territory_type_input = st.selectbox("Territory Type", [
            "Trading Post", "Mineral Deposits", "Archaeotech Site", 
            "Promethium Cache", "Water Still", "Manufactory",
            "Holestead", "Settlement", "Mine"
        ], key="territory_type")
        
        # Get existing gang names from session state for dropdown
        gang_options = ["Unclaimed"] + [gang.gang_name for gang in st.session_state.get("gangs", [])]
        new_controlled_by = st.selectbox("Controlled By", gang_options, key="new_controlled_by")
        
        # Use clicked coordinates if available, otherwise use random coordinates
        x_val = st.session_state.get("last_clicked_x", random.uniform(0, 4096))
        y_val = st.session_state.get("last_clicked_y", random.uniform(0, 4096))
        
        new_x = st.number_input("X Coordinate", value=float(x_val), key="new_x")
        new_y = st.number_input("Y Coordinate", value=float(y_val), key="new_y")
        
        if st.button("Add Territory"):
            if territory_name_input:
                # Handle "Unclaimed" selection
                controller = None if new_controlled_by == "Unclaimed" else new_controlled_by
                
                new_territory = Territory(
                    name=territory_name_input,
                    type=territory_type_input,
                    controlled_by=controller,
                    x=new_x,
                    y=new_y
                )
                st.session_state.territories.append(new_territory)
                save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                log_info(f"Added new territory: {territory_name_input}")
                
                # Set flag to indicate a new territory was created (for auto-fitting)
                st.session_state.new_territory_created = True
                
                st.success(f"Added territory: {territory_name_input}")
                st.session_state.last_clicked_x = None
                st.session_state.last_clicked_y = None
                st.rerun()
            else:
                st.error("Please enter a territory name.")
    
    with col2:
        st.subheader("Territory Assignment")
        
        # Territory Assignment Section
        unassigned_territories = [t.name for t in st.session_state.territories if not t.controlled_by]
        gang_names = [g.gang_name for g in st.session_state.gangs] if "gangs" in st.session_state else []
        
        if unassigned_territories and gang_names:
            territory_to_assign = st.selectbox("Select Territory", unassigned_territories, key="assign_territory")
            gang_to_assign = st.selectbox("Select Gang", gang_names, key="assign_gang")
            
            if st.button("Assign Territory"):
                for territory in st.session_state.territories:
                    if territory.name == territory_to_assign:
                        territory.controlled_by = gang_to_assign
                        break
                for gang in st.session_state.gangs:
                    if gang.gang_name == gang_to_assign and territory_to_assign not in gang.territories:
                        gang.territories.append(territory_to_assign)
                        break
                save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                log_info(f"Assigned {territory_to_assign} to {gang_to_assign}")
                st.success(f"Assigned {territory_to_assign} to {gang_to_assign}")
                st.rerun()
        else:
            st.info("Ensure unassigned territories and registered gangs exist.")
    
    # Display current territories with edit/delete options
    st.subheader("Current Territories")
    territory_df = pd.DataFrame([{
        "Name": t.name,
        "Type": t.type,
        "Controlled By": t.controlled_by if t.controlled_by else "Unclaimed",
        "X": t.x,
        "Y": t.y
    } for t in st.session_state.territories])
    
    edited_df = st.data_editor(
        territory_df,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        column_config={
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Type": st.column_config.SelectboxColumn(
                "Type",
                options=[
                    "Trading Post", "Mineral Deposits", "Archaeotech Site", 
                    "Promethium Cache", "Water Still", "Manufactory",
                    "Holestead", "Settlement", "Mine"
                ],
                width="medium"
            ),
            "Controlled By": st.column_config.TextColumn("Controlled By", width="medium"),
            "X": st.column_config.NumberColumn("X", format="%.1f", width="small"),
            "Y": st.column_config.NumberColumn("Y", format="%.1f", width="small")
        }
    )
    
    # Apply changes from the editor
    if not edited_df.equals(territory_df):
        try:
            # Update territories in session state
            updated_territories = []
            for _, row in edited_df.iterrows():
                territory = Territory(
                    name=row["Name"],
                    type=row["Type"],
                    controlled_by=None if row["Controlled By"] == "Unclaimed" else row["Controlled By"],
                    x=float(row["X"]),
                    y=float(row["Y"])
                )
                updated_territories.append(territory)
            
            st.session_state.territories = updated_territories
            save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
            log_info("Updated territories from data editor")
            st.success("Territory data updated")
        except Exception as e:
            log_error(f"Error updating territories: {str(e)}", exc_info=True)
            st.error(f"Error updating territories: {str(e)}")

    # Add an "Export Territories" button to allow users to download territory data
    st.subheader("Export/Import Territory Data")
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        if st.button("Export Territories as CSV"):
            try:
                # Create a dataframe with the territory data
                export_data = []
                for t in st.session_state.territories:
                    export_data.append({
                        "Name": t.name,
                        "Type": t.type,
                        "Controlled By": t.controlled_by if t.controlled_by else "",
                        "X": t.x,
                        "Y": t.y,
                        "Lat": t.lat,
                        "Lng": t.lng,
                        "Elevation": t.elevation
                    })
                
                if export_data:
                    df = pd.DataFrame(export_data)
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name="necromunda_territories.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No territories to export")
            except Exception as e:
                log_error(f"Error exporting territories: {e}", exc_info=True)
                st.error(f"Error exporting territories: {str(e)}")
    
    with col_exp2:
        # Add an "Import Territories from CSV" option
        uploaded_csv = st.file_uploader("Import territories from CSV", type=["csv"])
        if uploaded_csv is not None:
            try:
                df = pd.read_csv(uploaded_csv)
                if st.button("Process Imported Territories"):
                    # Convert DataFrame back to Territory objects
                    imported_territories = []
                    for _, row in df.iterrows():
                        # Handle null values
                        controlled_by = row.get("Controlled By", None)
                        if pd.isna(controlled_by):
                            controlled_by = None
                        
                        x = row.get("X", None)
                        if pd.isna(x):
                            x = None
                            
                        y = row.get("Y", None)
                        if pd.isna(y):
                            y = None
                            
                        lat = row.get("Lat", None)
                        if pd.isna(lat):
                            lat = None
                            
                        lng = row.get("Lng", None)
                        if pd.isna(lng):
                            lng = None
                            
                        elevation = row.get("Elevation", None)
                        if pd.isna(elevation):
                            elevation = None
                        
                        territory = Territory(
                            name=row["Name"],
                            type=row["Type"],
                            controlled_by=controlled_by,
                            x=x,
                            y=y,
                            lat=lat,
                            lng=lng,
                            elevation=elevation
                        )
                        imported_territories.append(territory)
                    
                    # Update session state with imported territories
                    st.session_state.territories = imported_territories
                    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                    log_info(f"Imported {len(imported_territories)} territories")
                    st.success(f"Imported {len(imported_territories)} territories")
                    st.rerun()
            except Exception as e:
                log_error(f"Error importing territories: {e}", exc_info=True)
                st.error(f"Error importing territories: {str(e)}")