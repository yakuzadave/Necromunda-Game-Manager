import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import plotly.express as px

from common import Gang, Equipment, save_data
from utils.logger import log_info, log_error, log_debug

def show_equipment_management():
    """Display equipment management interface"""
    
    st.title("Equipment Management")
    
    # Initialize equipment list in session state if not present
    if "equipment_list" not in st.session_state:
        st.session_state.equipment_list = []
    
    # Create tabs for different equipment management views
    tab1, tab2, tab3 = st.tabs(["Gang Equipment", "Equipment Catalog", "Trading Post"])
    
    # ------ Gang Equipment Tab ------
    with tab1:
        st.subheader("Gang Equipment")
        
        # Gang selector
        gangs = st.session_state.gangs
        if not gangs:
            st.info("No gangs available. Create a gang first.")
        else:
            gang_names = [g.gang_name for g in gangs]
            selected_gang_name = st.selectbox("Select Gang", gang_names)
            
            # Find selected gang object
            selected_gang = None
            for g in gangs:
                if g.gang_name == selected_gang_name:
                    selected_gang = g
                    break
            
            if selected_gang:
                # Display gang stash
                st.markdown(f"### {selected_gang.gang_name}'s Stash")
                st.markdown(f"**Credits:** ⓒ{selected_gang.credits}")
                
                if selected_gang.stash:
                    # Convert stash items to dataframe for display
                    stash_data = []
                    for item in selected_gang.stash:
                        stash_data.append({
                            "Item ID": item.equipment_id,
                            "Name": item.name,
                            "Quantity": item.qty,
                            "Cost": item.cost,
                            "Traits": item.traits
                        })
                    
                    stash_df = pd.DataFrame(stash_data)
                    
                    # Show the table with edit/delete capabilities
                    edited_df = st.data_editor(
                        stash_df,
                        column_config={
                            "Name": st.column_config.TextColumn("Name"),
                            "Quantity": st.column_config.NumberColumn("Quantity", min_value=0, step=1),
                            "Cost": st.column_config.NumberColumn("Cost", min_value=0),
                            "Traits": st.column_config.TextColumn("Traits"),
                            "Item ID": st.column_config.TextColumn("Item ID", disabled=True),
                        },
                        hide_index=True,
                        num_rows="dynamic",
                        use_container_width=True,
                        key="gang_equipment_table"
                    )
                    
                    # Save changes button
                    if st.button("Save Changes to Stash"):
                        try:
                            # Convert edited dataframe back to Equipment objects
                            new_stash = []
                            for _, row in edited_df.iterrows():
                                if pd.notna(row["Name"]) and row["Name"].strip():  # Only add items with valid names
                                    new_item = Equipment(
                                        equipment_id=row["Item ID"] if pd.notna(row["Item ID"]) else str(uuid.uuid4()),
                                        name=row["Name"],
                                        qty=int(row["Quantity"]) if pd.notna(row["Quantity"]) else 1,
                                        cost=int(row["Cost"]) if pd.notna(row["Cost"]) else 0,
                                        traits=row["Traits"] if pd.notna(row["Traits"]) else ""
                                    )
                                    new_stash.append(new_item)
                            
                            # Update gang stash
                            for g in st.session_state.gangs:
                                if g.gang_id == selected_gang.gang_id:
                                    g.stash = new_stash
                                    break
                            
                            # Save data
                            save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                            st.success("Stash updated successfully!")
                            log_info(f"Updated stash for gang {selected_gang.gang_name}")
                            
                        except Exception as e:
                            log_error(f"Error saving stash: {e}", exc_info=True)
                            st.error(f"Error saving stash: {str(e)}")
                else:
                    st.info("This gang has no equipment in their stash.")
                    
                # Add new equipment item form
                with st.form("add_equipment_form"):
                    st.subheader("Add New Equipment")
                    new_item_name = st.text_input("Item Name")
                    new_item_qty = st.number_input("Quantity", min_value=1, value=1, step=1)
                    new_item_cost = st.number_input("Cost", min_value=0, value=0, step=5)
                    new_item_traits = st.text_area("Traits/Description")
                    
                    submit_new = st.form_submit_button("Add to Stash")
                    
                    if submit_new and new_item_name:
                        try:
                            # Create new equipment item
                            new_item = Equipment(
                                equipment_id=str(uuid.uuid4()),
                                name=new_item_name,
                                qty=new_item_qty,
                                cost=new_item_cost,
                                traits=new_item_traits
                            )
                            
                            # Add to gang stash
                            for g in st.session_state.gangs:
                                if g.gang_id == selected_gang.gang_id:
                                    if not g.stash:
                                        g.stash = []
                                    g.stash.append(new_item)
                                    break
                            
                            # Save data
                            save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                            st.success("Item added to stash!")
                            log_info(f"Added {new_item_name} to {selected_gang.gang_name}'s stash")
                            st.rerun()
                            
                        except Exception as e:
                            log_error(f"Error adding item to stash: {e}", exc_info=True)
                            st.error(f"Error adding item: {str(e)}")
                
                # Equip fighter section
                st.subheader("Equip Fighter")
                if selected_gang.gangers:
                    # Fighter selector
                    fighter_names = [f.name for f in selected_gang.gangers]
                    selected_fighter_name = st.selectbox("Select Fighter", fighter_names)
                    
                    # Get selected fighter
                    selected_fighter = None
                    for f in selected_gang.gangers:
                        if f.name == selected_fighter_name:
                            selected_fighter = f
                            break
                    
                    if selected_fighter and selected_gang.stash:
                        # Display current equipment
                        st.markdown(f"#### {selected_fighter.name}'s Current Equipment")
                        if selected_fighter.equipment:
                            fighter_equip_data = []
                            for item in selected_fighter.equipment:
                                fighter_equip_data.append({
                                    "Name": item.name,
                                    "Quantity": item.qty,
                                    "Cost": item.cost,
                                    "Traits": item.traits
                                })
                            st.table(pd.DataFrame(fighter_equip_data))
                        else:
                            st.info("This fighter has no equipment.")
                        
                        # Equip from stash form
                        with st.form("equip_from_stash"):
                            st.subheader("Equip from Stash")
                            stash_items = [item.name for item in selected_gang.stash]
                            item_to_equip = st.selectbox("Select Item", stash_items, key="equip_item")
                            qty_to_equip = st.number_input("Quantity", min_value=1, value=1, max_value=10, step=1, key="equip_qty")
                            
                            equip_submit = st.form_submit_button("Equip Fighter")
                            
                            if equip_submit:
                                try:
                                    # Find the item in stash
                                    stash_item = None
                                    for item in selected_gang.stash:
                                        if item.name == item_to_equip:
                                            stash_item = item
                                            break
                                    
                                    if stash_item and stash_item.qty >= qty_to_equip:
                                        # Add to fighter's equipment
                                        new_equipment = Equipment(
                                            equipment_id=str(uuid.uuid4()),
                                            name=stash_item.name,
                                            qty=qty_to_equip,
                                            cost=stash_item.cost,
                                            traits=stash_item.traits
                                        )
                                        
                                        # Update session state
                                        for g in st.session_state.gangs:
                                            if g.gang_id == selected_gang.gang_id:
                                                for f in g.gangers:
                                                    if f.ganger_id == selected_fighter.ganger_id:
                                                        if not f.equipment:
                                                            f.equipment = []
                                                        
                                                        # Check if fighter already has this item
                                                        has_item = False
                                                        for idx, equip in enumerate(f.equipment):
                                                            if equip.name == stash_item.name:
                                                                has_item = True
                                                                f.equipment[idx].qty += qty_to_equip
                                                                break
                                                        
                                                        if not has_item:
                                                            f.equipment.append(new_equipment)
                                                        
                                                        # Update fighter's datetime
                                                        f.datetime_updated = datetime.now().isoformat()
                                                        break
                                                    
                                                # Update stash quantity
                                                for idx, item in enumerate(g.stash):
                                                    if item.equipment_id == stash_item.equipment_id:
                                                        if item.qty == qty_to_equip:
                                                            # Remove item if using all
                                                            g.stash.pop(idx)
                                                        else:
                                                            # Reduce quantity
                                                            g.stash[idx].qty -= qty_to_equip
                                                        break
                                                break
                                        
                                        # Save data
                                        save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                                        st.success(f"Equipped {qty_to_equip}x {stash_item.name} to {selected_fighter.name}")
                                        log_info(f"Equipped {stash_item.name} to {selected_fighter.name}")
                                        st.rerun()
                                    else:
                                        st.error("Not enough items in stash.")
                                        
                                except Exception as e:
                                    log_error(f"Error equipping fighter: {e}", exc_info=True)
                                    st.error(f"Error equipping fighter: {str(e)}")
                    else:
                        st.info("No equipment available in stash to equip.")
                else:
                    st.info("This gang has no fighters to equip.")

    # ------ Equipment Catalog Tab ------
    with tab2:
        st.subheader("Equipment Catalog")
        # Placeholder for equipment catalog functionality
        st.info("Equipment catalog feature coming soon...")

    # ------ Trading Post Tab ------
    with tab3:
        st.subheader("Trading Post")
        # Placeholder for trading post functionality
        st.info("Trading post feature coming soon...")

# Call the function to display the equipment management interface
show_equipment_management()
