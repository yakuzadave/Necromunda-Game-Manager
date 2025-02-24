import streamlit as st
import pandas as pd
from common import Gang  # Import the Gang model from common.py

st.title("Gangs Data Overview")

# Ensure gangs exist in session state.
if "gangs" not in st.session_state or not st.session_state.gangs:
    st.error("No gangs loaded. Please add some gangs first.")
    st.stop()

@st.cache_data(ttl=300)  # Cache gang summary data for 5 minutes
def create_gang_summary(_gangs):
    data = []
    for gang in _gangs:
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
    return data

# Create a DataFrame from the list of dictionaries
data = create_gang_summary(st.session_state.gangs)
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
