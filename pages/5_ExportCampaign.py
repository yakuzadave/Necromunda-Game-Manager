import streamlit as st
import json
import uuid
from datetime import datetime

def export_campaign():
    st.subheader("Export Full Campaign Overview")
    st.write("Fill in the campaign metadata below to generate a full campaign JSON from the current data.")
    with st.form("export_form"):
        campaign_name = st.text_input("Campaign Name", value="Power Play")
        campaign_url = st.text_input("Campaign URL", value="")
        campaign_created_username = st.text_input("Created By", value="User")
        submit_export = st.form_submit_button("Generate Full Campaign JSON")
    if submit_export:
        campaign_id = str(uuid.uuid4())
        campaign_created_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        campaign_gang_count = len(st.session_state.gangs)
        campaign_member_count = 0  # Adjust if you add member management
        # Convert local gangs to a simplified campaign gang format
        campaign_gangs = []
        for gang in st.session_state.gangs:
            campaign_gangs.append({
                "gang_id": gang.gang_id,
                "gang_user_id": "N/A",
                "gang_username": "N/A",
                "gang_name": gang.gang_name,
                "gang_type": gang.gang_type,
                "gang_url": "",
                "gang_rating": 0,
                "credits": gang.credits,
                "reptutation": gang.reputation,
                "wealth": 0,
                "alignment": "",
                "territories_dominion": None,
                "territories_gang": len(gang.territories),
                "kills": 0
            })
        # Convert local territories
        campaign_territories = []
        for territory in st.session_state.territories:
            campaign_territories.append({
                "territory_id": str(uuid.uuid4()),
                "territory_name": territory.name,
                "territory_gang_type": "",
                "territory_gang_id": territory.controlled_by if territory.controlled_by else "N/A",
                "territory_gang_name": territory.controlled_by if territory.controlled_by else "N/A"
            })
        # Convert local battles (simplified conversion)
        campaign_battles = []
        for battle in st.session_state.battles:
            battle_gangs = []
            for gang_name in battle.participating_gangs:
                found_gang = next((g for g in st.session_state.gangs if g.gang_name == gang_name), None)
                if found_gang:
                    battle_gangs.append({
                        "gang_id": 0,
                        "gang_name": found_gang.gang_name,
                        "gang_rating": 0
                    })
                else:
                    battle_gangs.append({
                        "gang_id": 0,
                        "gang_name": gang_name,
                        "gang_rating": 0
                    })
            campaign_battles.append({
                "battle_id": battle.battle_id,
                "battle_created_datetime": battle.battle_created_datetime,
                "battle_scenario": battle.battle_scenario,
                "battle_winner_gang_id": "N/A",
                "battle_winner_gang_name": battle.winner_gang,
                "battle_winner_territory": battle.winner_territory,
                "battle_gangs": battle_gangs
            })
        full_campaign = {
            "campaign": {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "campaign_url": campaign_url,
                "campaign_created_datetime": campaign_created_datetime,
                "campaign_created_username": campaign_created_username,
                "campaign_member_count": campaign_member_count,
                "campaign_gang_count": campaign_gang_count,
                "members": [],
                "gangs": campaign_gangs,
                "territories": campaign_territories,
                "battles": campaign_battles
            }
        }
        full_campaign_json = json.dumps(full_campaign, indent=4)
        st.session_state.full_campaign_json = full_campaign_json
        st.success("Full campaign JSON generated!")
    if "full_campaign_json" in st.session_state:
        st.download_button(
            "Download Full Campaign JSON", 
            data=st.session_state.full_campaign_json, 
            file_name="full_campaign_data.json", 
            mime="application/json"
        )

export_campaign()
