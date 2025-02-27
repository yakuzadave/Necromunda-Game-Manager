# pages/8_ImportYaktribe.py

from typing import Any, Dict, List

import requests
import streamlit as st

from common import Gang, save_data


def convert_ganger_stats(ganger: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ganger statistics from strings to integers."""
    stat_fields = ['m', 'ws', 'bs', 's', 't', 'w', 'i', 'a', 'ld', 'cl', 'wil']
    other_fields = ['cost', 'xp', 'kills', 'advance_count']
    
    for field in stat_fields:
        ganger[field] = int(ganger.get(field, 0))
    
    for field in other_fields:
        ganger[field] = int(ganger.get(field, "0"))
    
    # Special case for intelligence as it's named differently in the JSON
    ganger['intelligence'] = int(ganger.get('int', 0))
    
    return ganger

st.title("Import Yaktribe Gang")

st.markdown("""
Enter the URL of your Yaktribe gang JSON file (e.g., 
`https://yaktribe.games/underhive/json/gang/485755.json`), then click **Import Gang**.
""")

url = st.text_input("Yaktribe JSON URL", value="https://yaktribe.games/underhive/json/gang/485755.json")

if st.button("Import Gang"):
    try:
        response = requests.get(url, timeout=10)  # Add timeout
        response.raise_for_status()
        yak_data = response.json()

        gang_data = yak_data.get("gang")
        if not gang_data:
            st.error("No gang data found in the JSON payload.")
            st.stop()

        # Convert numeric values and validate required fields
        required_fields = ['gang_id', 'gang_name', 'gang_type']
        if not all(field in gang_data for field in required_fields):
            st.error("Missing required gang data fields.")
            st.stop()

        # Convert numeric fields with default values
        gang_data["credits"] = int(gang_data.get("credits", "0"))
        gang_data["reputation"] = int(gang_data.get("reputation", "0"))

        # Process gangers
        gang_data["gangers"] = [
            convert_ganger_stats(ganger) 
            for ganger in gang_data.get("gangers", [])
        ]

        # Create new gang instance
        new_gang = Gang(
            gang_id=gang_data["gang_id"],
            gang_name=gang_data["gang_name"],
            gang_type=gang_data["gang_type"],
            campaign=gang_data.get("campaign"),
            credits=gang_data["credits"],
            reputation=gang_data["reputation"],
            territories=gang_data.get("territories", []),
            gangers=gang_data["gangers"]
        )

        # Update or add gang to session state
        gang_index = next(
            (i for i, g in enumerate(st.session_state.gangs) 
             if g.gang_id == new_gang.gang_id),
            None
        )

        if gang_index is not None:
            st.session_state.gangs[gang_index] = new_gang
            message = f"Updated gang '{new_gang.gang_name}' successfully!"
        else:
            st.session_state.gangs.append(new_gang)
            message = f"Imported gang '{new_gang.gang_name}' successfully!"

        # Save changes
        save_data(
            st.session_state.gangs, 
            st.session_state.territories, 
            st.session_state.battles
        )
        st.success(message)

    except requests.Timeout:
        st.error("Request timed out. Please try again.")
    except requests.RequestException as e:
        st.error(f"HTTP error: {str(e)}")
    except ValueError as e:
        st.error(f"Invalid JSON data: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
