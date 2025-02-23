import streamlit as st
import pandas as pd
import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
import uuid

# Set page config
st.set_page_config(
    page_title="Necromunda Campaign Manager",
    page_icon="🎮",
    layout="wide"
)

# -------------------- File Names --------------------
DATA_FILE = "campaign_data.json"
FULL_CAMPAIGN_DATA_FILE = "full_campaign_data.json"

# -------------------- Session State Initialization --------------------
if 'gangs' not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            # Convert gang dictionaries to Gang objects
            st.session_state.gangs = [Gang(**g) for g in data.get("gangs", [])]
            st.session_state.territories = data.get("territories", [])
            st.session_state.battles = data.get("battles", [])
    else:
        st.session_state.gangs = []
        st.session_state.territories = []
        st.session_state.battles = []
if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []

# -------------------- Main Page Content --------------------
st.title("Welcome to Necromunda Campaign Manager")
st.markdown("""
## Getting Started
Use the sidebar to navigate between different sections:
- **Dashboard**: Overview of your campaign statistics
- **Gangs**: Manage your gangs and fighters
- **Territories**: Control territory distribution
- **Battles**: Record battle outcomes
- **Equipment**: Manage your equipment library
- **Full Campaign Overview**: View imported campaign data
- **Export Campaign**: Export your campaign data
""")

# Display quick stats if data exists
if st.session_state.gangs or st.session_state.territories or st.session_state.battles:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Gangs", len(st.session_state.gangs))
    with col2:
        st.metric("Total Territories", len(st.session_state.territories))
    with col3:
        st.metric("Battles Fought", len(st.session_state.battles))
else:
    st.info("Start by adding your first gang in the Gangs section!")

# -------------------- Local Campaign Models --------------------

class Equipment(BaseModel):
    equipment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    qty: int
    cost: int = 0
    traits: str = ""

class GangFighter(BaseModel):
    ganger_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label_id: Optional[str] = ""
    name: str
    type: str
    m: int
    ws: int
    bs: int
    s: int
    t: int
    w: int
    i: int
    a: int
    ld: int
    cl: int
    wil: int
    intelligence: int = Field(..., alias="int")
    cost: int
    xp: int
    kills: int
    advance_count: int
    equipment: List[Equipment] = []
    skills: List[str] = []
    injuries: List[str] = []
    image: Optional[str] = None
    status: str
    notes: str
    datetime_added: str
    datetime_updated: str

    class Config:
        allow_population_by_field_name = True

class Gang(BaseModel):
    gang_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gang_name: str
    gang_type: str
    campaign: str = ""
    credits: int
    reputation: int
    territories: List[str] = []
    gangers: List[GangFighter] = []

class Territory(BaseModel):
    name: str
    type: str
    controlled_by: Optional[str] = None
    x: Optional[float] = None  # Custom X coordinate for abstract map
    y: Optional[float] = None  # Custom Y coordinate for abstract map
    lat: Optional[float] = None  # For geolocated maps (if needed)
    lng: Optional[float] = None  # For geolocated maps (if needed)

class LocalBattle(BaseModel):
    battle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    battle_created_datetime: str
    battle_scenario: str
    winner_gang: str
    winner_territory: Optional[str] = None
    participating_gangs: List[str]

# -------------------- Full Campaign Models --------------------
# These models mirror the structure of your full campaign JSON data.

class Member(BaseModel):
    member_user_id: int
    member_username: str
    member_url: str
    member_admin: str

class CampaignGang(BaseModel):
    gang_id: str
    gang_user_id: str
    gang_username: str
    gang_name: str
    gang_type: str
    gang_url: Optional[str] = None
    gang_rating: int
    credits: int
    reputation: int = Field(..., alias="reptutation")
    wealth: int
    alignment: str
    territories_dominion: Optional[int] = None
    territories_gang: int
    kills: int

class CampaignTerritory(BaseModel):
    territory_id: str
    territory_name: str
    territory_gang_type: Optional[str] = ""
    territory_gang_id: str
    territory_gang_name: str

class BattleGang(BaseModel):
    gang_id: int
    gang_name: str
    gang_rating: int

class Battle(BaseModel):
    battle_id: str
    battle_created_datetime: str
    battle_scenario: str
    battle_winner_gang_id: Optional[str] = None
    battle_winner_gang_name: str
    battle_winner_territory: Optional[str] = None
    battle_gangs: List[BattleGang]

class Campaign(BaseModel):
    campaign_id: str
    campaign_name: str
    campaign_url: str
    campaign_created_datetime: str
    campaign_created_username: str
    campaign_member_count: int
    campaign_gang_count: int
    members: List[Member]
    gangs: List[CampaignGang]
    territories: List[CampaignTerritory]
    battles: List[Battle]

