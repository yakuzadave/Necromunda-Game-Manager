# common.py

import json
import os
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError

# -------------------- Constants --------------------
DATA_FILE = "campaign_data.json"
FULL_CAMPAIGN_DATA_FILE = "full_campaign_data.json"

DATA_DIR = "data"
GANGS_DIR = os.path.join(DATA_DIR, "gangs")
TERRITORIES_DIR = os.path.join(DATA_DIR, "territories")
BATTLES_DIR = os.path.join(DATA_DIR, "battles")
EQUIPMENT_DIR = os.path.join(DATA_DIR, "equipment")

# Ensure directories exist
for directory in [GANGS_DIR, TERRITORIES_DIR, BATTLES_DIR, EQUIPMENT_DIR]:
    os.makedirs(directory, exist_ok=True)




# -------------------- Local Campaign Models --------------------

class Injury(BaseModel):
    """Model for tracking fighter injuries"""
    injury_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    severity: str  # Minor, Major, Critical
    permanent: bool = False

class Skill(BaseModel):
    """Model for fighter skills and special abilities"""
    skill_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # Combat, Agility, Brawn, etc.
    description: str
    prerequisites: List[str] = []

class Advancement(BaseModel):
    """Model for tracking fighter experience advancements"""
    advancement_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # StatIncrease, Skill, Talent
    description: str
    xp_cost: int
    date_acquired: datetime = Field(default_factory=datetime.now)

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
    # intelligence: int = Field(..., alias="int")
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
        # allow_population_by_field_name = True
        populate_by_name = True

class Gang(BaseModel):
    gang_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gang_name: str
    gang_type: str
    campaign: str = ""
    credits: int
    reputation: int
    territories: List[str] = []
    gangers: List[GangFighter] = []
    stash: List[Equipment] = []

class Territory(BaseModel):
    name: str
    type: str
    controlled_by: Optional[str] = None
    x: Optional[float] = None  # For an abstract map
    y: Optional[float] = None  # For an abstract map
    lat: Optional[float] = None  # For geolocated maps (if needed)
    lng: Optional[float] = None  # For geolocated maps (if needed)
    elevation: Optional[float] = None  # For maps (if needed)

class TerritoryEffect(BaseModel):
    effect_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    income_bonus: int = 0
    reputation_bonus: int = 0
    special_rules: List[str] = []

class Scenario(BaseModel):
    scenario_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    objectives: List[str] = []
    special_rules: List[str] = []
    min_players: int = 2
    max_players: int = 4

class LocalBattle(BaseModel):
    battle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    battle_created_datetime: str
    battle_scenario: str
    winner_gang: str
    winner_territory: Optional[str] = None
    participating_gangs: List[str]

# -------------------- Full Campaign Models --------------------

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

# -------------------- Persistence Functions --------------------

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
                print(f"Error loading gang data: {e}")
        for t in data.get("territories", []):
            try:
                territories.append(Territory(**t))
            except ValidationError as e:
                print(f"Error loading territory data: {e}")
        for b in data.get("battles", []):
            try:
                battles.append(LocalBattle(**b))
            except ValidationError as e:
                print(f"Error loading battle data: {e}")
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
    
    # Create backup after saving
    if 'backup_manager' in st.session_state:
        st.session_state.backup_manager.create_backup()



# Save a single gang
def save_gang(gang):
    """Saves a gang as a separate JSON file."""
    file_path = os.path.join(GANGS_DIR, f"{gang.gang_id}.json")
    with open(file_path, "w") as f:
        json.dump(gang.dict(), f, indent=4)

# Save a single territory
def save_territory(territory):
    """Saves a territory as a separate JSON file."""
    file_path = os.path.join(TERRITORIES_DIR, f"{territory.name}.json")
    with open(file_path, "w") as f:
        json.dump(territory.dict(), f, indent=4)

# Save a single battle
def save_battle(battle):
    """Saves a battle as a separate JSON file."""
    file_path = os.path.join(BATTLES_DIR, f"{battle.battle_id}.json")
    with open(file_path, "w") as f:
        json.dump(battle.dict(), f, indent=4)

# Save a single equipment item
def save_equipment(equipment):
    """Saves an equipment item as a separate JSON file."""
    file_path = os.path.join(EQUIPMENT_DIR, f"{equipment.equipment_id}.json")
    with open(file_path, "w") as f:
        json.dump(equipment.dict(), f, indent=4)
# -------------------- Utility Functions --------------------

def assign_territory(territory_name: str, gang_name: str, gangs: List[Gang], territories: List[Territory]):
    for territory in territories:
        if territory.name == territory_name:
            territory.controlled_by = gang_name
            break
    for gang in gangs:
        if gang.gang_name == gang_name:
            if territory_name not in gang.territories:
                gang.territories.append(territory_name)
            break
    save_data(gangs, territories, [])

def to_gang_obj(g):
    if isinstance(g, dict):
        try:
            return Gang(**g)
        except Exception as e:
            print(f"Conversion error for gang {g.get('gang_name', 'Unknown')}: {e}")
            return None
    return g



# -------------------- Load Full Campaign Data --------------------

def load_full_campaign() -> Optional[Campaign]:
    """
    Load full campaign data from FULL_CAMPAIGN_DATA_FILE and return a Campaign instance.
    """
    if os.path.exists(FULL_CAMPAIGN_DATA_FILE):
        try:
            with open(FULL_CAMPAIGN_DATA_FILE, "r") as f:
                full_data = json.load(f)
            campaign = Campaign(**full_data["campaign"])
            return campaign
        except Exception as e:
            print(f"Error loading full campaign data: {e}")
            return None
    else:
        return None
