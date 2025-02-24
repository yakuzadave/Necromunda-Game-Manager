from typing import List, Optional
import json
import requests
import os
from pydantic import BaseModel, Field, ValidationError

# Importing game rules (ensure this module contains any additional game-specific logic)
from common import Gang, GangFighter  # Placeholder; update as needed

# Environment Variables
groq_api_key = os.environ.get('GROQ_API_KEY')
if not groq_api_key:
    raise EnvironmentError("GROQ_API_KEY must be set in the environment variables.")

# --- NECROMUNDA GANG MODELS ---

class Weapon(BaseModel):
    name: str
    cost: int
    type: str  # e.g., "Pistol", "Basic", "Special", "Heavy"
    restrictions: Optional[List[str]] = []  # e.g., ["Leader", "Champion"]

class Equipment(BaseModel):
    name: str
    cost: int

class GangMember(BaseModel):
    name: str
    rank: str = Field(..., pattern="^(Leader|Champion|Ganger|Juve|Prospect)$")  # Use 'pattern' for Pydantic v2
    cost: int
    skills: Optional[List[str]] = []
    weapons: Optional[List[Weapon]] = []
    equipment: Optional[List[Equipment]] = []

class GangSchema(BaseModel):
    gang_name: str
    members: List[GangMember]
    territories: List[str]

    def validate_gang(self):
        """
        Validates that the gang adheres to the Escher rules:
         - Exactly one Leader.
         - At most two Champions.
         - At least three Gangers.
         - Total cost does not exceed 1000 credits.
        """
        total_cost = sum(
            member.cost +
            sum(w.cost for w in (member.weapons or [])) +
            sum(e.cost for e in (member.equipment or []))
            for member in self.members
        )

        leader_count = sum(1 for m in self.members if m.rank == "Leader")
        champion_count = sum(1 for m in self.members if m.rank == "Champion")
        ganger_count = sum(1 for m in self.members if m.rank == "Ganger")
        juve_count = sum(1 for m in self.members if m.rank == "Juve")

        errors = []
        if leader_count != 1:
            errors.append("An Escher gang must have exactly ONE Leader.")
        if champion_count > 2:
            errors.append("An Escher gang can have at most TWO Champions.")
        if ganger_count < 3:
            errors.append("An Escher gang must have at least THREE Gangers.")
        if total_cost > 1000:
            errors.append(f"Gang exceeds the 1000-credit limit! Current total cost: {total_cost} credits.")

        if errors:
            raise ValueError("Gang validation failed:\n" + "\n".join(errors))

# --- API CALL TO FETCH GANG DATA ---

def get_gang(gang_name: str, temperature: float = 0.5, attempt: int = 1) -> GangSchema:
    """
    Calls the Groq API to fetch gang data. The system prompt is modified on retries
    to include a re-run instruction, and the temperature parameter introduces variance.
    """
    url = 'https://api.groq.com/openai/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {groq_api_key}',
        'Content-Type': 'application/json'
    }

    # Build the system prompt.
    system_message = (
        "You are a Necromunda gang database. You must generate a valid JSON object "
        "that strictly conforms to the following JSON schema. Do not include any extra text.\n\n"
    )
    if attempt > 1:
        system_message += (
            f"This is re-run attempt number {attempt}. Please reformat your output to contain only valid JSON "
            "exactly according to the schema, with no additional commentary.\n\n"
        )
    # Append the JSON schema definition.
    system_message += json.dumps(GangSchema.model_json_schema(), indent=2)

    payload = {
        'messages': [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Provide the details for the Escher gang called '{gang_name}' within a 1000-credit limit."}
        ],
        'model': "llama-3.3-70b-specdec",
        'temperature': temperature,
        'stream': False,
        'response_format': {"type": "json_object"}
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    chat_completion = response.json()

    try:
        # Parse and validate JSON against the schema.
        gang = GangSchema.model_validate_json(chat_completion['choices'][0]['message']['content'])
        gang.validate_gang()  # Run custom gang composition validations.
        return gang
    except ValidationError as e:
        print("Pydantic Validation Error:", e.json())
        raise
    except ValueError as e:
        print("Gang Validation Failed:", str(e))
        raise

def get_valid_gang(gang_name: str, max_retries: int = 3) -> GangSchema:
    """
    Tries to fetch and validate gang data up to max_retries times.
    The temperature is increased with each attempt to introduce variance.
    """
    base_temperature = 0.5
    for attempt in range(1, max_retries + 1):
        try:
            # Increase temperature slightly with each attempt.
            current_temperature = base_temperature + (attempt - 1) * 0.1
            print(f"Attempt {attempt} with temperature {current_temperature:.2f}...")
            gang = get_gang(gang_name, temperature=current_temperature, attempt=attempt)
            return gang
        except (ValidationError, ValueError) as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt == max_retries:
                raise RuntimeError("Failed to generate a valid gang after multiple attempts.")
            else:
                print("Retrying with updated parameters...\n")

# --- PRINT GANG DETAILS ---

def print_gang(gang: GangSchema):
    print(f"\n=== Gang: {gang.gang_name} ===\n")
    print("Members:")
    for member in gang.members:
        print(f"- {member.name}: {member.rank} ({member.cost} credits)")
        if member.skills:
            print(f"  Skills: {', '.join(member.skills)}")
        if member.weapons:
            weapons_str = ", ".join([f"{w.name} ({w.cost} credits)" for w in member.weapons])
            print(f"  Weapons: {weapons_str}")
        if member.equipment:
            equipment_str = ", ".join([f"{e.name} ({e.cost} credits)" for e in member.equipment])
            print(f"  Equipment: {equipment_str}")
    print("\nTerritories:")
    for territory in gang.territories:
        print(f"- {territory}")

# --- MAIN EXECUTION ---

if __name__ == '__main__':
    try:
        gang = get_valid_gang("The Wild Bunch", max_retries=3)
        print_gang(gang)
    except Exception as e:
        print("Error:", e)
