
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

# Create tabs for different views
tab1, tab2 = st.tabs(["Sunburst Chart", "Territory Table"])

with tab1:
    # Create the sunburst chart.
    fig = px.sunburst(
        df,
        path=["Campaign", "Gang", "Territory"],
        title="Campaign Hierarchy: Gangs & Territories",
        color="Gang"  # Optional: color by gang
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Territory Overview")
    
    # Create territory table data
    territory_data = []
    for territory in st.session_state.territories:
        territory_data.append({
            "Territory Name": territory.name,
            "Type": territory.type,
            "Controlled By": territory.controlled_by if territory.controlled_by else "Unclaimed",
            "Location": f"X: {territory.x:.2f}, Y: {territory.y:.2f}" if territory.x is not None and territory.y is not None else "No location set"
        })
    
    # Convert to DataFrame and display
    territory_df = pd.DataFrame(territory_data)
    st.dataframe(
        territory_df,
        column_config={
            "Territory Name": st.column_config.TextColumn("Territory Name", width="medium"),
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Controlled By": st.column_config.TextColumn("Controlled By", width="medium"),
            "Location": st.column_config.TextColumn("Location", width="medium")
        },
        hide_index=True
    )
