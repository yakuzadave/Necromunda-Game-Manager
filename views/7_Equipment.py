import streamlit as st
from common import Equipment  # Import Equipment model from the common module
from pydantic import ValidationError

st.title("Equipment Management")

st.write("Manage your equipment library. Here you can add new equipment items, view the list, and remove items if needed.")

# Ensure the equipment list exists in session state.
if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []

# --- Populate Equipment from Gang Data ---
# Iterate over all gangs and their fighters. If a fighter has an equipment item not already in our equipment_list (by name),
# add it to the equipment_list.
if "gangs" in st.session_state:
    for gang in st.session_state.gangs:
        if hasattr(gang, "gangers"):
            for fighter in gang.gangers:
                if hasattr(fighter, "equipment"):
                    for eq in fighter.equipment:
                        # Check if an equipment item with the same name exists already (you can adjust this condition if needed)
                        if not any(existing.name == eq.name for existing in st.session_state.equipment_list):
                            st.session_state.equipment_list.append(eq)

# --- Form to add new equipment manually ---
with st.form("add_equipment_form"):
    equipment_name = st.text_input("Equipment Name")
    equipment_qty = st.number_input("Quantity", min_value=1, value=1)
    equipment_cost = st.number_input("Cost", min_value=0, value=0)
    equipment_traits = st.text_input("Traits (comma-separated)", value="")
    submit_equipment = st.form_submit_button("Add Equipment")

    if submit_equipment:
        if equipment_name:
            try:
                new_equipment = Equipment(
                    name=equipment_name,
                    qty=equipment_qty,
                    cost=equipment_cost,
                    traits=equipment_traits
                )
                # Check if equipment with the same name already exists
                if any(eq.name == new_equipment.name for eq in st.session_state.equipment_list):
                    st.warning(f"Equipment '{equipment_name}' already exists.")
                else:
                    st.session_state.equipment_list.append(new_equipment)
                    st.success(f"Added equipment: {equipment_name}")
            except ValidationError as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter an equipment name.")

st.markdown("---")
st.write("### Equipment Library")

# Display the equipment list as a table
if st.session_state.equipment_list:
    # Create a list of dictionaries for the dataframe view.
    eq_data = [
        {"Name": eq.name, "Quantity": eq.qty, "Cost": eq.cost, "Traits": eq.traits}
        for eq in st.session_state.equipment_list
    ]
    st.dataframe(eq_data, use_container_width=True)

    # Provide individual Remove buttons for each equipment item.
    st.write("#### Remove Equipment")
    for idx, eq in enumerate(st.session_state.equipment_list):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{eq.name}** (Qty: {eq.qty}, Cost: {eq.cost}, Traits: {eq.traits})")
        with col2:
            if st.button("Remove", key=f"remove_eq_{idx}"):
                st.session_state.equipment_list.pop(idx)
                st.success(f"Removed equipment: {eq.name}")
                st.experimental_rerun()
else:
    st.info("No equipment added yet.")
