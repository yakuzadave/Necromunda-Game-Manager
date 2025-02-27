import streamlit as st

from utils.logger import log_error
from utils.map_utils import calculate_territory_adjacency
from common import save_data

def render_advanced_territory():
    """Render the advanced territory management tab content"""
    st.header("Advanced Territory Management")
    
    # Territory network visualization
    st.subheader("Territory Network")
    st.write("Analyze how territories are connected to each other.")
    
    # Calculate adjacency for visualization
    adjacency = calculate_territory_adjacency(st.session_state.territories) if st.session_state.territories else {}
    
    if adjacency:
        # Create network data
        nodes = []
        edges = []
        
        for territory_name, adjacent_list in adjacency.items():
            source = next((t for t in st.session_state.territories if t.name == territory_name), None)
            if source:
                controlled_by = source.controlled_by or "Unclaimed"
                nodes.append(f"{territory_name} ({controlled_by})")
                
                for adj in adjacent_list:
                    edges.append((
                        f"{territory_name} ({controlled_by})",
                        f"{adj['name']} ({adj['controlled_by'] or 'Unclaimed'})",
                        f"{adj['distance']:.1f}"
                    ))
        
        # Generate Mermaid diagram code
        if nodes and edges:
            try:
                from streamlit_mermaid import st_mermaid
                
                # Prepare mermaid graph
                mermaid_code = ["graph TD"]
                
                # Add nodes
                for node in nodes:
                    safe_id = "".join([c if c.isalnum() else "_" for c in node])
                    mermaid_code.append(f"    {safe_id}[\"{node}\"]")
                
                # Add edges
                for source, target, label in edges:
                    source_id = "".join([c if c.isalnum() else "_" for c in source])
                    target_id = "".join([c if c.isalnum() else "_" for c in target])
                    mermaid_code.append(f"    {source_id} -- \"{label}\" --> {target_id}")
                
                # Render diagram
                st_mermaid("\n".join(mermaid_code))
            except Exception as e:
                st.warning("Could not generate network visualization. Install streamlit-mermaid with: pip install streamlit-mermaid")
                st.code("\n".join(mermaid_code), language="markdown")
        else:
            st.info("Not enough connected territories to generate a network.")
    else:
        st.info("Add more territories with coordinates to generate a network visualization.")
    
    # Territory batch operations
    st.subheader("Batch Operations")
    st.write("Perform operations on multiple territories at once.")
    
    col_batch1, col_batch2 = st.columns(2)
    
    with col_batch1:
        # Batch faction assignment
        st.write("Assign multiple territories to a faction:")
        selected_territories = st.multiselect(
            "Select territories",
            options=[t.name for t in st.session_state.territories]
        )
        
        if selected_territories:
            gang_options = ["Unclaimed"] + [g.gang_name for g in st.session_state.get("gangs", [])]
            batch_faction = st.selectbox("Assign to faction", options=gang_options)
            
            if st.button("Assign Selected Territories"):
                try:
                    # Process unclaimed selection
                    controller = None if batch_faction == "Unclaimed" else batch_faction
                    
                    # Update territory controllers
                    for territory in st.session_state.territories:
                        if territory.name in selected_territories:
                            territory.controlled_by = controller
                    
                    # If assigning to a gang, update gang's territory list
                    if controller:
                        for gang in st.session_state.gangs:
                            if gang.gang_name == controller:
                                for territory_name in selected_territories:
                                    if territory_name not in gang.territories:
                                        gang.territories.append(territory_name)
                    
                    # Save changes
                    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                    st.success(f"Assigned {len(selected_territories)} territories to {batch_faction}")
                    st.rerun()
                except Exception as e:
                    log_error(f"Error in batch assign: {e}", exc_info=True)
                    st.error(f"Error assigning territories: {str(e)}")
    
    with col_batch2:
        # Batch type assignment
        st.write("Set territory type for multiple territories:")
        territory_type_options = sorted(set(t.type for t in st.session_state.territories))
        batch_type = st.selectbox("New Territory Type", options=territory_type_options)
        
        if selected_territories and batch_type and st.button("Set Territory Type"):
            try:
                # Update territory types
                for territory in st.session_state.territories:
                    if territory.name in selected_territories:
                        territory.type = batch_type
                        
                # Save changes
                save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                st.success(f"Updated type for {len(selected_territories)} territories to {batch_type}")
                st.rerun()
            except Exception as e:
                log_error(f"Error in batch type update: {e}", exc_info=True)
                st.error(f"Error updating territory types: {str(e)}")