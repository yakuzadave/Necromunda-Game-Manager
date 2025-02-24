import streamlit as st
import plotly.express as px
import pandas as pd

def show_abstract_map():
    st.title("Abstract Territory Map")

    # Get territories from session state.
    territories = st.session_state.get("territories", [])

    # Prepare data for Plotly. If a territory doesn't have x/y coordinates,
    # generate fallback positions (for example, spaced out based on index).
    data = []
    for idx, territory in enumerate(territories):
        # Use provided coordinates or fallback values.
        x = territory.x if territory.x is not None else 100 * (idx % 5)
        y = territory.y if territory.y is not None else 100 * (idx // 5)
        controlled_by = territory.controlled_by if territory.controlled_by else "Unassigned"
        data.append({
            "Territory": territory.name,
            "X": x,
            "Y": y,
            "Controlled By": controlled_by
        })

    if not data:
        st.info("No territories available. Please add some territories first.")
        return

    df = pd.DataFrame(data)

    # Create an abstract scatter plot.
    fig = px.scatter(
        df,
        x="X",
        y="Y",
        text="Territory",
        color="Controlled By",
        hover_data=["Territory", "Controlled By"],
        title="Abstract Territory Map"
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(
        xaxis_title="Abstract X",
        yaxis_title="Abstract Y",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False)
    )

    st.plotly_chart(fig, use_container_width=True)

# Render the abstract map.
show_abstract_map()