# -------------------- Persistence Functions for Local Data --------------------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        gangs = []
        territories = []
        battles = []
        for g in data.get("gangs", []):
            try:
                gangs.append(Gang(**g))
            except ValidationError as e:
                st.error(f"Error loading gang data: {e}")
        for t in data.get("territories", []):
            try:
                territories.append(Territory(**t))
            except ValidationError as e:
                st.error(f"Error loading territory data: {e}")
        for b in data.get("battles", []):
            try:
                battles.append(LocalBattle(**b))
            except ValidationError as e:
                st.error(f"Error loading battle data: {e}")
        return gangs, territories, battles
    else:
        return [], [], []

def save_data(gangs: List[Gang], territories: List[Territory], battles: List[LocalBattle]):
    data = {
        "gangs": [g.dict() for g in gangs],
        "territories": [t.dict() for t in territories],
        "battles": [b.dict() for b in battles]
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -------------------- Load Full Campaign Data (External) --------------------

def load_full_campaign() -> Optional[Campaign]:
    if os.path.exists(FULL_CAMPAIGN_DATA_FILE):
        try:
            with open(FULL_CAMPAIGN_DATA_FILE, "r") as f:
                full_data = json.load(f)
            campaign = Campaign(**full_data["campaign"])
            return campaign
        except Exception as e:
            st.error(f"Error loading full campaign data: {e}")
            return None
    else:
        st.info(f"Full campaign data file '{FULL_CAMPAIGN_DATA_FILE}' not found. Please add a valid file to enable this feature.")
        return None

# -------------------- Utility Functions --------------------

def assign_territory(territory_name: str, gang_name: str):
    for territory in st.session_state.territories:
        if territory.name == territory_name:
            territory.controlled_by = gang_name
            break
    for gang in st.session_state.gangs:
        if gang.gang_name == gang_name:
            if territory_name not in gang.territories:
                gang.territories.append(territory_name)
            break
    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)

# -------------------- Page Functions --------------------

def show_dashboard():
    st.subheader("Dashboard")
    # Convert gangs to proper Gang objects
    gang_objects = []
    for g in st.session_state.gangs:
        if isinstance(g, dict):
            try:
                gang_objects.append(Gang(**g))
            except Exception as e:
                st.error(f"Error converting gang: {e}")
        else:
            gang_objects.append(g)
            
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("Total Gangs", len(gang_objects))
    with col4:
        total_credits = sum(g.credits for g in gang_objects)
        st.metric("Total Credits", total_credits)
    with col5:
        if gang_objects:
            top_gang = max(gang_objects, key=lambda g: g.reputation)
            st.metric("Top Gang", f"{top_gang.gang_name} ({top_gang.reputation} rep)")
    if st.session_state.battles:
        with st.expander("Battle Log"):
            for battle in st.session_state.battles:
                st.write(f"**{battle.battle_scenario}** on {battle.battle_created_datetime}")
                win_info = f"Winner: {battle.winner_gang}"
                if battle.winner_territory:
                    win_info += f" (Territory: {battle.winner_territory})"
                st.write(win_info)
                st.write(f"Participants: {', '.join(battle.participating_gangs)}")
                st.markdown("---")
    else:
        st.info("No battles recorded yet.")

