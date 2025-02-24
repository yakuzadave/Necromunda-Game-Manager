import streamlit as st
import pandas as pd
from common import Gang  # Import the Gang model from common.py

st.title("Gangs Data Overview")

# Ensure gangs exist in session state.
if "gangs" not in st.session_state or not st.session_state.gangs:
    st.error("No gangs loaded. Please add some gangs first.")
    st.stop()

# Convert the list of Gang objects into a list of dictionaries with summary data.
data = []
for gang in st.session_state.gangs:
    data.append({
        "Gang ID": gang.gang_id,
        "Name": gang.gang_name,
        "Type": gang.gang_type,
        "Campaign": gang.campaign,
        "Credits": gang.credits,
        "Reputation": gang.reputation,
        "Territories": ", ".join(gang.territories) if gang.territories else "",
        "Fighters Count": len(gang.gangers) if hasattr(gang, "gangers") else 0,
    })

# Create a DataFrame from the list of dictionaries.
df = pd.DataFrame(data)

st.markdown("### Gangs Summary Table")
st.dataframe(df, use_container_width=True)

# Optionally allow the user to download the DataFrame as CSV.
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Gangs Data as CSV",
    data=csv,
    file_name="gangs_data.csv",
    mime="text/csv"
)
