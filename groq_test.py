from typing import List, Optional, Dict
import json
import requests
import os
from pydantic import BaseModel, Field, ValidationError, model_validator
from datetime import datetime
import uuid

# Environment Variables
groq_api_key = os.environ.get('GROQ_API_KEY')
if not groq_api_key:
    raise EnvironmentError("GROQ_API_KEY must be set in the environment variables.")

# --- Enhanced NECROMUNDA GANG MODELS ---

class Injury(BaseModel):
    name: str
    description: str
    severity: str = Field(..., pattern="^(Minor|Major|Critical)$")
    permanent: bool = False

class Advancement(BaseModel):
    type: str = Field(..., pattern="^(StatIncrease|Skill|Talent)$")
    description: str
    xp_cost: int = Field(..., ge=0)
    date_acquired: datetime = Field(default_factory=datetime.now)

class Weapon(BaseModel):
    name: str
    cost: int = Field(..., ge=0)
    type: str = Field(..., pattern="^(Pistol|Basic|Special|Heavy|Melee)$")
    traits: List[str] = []
    restrictions: List[str] = []

class Equipment(BaseModel):
    name: str
    cost: int = Field(..., ge=0)
    qty: int = Field(1, ge=1)
    traits: List[str] = []

class GangFighter(BaseModel):
    name: str
    rank: str = Field(..., pattern="^(Leader|Champion|Ganger|Juve)$")
    m: int = Field(..., ge=1, le=6)
    ws: int = Field(..., ge=1, le=6)
    bs: int = Field(..., ge=1, le=6)
    s: int = Field(..., ge=1, le=6)
    t: int = Field(..., ge=1, le=6)
    w: int = Field(..., ge=1, le=6)
    i: int = Field(..., ge=1, le=6)
    a: int = Field(..., ge=1, le=6)
    ld: int = Field(..., ge=1, le=6)
    cl: int = Field(..., ge=1, le=6)
    wil: int = Field(..., ge=1, le=6)
    intelligence: int = Field(..., alias="int", ge=1, le=6)
    cost: int = Field(..., ge=0)
    xp: int = Field(0, ge=0)
    skills: List[str] = []
    weapons: List[Weapon] = []
    equipment: List[Equipment] = []
    injuries: List[Injury] = []
    advancements: List[Advancement] = []
    status: str = Field("Active", pattern="^(Active|Injured|Retired|Dead)$")

    @model_validator(mode='after')
    def validate_weapons(self) -> 'GangFighter':
        if self.rank == 'Juve':
            for weapon in self.weapons:
                if weapon.type in ['Heavy', 'Special']:
                    raise ValueError("Juves cannot carry Heavy or Special weapons")
        return self

class GangSchema(BaseModel):
    gang_name: str
    credits: int = Field(..., ge=0)
    reputation: int = Field(0, ge=0)
    territories: List[str] = []
    gangers: List[GangFighter]
    stash: List[Equipment] = []

    @model_validator(mode='after')
    def validate_gang(self) -> 'GangSchema':
        total_cost = sum(
            fighter.cost +
            sum(w.cost for w in fighter.weapons) +
            sum(e.cost * e.qty for e in fighter.equipment)
            for fighter in self.gangers
        ) + sum(e.cost * e.qty for e in self.stash)

        ranks = [fighter.rank for fighter in self.gangers]
        errors = []

        if ranks.count("Leader") != 1:
            errors.append("Must have exactly one Leader")
        if ranks.count("Champion") > 2:
            errors.append("Maximum of two Champions allowed")
        if ranks.count("Ganger") < 3:
            errors.append("Minimum three Gangers required")
        if total_cost > 1000:
            errors.append(f"Total cost {total_cost} exceeds 1000 credit limit")

        if errors:
            raise ValueError("\n".join(errors))
        return self

def get_gang(gang_name: str, temperature: float = 0.5, validation_errors: List[str] = None) -> GangSchema:
    from prompt_templates.gang_gen import (
        generate_system_prompt,
        generate_rerun_prompt
    )

    schema_json = json.dumps(GangSchema.model_json_schema(), indent=2)
    rules = (
        "1 Leader, 0-2 Champions, 3+ Gangers, "
        "Weapons restricted by fighter rank, "
        "Total cost ≤ 1000 credits (including stash)"
    )

    system_message = generate_rerun_prompt(
        gang_name=gang_name,
        schema_json=schema_json,
        credit_limit=1000,
        rules=rules,
        attempt=attempt
    ) if validation_errors else generate_system_prompt(
        faction_name="Escher",
        schema_json=schema_json,
        credit_limit=1000,
        rules=rules
    )

    payload = {
        'messages': [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Generate the '{gang_name}' gang with full equipment traits and valid stats"}
        ],
        'model': "llama3-70b-8192",
        'temperature': temperature,
        'response_format': {"type": "json_object"}
    }

    response = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={'Authorization': f'Bearer {groq_api_key}'},
        json=payload
    )
    response.raise_for_status()

    try:
        content = response.json()['choices'][0]['message']['content']
        gang = GangSchema.model_validate_json(content)
        gang.validate_gang()
        return gang
    except (ValidationError, ValueError) as e:
        error_messages = e.errors() if isinstance(e, ValidationError) else [{'msg': str(e)}]
        raise ValidationError.from_exception_data(
            title='Gang Validation Error',
            line_errors=error_messages
        )

def get_valid_gang(gang_name: str, max_retries: int = 3) -> GangSchema:
    validation_errors = []
    temperature = 0.5

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt} (Temperature: {temperature:.1f})")
            gang = get_gang(gang_name, temperature, validation_errors)
            return gang
        except (ValidationError, ValueError) as e:
            validation_errors = e.args[0] if e.args else []
            print(f"Validation failed: {validation_errors}")

            temperature = min(0.9, temperature + 0.2)
            if attempt == max_retries:
                raise RuntimeError(f"Failed after {max_retries} attempts")

            print("Retrying with adjusted parameters...\n")

def print_gang(gang: GangSchema):
    print(f"\n{gang.gang_name} (Credits: {gang.credits}, Rep: {gang.reputation})")

    print("\nFighters:")
    for fighter in gang.gangers:
        print(f"\n{fighter.name} ({fighter.rank})")
        print(f"Stats: M:{fighter.m} WS:{fighter.ws} BS:{fighter.bs} S:{fighter.s} T:{fighter.t} W:{fighter.w} I:{fighter.i} A:{fighter.a}")
        print(f"Characteristics: LD:{fighter.ld} CL:{fighter.cl} WIL:{fighter.wil} INT:{fighter.intelligence}")
        print(f"XP: {fighter.xp} | Status: {fighter.status}")

        if fighter.weapons:
            print("Weapons:")
            for weapon in fighter.weapons:
                print(f"  - {weapon.name} ({weapon.type}, {weapon.cost}cr, Traits: {', '.join(weapon.traits)})")

        if fighter.equipment:
            print("Equipment:")
            for item in fighter.equipment:
                print(f"  - {item.name} x{item.qty} ({item.cost}cr each, Traits: {', '.join(item.traits)})")

    if gang.stash:
        print("\nGang Stash:")
        for item in gang.stash:
            print(f"  - {item.name} x{item.qty} ({item.cost}cr each)")

if __name__ == '__main__':
    try:
        gang = get_valid_gang("Venom's Blades", max_retries=3)
        print_gang(gang)
    except Exception as e:
        print(f"Error: {e}")