def show_gangs():
    st.subheader("Gangs")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.write("### Register New Gang")
        gang_name_input = st.text_input("Gang Name")
        gang_type_input = st.selectbox("Gang Type", [
            "House Orlock",
            "House Goliath",
            "House Escher",
            "House Van Saar",
            "House Delaque",
            "House Cawdor",
            "Enforcers",
            "Genestealer Cults",
            "Squat Prospectors",
            "Chaos Cults",
            "Corpse Grinder Cults",
            "Venators (Bounty Hunters)",
            "Slave Ogryns",
            "Ash Waste Nomads",
            "Outcast Gangs"
        ])
        campaign_input = st.text_input("Campaign", value="Power Play")
        credits_input = st.number_input("Starting Credits", min_value=0, value=160)
        reputation_input = st.number_input("Reputation", min_value=0, value=6)
        if st.button("Register Gang"):
            if gang_name_input:
                try:
                    new_gang = Gang(
                        gang_name=gang_name_input,
                        gang_type=gang_type_input,
                        campaign=campaign_input,
                        credits=credits_input,
                        reputation=reputation_input
                    )
                    st.session_state.gangs.append(new_gang)
                    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                    st.success(f"Registered {gang_name_input}!")
                except ValidationError as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please enter a gang name.")
    with col2:
        st.write("### Active Gangs & Fighter Management")
        if st.session_state.gangs:
            for idx, gang in enumerate(st.session_state.gangs):
                with st.expander(f"{gang.gang_name} ({gang.gang_type})"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"Credits: {gang.credits}")
                        st.write(f"Reputation: {gang.reputation}")
                    with col_b:
                        st.write(f"Territories: {len(gang.territories)}")
                    if st.button("Record Battle (Quick)", key=f"battle_{idx}"):
                        gang.reputation += 5
                        gang.credits += 100
                        save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                        st.success("Battle recorded!")
                    if st.button("Remove Gang", key=f"remove_{idx}"):
                        st.session_state.gangs.pop(idx)
                        save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                        st.experimental_rerun()
                    st.write("**Fighters:**")
                    if hasattr(gang, "gangers") and gang.gangers:
                        for fighter in gang.gangers:
                            st.write(f"**{fighter.name}** ({fighter.type}) - M: {fighter.m}, WS: {fighter.ws}, BS: {fighter.bs}")
                    with st.form(key=f"fighter_form_{idx}"):
                        fighter_name = st.text_input("Fighter Name")
                        fighter_type = st.text_input("Fighter Type")
                        m_default = st.number_input("M", min_value=1, value=5, key=f"m_{idx}")
                        ws_default = st.number_input("WS", min_value=1, value=4, key=f"ws_{idx}")
                        bs_default = st.number_input("BS", min_value=1, value=3, key=f"bs_{idx}")
                        s_default = st.number_input("S", min_value=1, value=3, key=f"s_{idx}")
                        t_default = st.number_input("T", min_value=1, value=3, key=f"t_{idx}")
                        w_default = st.number_input("W", min_value=1, value=1, key=f"w_{idx}")
                        i_default = st.number_input("I", min_value=1, value=4, key=f"i_{idx}")
                        a_default = st.number_input("A", min_value=1, value=1, key=f"a_{idx}")
                        ld_default = st.number_input("Ld", min_value=1, value=7, key=f"ld_{idx}")
                        cl_default = st.number_input("Cl", min_value=1, value=5, key=f"cl_{idx}")
                        wil_default = st.number_input("Wil", min_value=1, value=6, key=f"wil_{idx}")
                        int_default = st.number_input("Int", min_value=1, value=8, key=f"int_{idx}")
                        submitted = st.form_submit_button("Add Fighter")
                        if submitted:
                            if fighter_name and fighter_type:
                                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                try:
                                    new_fighter = GangFighter(
                                        name=fighter_name,
                                        type=fighter_type,
                                        m=m_default,
                                        ws=ws_default,
                                        bs=bs_default,
                                        s=s_default,
                                        t=t_default,
                                        w=w_default,
                                        i=i_default,
                                        a=a_default,
                                        ld=ld_default,
                                        cl=cl_default,
                                        wil=wil_default,
                                        intelligence=int_default,
                                        cost=300,
                                        xp=0,
                                        kills=0,
                                        advance_count=0,
                                        status="Alive",
                                        notes="",
                                        datetime_added=now_str,
                                        datetime_updated=now_str
                                    )
                                    gang.gangers.append(new_fighter)
                                    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                                    st.success(f"Added fighter {fighter_name}!")
                                except ValidationError as e:
                                    st.error(f"Error: {e}")
                            else:
                                st.error("Provide both fighter name and type.")
        else:
            st.info("No gangs registered yet.")

def show_territories():
    st.subheader("Territory Management")
    territory_name_input = st.text_input("New Territory Name", key="territory_name")
    territory_type_input = st.selectbox("Territory Type", [
        'Trading Post', 'Mineral Deposits', 'Archaeotech Site', 
        'Promethium Cache', 'Water Still', 'Manufactory'
    ], key="territory_type")
    if st.button("Add Territory"):
        if territory_name_input:
            try:
                new_territory = Territory(
                    name=territory_name_input,
                    type=territory_type_input
                )
                st.session_state.territories.append(new_territory)
                save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                st.success(f"Added territory '{territory_name_input}'!")
            except ValidationError as e:
                st.error(f"Error: {e}")
        else:
            st.error("Enter a territory name.")
    st.markdown("---")
    st.write("### Assign Territory to Gang")
    unassigned_territories = [t.name for t in st.session_state.territories if t.controlled_by is None]
    gang_names = [g.gang_name for g in st.session_state.gangs]
    if unassigned_territories and gang_names:
        territory_to_assign = st.selectbox("Select Territory", unassigned_territories, key="assign_territory")
        gang_to_assign = st.selectbox("Select Gang", gang_names, key="assign_gang")
        if st.button("Assign Territory"):
            assign_territory(territory_to_assign, gang_to_assign)
            st.success(f"Assigned {territory_to_assign} to {gang_to_assign}")
    else:
        st.info("Ensure unassigned territories and registered gangs exist.")

