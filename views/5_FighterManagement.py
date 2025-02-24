import streamlit as st
import pandas as pd
from datetime import datetime
from pydantic import ValidationError
from common import Gang, GangFighter, Equipment, save_data

st.title("Fighter Management")

# --- Ensure a gang exists ---
if "gangs" not in st.session_state or not st.session_state.gangs:
    st.error("No gangs loaded. Please add a gang first.")
    st.stop()

# --- Select a Gang ---
gang_options = {gang.gang_name: gang for gang in st.session_state.gangs}
selected_gang_name = st.selectbox("Select a Gang", list(gang_options.keys()))
selected_gang = gang_options[selected_gang_name]

# --- Select a Fighter from the Selected Gang ---
if selected_gang.gangers:
    fighter_options = {
        fighter.name: fighter
        for fighter in selected_gang.gangers
    }
    selected_fighter_name = st.selectbox("Select a Fighter",
                                         list(fighter_options.keys()))
    selected_fighter = fighter_options[selected_fighter_name]
else:
    st.info("No fighters available for this gang. Please add a fighter first.")
    st.stop()

st.markdown("## Edit Fighter Details")

# Prepare a dictionary of fighter attributes for editing.
# We include a subset of fields that are safe to edit.
editable_fields = {
    "name":
    selected_fighter.name,
    "type":
    selected_fighter.type,
    "m":
    selected_fighter.m,
    "ws":
    selected_fighter.ws,
    "bs":
    selected_fighter.bs,
    "s":
    selected_fighter.s,
    "t":
    selected_fighter.t,
    "w":
    selected_fighter.w,
    "i":
    selected_fighter.i,
    "a":
    selected_fighter.a,
    "ld":
    selected_fighter.ld,
    "cl":
    selected_fighter.cl,
    "wil":
    selected_fighter.wil,
    "intelligence":
    selected_fighter.intelligence,
    "cost":
    selected_fighter.cost,
    "xp":
    selected_fighter.xp,
    "kills":
    selected_fighter.kills,
    "advance_count":
    selected_fighter.advance_count,
    "status":
    selected_fighter.status,
    "notes":
    selected_fighter.notes,
    # For equipment and injuries, join list elements into a comma-separated string.
    "equipment":
    ", ".join(eq.name for eq in selected_fighter.equipment)
    if selected_fighter.equipment else "",
    "injuries":
    ", ".join(selected_fighter.injuries) if selected_fighter.injuries else "",
}

# Convert the dictionary to a one-row DataFrame for editing.
df = pd.DataFrame([editable_fields])

st.write("Edit fighter details below:")
edited_df = st.data_editor(df, num_rows="fixed", use_container_width=True)

# Button to save changes back to the fighter model
if st.button("Save Changes"):
    updated_values = edited_df.iloc[0].to_dict()
    # Update fighter's basic stats
    for field in [
            "name", "type", "m", "ws", "bs", "s", "t", "w", "i", "a", "ld",
            "cl", "wil", "intelligence", "cost", "xp", "kills",
            "advance_count", "status", "notes"
    ]:
        try:
            setattr(selected_fighter, field, updated_values[field])
        except Exception as e:
            st.error(f"Error updating field {field}: {e}")
    # For equipment and injuries, split the string by commas (if non-empty)
    if updated_values.get("equipment", "").strip():
        equipment_names = [
            name.strip() for name in updated_values["equipment"].split(",")
            if name.strip()
        ]
        # Optionally, you could update quantities or create new Equipment objects here.
        # For simplicity, we update equipment as a list of Equipment objects with default quantity 1.
        selected_fighter.equipment = [
            Equipment(name=name, qty=1) for name in equipment_names
        ]
    else:
        selected_fighter.equipment = []

    if updated_values.get("injuries", "").strip():
        injuries_list = [
            inj.strip() for inj in updated_values["injuries"].split(",")
            if inj.strip()
        ]
        selected_fighter.injuries = injuries_list
    else:
        selected_fighter.injuries = []

    # Update last updated timestamp
    selected_fighter.datetime_updated = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S")

    # Persist changes using the save_data function
    save_data(st.session_state.gangs, st.session_state.territories,
              st.session_state.battles)

    st.success(f"Fighter '{selected_fighter.name}' updated successfully!")
    st.experimental_rerun()

# --- Display Current Fighter Details for Confirmation ---
st.markdown("### Current Fighter Details")
st.markdown(f"**Name:** {selected_fighter.name}")
st.markdown(f"**Type:** {selected_fighter.type}")
st.markdown(
    f"**M:** {selected_fighter.m} | **WS:** {selected_fighter.ws} | **BS:** {selected_fighter.bs}"
)
st.markdown(
    f"**S:** {selected_fighter.s} | **T:** {selected_fighter.t} | **W:** {selected_fighter.w}"
)
st.markdown(f"**I:** {selected_fighter.i} | **A:** {selected_fighter.a}")
st.markdown(
    f"**Ld:** {selected_fighter.ld} | **Cl:** {selected_fighter.cl} | **Wil:** {selected_fighter.wil}"
)
st.markdown(f"**Int:** {selected_fighter.intelligence}")
st.markdown(
    f"**Cost:** {selected_fighter.cost} | **XP:** {selected_fighter.xp}")
st.markdown(
    f"**Kills:** {selected_fighter.kills} | **Advance Count:** {selected_fighter.advance_count}"
)
st.markdown("---")
st.markdown("#### Equipment")
if selected_fighter.equipment:
    for eq in selected_fighter.equipment:
        st.markdown(f"- **{eq.name}** (Qty: {eq.qty})")
else:
    st.markdown("_None_")
st.markdown("#### Injuries")
if selected_fighter.injuries:
    st.markdown(", ".join(selected_fighter.injuries))
else:
    st.markdown("_None_")
