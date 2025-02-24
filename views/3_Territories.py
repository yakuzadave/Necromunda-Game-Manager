import streamlit as st
import plotly.express as px
import pandas as pd

st.title("Campaign Territory Chart")

# Ensure campaign data is loaded.
if "gangs" not in st.session_state or "territories" not in st.session_state:
    st.error("Campaign data not found. Please load your campaign data first.")
    st.stop()

# Define a constant campaign name (this could be dynamic if you have metadata).
campaign_name = "Necromunda Campaign"

# Build a list of dictionaries for the sunburst chart.
# For each gang, we add a row for every territory that it controls.
data = []

for gang in st.session_state.gangs:
    # Find territories controlled by this gang.
    controlled_territories = [t for t in st.session_state.territories if t.controlled_by == gang.gang_name]

    # If the gang controls at least one territory, add each territory as a row.
    if controlled_territories:
        for territory in controlled_territories:
            data.append({
                "Campaign": campaign_name,
                "Gang": gang.gang_name,
                "Territory": territory.name
            })
    else:
        # If the gang controls no territory, add a row with a placeholder.
        data.append({
            "Campaign": campaign_name,
            "Gang": gang.gang_name,
            "Territory": "None"
        })

# Convert the list into a DataFrame.
df = pd.DataFrame(data)

# Create the sunburst chart.
fig = px.sunburst(
    df,
    path=["Campaign", "Gang", "Territory"],
    title="Campaign Hierarchy: Gangs & Territories",
    color="Gang"  # Optional: color by gang
)

st.plotly_chart(fig, use_container_width=True)
