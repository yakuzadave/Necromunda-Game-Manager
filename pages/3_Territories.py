import streamlit as st
import uuid

def show_territories():
    st.subheader("Territory Management")
    territory_name_input = st.text_input("New Territory Name", key="territory_name")
    territory_type_input = st.selectbox("Territory Type", [
        'Trading Post', 'Mineral Deposits', 'Archaeotech Site', 
        'Promethium Cache', 'Water Still', 'Manufactory'
    ], key="territory_type")
    if st.button("Add Territory"):
        if territory_name_input:
            try:
                new_territory = st.session_state.territories[0].__class__(
                    name=territory_name_input,
                    type=territory_type_input
                )
                st.session_state.territories.append(new_territory)
                st.success(f"Added territory '{territory_name_input}'!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Enter a territory name.")
    st.markdown("---")
    st.write("### Assign Territory to Gang")
    unassigned_territories = [t.name for t in st.session_state.territories if t.controlled_by is None]
    gang_names = [g.gang_name for g in st.session_state.gangs]
    if unassigned_territories and gang_names:
        territory_to_assign = st.selectbox("Select Territory", unassigned_territories, key="assign_territory")
        gang_to_assign = st.selectbox("Select Gang", gang_names, key="assign_gang")
        if st.button("Assign Territory"):
            # Here, you would call your assign_territory() utility function.
            # For example:
            for territory in st.session_state.territories:
                if territory.name == territory_to_assign:
                    territory.controlled_by = gang_to_assign
                    break
            for gang in st.session_state.gangs:
                if gang.gang_name == gang_to_assign and territory_to_assign not in gang.territories:
                    gang.territories.append(territory_to_assign)
                    break
            st.success(f"Assigned {territory_to_assign} to {gang_to_assign}")
    else:
        st.info("Ensure unassigned territories and registered gangs exist.")

show_territories()
