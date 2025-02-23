import streamlit as st
from pydantic import BaseModel, Field, ValidationError
import uuid

# Define a simple Equipment model.
class Equipment(BaseModel):
    equipment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    qty: int
    cost: int = 0
    traits: str = ""  # Comma-separated traits

# Initialize the equipment list in session state if not already present.
if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []

st.title("Equipment Management")

st.write("Manage your equipment library. Here you can add new equipment items and view the current list.")

# Form to add new equipment.
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
                st.session_state.equipment_list.append(new_equipment)
                st.success(f"Added equipment: {equipment_name}")
            except ValidationError as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter an equipment name.")

st.markdown("---")
st.write("### Equipment Library")
if st.session_state.equipment_list:
    for eq in st.session_state.equipment_list:
        st.write(f"**{eq.name}** (Qty: {eq.qty}, Cost: {eq.cost}, Traits: {eq.traits})")
else:
    st.info("No equipment added yet.")
