# pages/8_ImportYaktribe.py

import streamlit as st
import requests
from datetime import datetime
from common import Gang, save_data  # Import necessary models and functions
import json

st.title("Import Yaktribe Gang")

st.markdown("""
Enter the URL of your Yaktribe gang JSON file (e.g., 
`https://yaktribe.games/underhive/json/gang/485755.json`), then click **Import Gang**.
""")

# Input field for the URL
url = st.text_input("Yaktribe JSON URL", value="https://yaktribe.games/underhive/json/gang/485755.json")

if st.button("Import Gang"):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for bad responses
        yak_data = response.json()

        # The expected format: {"gang": { ... }}
        gang_data = yak_data.get("gang")
        if not gang_data:
            st.error("No gang data found in the JSON payload.")
        else:
            # Convert numeric values from strings to integers as needed.
            gang_data["credits"] = int(gang_data.get("credits", "0"))
            gang_data["reputation"] = int(gang_data.get("reputation", "0"))
            # (Optionally, convert other fields such as gang_rating, wealth, etc.)

            # Process each fighter in "gangers": convert numeric strings to ints.
            for ganger in gang_data.get("gangers", []):
                ganger["m"] = int(ganger.get("m", 0))
                ganger["ws"] = int(ganger.get("ws", 0))
                ganger["bs"] = int(ganger.get("bs", 0))
                ganger["s"] = int(ganger.get("s", 0))
                ganger["t"] = int(ganger.get("t", 0))
                ganger["w"] = int(ganger.get("w", 0))
                ganger["i"] = int(ganger.get("i", 0))
                ganger["a"] = int(ganger.get("a", 0))
                ganger["ld"] = int(ganger.get("ld", 0))
                ganger["cl"] = int(ganger.get("cl", 0))
                ganger["wil"] = int(ganger.get("wil", 0))
                ganger["intelligence"] = int(ganger.get("int", 0))
                ganger["cost"] = int(ganger.get("cost", "0"))
                ganger["xp"] = int(ganger.get("xp", "0"))
                ganger["kills"] = int(ganger.get("kills", "0"))
                ganger["advance_count"] = int(ganger.get("advance_count", "0"))

            # Create a new Gang instance from the Yaktribe data.
            new_gang = Gang(
                gang_id=gang_data.get("gang_id"),
                gang_name=gang_data.get("gang_name"),
                gang_type=gang_data.get("gang_type"),
                campaign=gang_data.get("campaign"),
                credits=gang_data.get("credits"),
                reputation=gang_data.get("reputation"),
                territories=gang_data.get("territories", []),
                gangers=gang_data.get("gangers", [])
            )

            # Check if a gang with this gang_id already exists in session state.
            exists = False
            for idx, existing in enumerate(st.session_state.gangs):
                if existing.gang_id == new_gang.gang_id:
                    st.session_state.gangs[idx] = new_gang  # Update the existing gang.
                    exists = True
                    break

            if not exists:
                st.session_state.gangs.append(new_gang)  # Add new gang if not found.

            # Save the updated data to campaign_data.json.
            save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)

            if exists:
                st.success(f"Updated gang '{new_gang.gang_name}' successfully!")
            else:
                st.success(f"Imported gang '{new_gang.gang_name}' successfully!")
    except requests.RequestException as e:
        st.error(f"HTTP error: {e}")
    except Exception as e:
        st.error(f"Error importing Yaktribe gang: {e}")
