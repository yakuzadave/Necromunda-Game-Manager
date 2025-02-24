
import streamlit as st
from streamlit_mermaid import st_mermaid

st.title("Campaign Flow Charts")

st.markdown("""
Use this page to visualize campaign relationships and battle flows using Mermaid charts.
Choose a chart type below to visualize different aspects of your campaign.
""")

chart_type = st.selectbox(
    "Select Chart Type",
    ["Gang Relationships", "Battle Flow", "Territory Control"]
)

if chart_type == "Gang Relationships":
    gangs = st.session_state.gangs
    # Create a flowchart showing gang relationships
    chart = """
    flowchart TD
    """
    for gang in gangs:
        chart += f"\n    {gang.gang_id}[{gang.gang_name}]"
        for territory in gang.territories:
            chart += f"\n    {gang.gang_id} -->|controls| {territory}"
    
    st_mermaid(chart)

elif chart_type == "Battle Flow":
    battles = st.session_state.battles
    # Create a sequence diagram of battles
    chart = """
    sequenceDiagram
    """
    for battle in battles:
        for gang in battle.participating_gangs:
            chart += f"\n    participant {gang}"
        chart += f"\n    Note over {battle.winner_gang}: Winner"
    
    st_mermaid(chart)

elif chart_type == "Territory Control":
    territories = st.session_state.territories
    # Create a pie chart of territory control
    chart = """
    pie
    title Territory Control
    """
    control_count = {}
    for territory in territories:
        controller = territory.controlled_by or "Unclaimed"
        control_count[controller] = control_count.get(controller, 0) + 1
    
    for controller, count in control_count.items():
        chart += f'\n    "{controller}" : {count}'
    
    st_mermaid(chart)