def show_battles():
    st.subheader("Battle Recording")
    with st.form("battle_form"):
        battle_scenario = st.text_input("Battle Scenario")
        gang_names = [g.gang_name for g in st.session_state.gangs]
        winner_gang = st.selectbox("Winning Gang", gang_names) if gang_names else ""
        winner_territory = st.text_input("Winning Territory (optional)")
        participating_gangs = st.multiselect("Participating Gangs", gang_names)
        submit_battle = st.form_submit_button("Record Battle")
        if submit_battle:
            if battle_scenario and winner_gang and participating_gangs:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_battle = LocalBattle(
                    battle_created_datetime=now_str,
                    battle_scenario=battle_scenario,
                    winner_gang=winner_gang,
                    winner_territory=winner_territory if winner_territory else None,
                    participating_gangs=participating_gangs
                )
                st.session_state.battles.append(new_battle)
                save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
                st.success("Battle recorded!")
            else:
                st.error("Complete all battle details and select participants.")
    st.markdown("---")
    st.write("### Battle Log")
    if st.session_state.battles:
        for battle in st.session_state.battles:
            st.write(f"**{battle.battle_scenario}** on {battle.battle_created_datetime}")
            win_info = f"Winner: {battle.winner_gang}"
            if battle.winner_territory:
                win_info += f" (Territory: {battle.winner_territory})"
            st.write(win_info)
            st.write(f"Participants: {', '.join(battle.participating_gangs)}")
            st.markdown("---")
    else:
        st.info("No battles recorded yet.")

def show_full_campaign():
    st.subheader("Full Campaign Overview")
    campaign = load_full_campaign()
    if campaign:
        st.write(f"**Campaign ID:** {campaign.campaign_id}")
        st.write(f"**Campaign Name:** {campaign.campaign_name}")
        st.write(f"**Created By:** {campaign.campaign_created_username} on {campaign.campaign_created_datetime}")
        st.write(f"**Members:** {len(campaign.members)}")
        st.write(f"**Gangs:** {len(campaign.gangs)}")
        st.write(f"**Territories:** {len(campaign.territories)}")
        st.write(f"**Battles:** {len(campaign.battles)}")
    else:
        st.info("Full campaign data is not available.")

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
            # Convert local battles (using a simplified conversion)
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
            st.download_button("Download Full Campaign JSON", data=full_campaign_json, file_name="full_campaign_data.json", mime="application/json")
            st.success("Full campaign JSON generated!")

def show_equipment():
    st.subheader("Equipment Management")
    st.write("Manage your equipment library. Add new equipment items and view the current list.")
    with st.form("add_equipment_form"):
        equipment_name = st.text_input("Equipment Name")
        equipment_qty = st.number_input("Quantity", min_value=1, value=1)
        equipment_cost = st.number_input("Cost", min_value=0, value=0)
        equipment_traits = st.text_input("Traits (comma-separated)", value="")
        submit_equipment = st.form_submit_button("Add Equipment")
        if submit_equipment:
            if equipment_name:
                try:
                    new_equipment = Equipment(
                        name=equipment_name,
                        qty=equipment_qty,
                        cost=equipment_cost,
                        traits=equipment_traits
                    )
                    st.session_state.equipment_list.append(new_equipment)
                    st.success(f"Added equipment: {equipment_name}")
                except ValidationError as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please enter an equipment name.")
    st.markdown("---")
    st.write("### Equipment Library")
    if st.session_state.equipment_list:
        for eq in st.session_state.equipment_list:
            st.write(f"**{eq.name}** (Qty: {eq.qty}, Cost: {eq.cost}, Traits: {eq.traits})")
    else:
        st.info("No equipment added yet.")

# -------------------- Sidebar Navigation --------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Dashboard", "Gangs", "Territories", "Battles", "Equipment", "Full Campaign Overview", "Export Campaign"
])

if st.sidebar.button("Reset Campaign"):
    st.session_state.gangs = []
    st.session_state.territories = []
    st.session_state.battles = []
    st.session_state.equipment_list = []
    save_data(st.session_state.gangs, st.session_state.territories, st.session_state.battles)
    st.sidebar.warning("Campaign reset!")
    st.experimental_rerun()

# -------------------- Render Selected Page --------------------
if page == "Dashboard":
    show_dashboard()
elif page == "Gangs":
    show_gangs()
elif page == "Territories":
    show_territories()
elif page == "Battles":
    show_battles()
elif page == "Equipment":
    show_equipment()
elif page == "Full Campaign Overview":
    show_full_campaign()
elif page == "Export Campaign":
    export_campaign()
