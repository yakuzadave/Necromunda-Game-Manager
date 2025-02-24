import streamlit as st
from streamlit_mermaid import st_mermaid

st.title("Campaign Flow Charts")

st.markdown(
    """
    Use this page to visualize campaign relationships and battle flows using Mermaid charts.
    Choose a chart type below to visualize different aspects of your campaign.
    """
)

chart_type = st.selectbox(
    "Select Chart Type",
    ["Gang Relationships", "Battle Flow", "Territory Control"]
)

if chart_type == "Gang Relationships":
    if "gangs" not in st.session_state or not st.session_state.gangs:
        st.error("No gang data available.")
    else:
        # Build the flowchart diagram
        lines = ["flowchart TD"]
        for gang in st.session_state.gangs:
            # Create a node for each gang using its ID and name.
            lines.append(f"    {gang.gang_id}[{gang.gang_name}]")
            # Create a link from the gang to each territory it controls.
            for territory in gang.territories:
                lines.append(f"    {gang.gang_id} -->|controls| {territory}")
        chart = "\n".join(lines)
        st_mermaid(chart)

elif chart_type == "Battle Flow":
    if "battles" not in st.session_state or not st.session_state.battles:
        st.error("No battle data available.")
    else:
        # Build a sequence diagram for battles.
        lines = ["sequenceDiagram"]
        for battle in st.session_state.battles:
            # Add each participating gang as a participant.
            for gang in battle.participating_gangs:
                lines.append(f"    participant {gang}")
            # Add a note indicating the winner for the battle.
            lines.append(f"    Note over {battle.winner_gang}: Winner")
        chart = "\n".join(lines)
        st_mermaid(chart)

elif chart_type == "Territory Control":
    if "territories" not in st.session_state or not st.session_state.territories:
        st.error("No territory data available.")
    else:
        # Build a pie chart showing territory control.
        lines = ["pie", "title Territory Control"]
        control_count = {}
        for territory in st.session_state.territories:
            controller = territory.controlled_by or "Unclaimed"
            control_count[controller] = control_count.get(controller, 0) + 1
        for controller, count in control_count.items():
            lines.append(f'    "{controller}" : {count}')
        chart = "\n".join(lines)
        st_mermaid(chart)
