territory_schema_json = """{
  "title": "TerritorySchema",
  "type": "object",
  "properties": {
    "territory_name": { "type": "string" },
    "description": { "type": "string" },
    "base_boons": {
      "type": "object",
      "properties": {
        "income": { "type": "string" },
        "recruit": { "type": "string" },
        "equipment": { "type": "string" },
        "reputation": { "type": "string" },
        "special": { "type": "string" }
      }
    },
    "enhanced_boons": {
      "type": "object",
      "description": "Enhanced Boons for specific Houses",
      "properties": {
        "house_benefits": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "house_name": { "type": "string" },
              "income": { "type": "string" },
              "recruit": { "type": "string" },
              "equipment": { "type": "string" },
              "reputation": { "type": "string" },
              "special": { "type": "string" }
            }
          }
        }
      }
    },
    "notes": { "type": "string" }
  },
  "required": [
    "territory_name",
    "description",
    "base_boons"
  ]
}"""


def generate_territory_system_prompt(schema_json: str) -> str:
  """
  Generates the system prompt for Necromunda territory generation.

  Parameters:
  - schema_json: A string containing the JSON schema that the output must conform to.

  Returns:
  - A prompt string instructing the LLM to output valid JSON with no extra commentary.
  """
  return (
      "You are a Necromunda territory database. "
      "Your task is to generate a valid JSON object that strictly conforms to the JSON schema below.\n\n"
      f"{schema_json}\n\n"
      "Territories in a Dominion Campaign grant boons such as Income, Recruit, Equipment, Reputation, "
      "or Special benefits. They may also offer enhanced boons for specific Houses. "
      "Do not include any commentary—only the JSON object."
  )

def generate_territory_user_prompt(territory_name: str) -> str:
  """
  Generates the user prompt for requesting details of a specific Necromunda territory.

  Parameters:
  - territory_name: The name of the territory to generate (e.g., 'Settlement', 'Refuse Drift', 'Gambling Den').

  Returns:
  - A prompt string instructing the LLM on which territory details to produce.
  """
  return (
      f"Provide the details for the territory named '{territory_name}' in a Dominion Campaign. "
      "Include base boons and any relevant enhanced boons."
  )

def generate_territory_rerun_prompt(territory_name: str, schema_json: str, attempt: int) -> str:
  """
  Generates a re-run prompt with additional instructions if the first generation fails.

  Parameters:
  - territory_name: The name of the territory.
  - schema_json: The JSON schema for validation.
  - attempt: Current re-run attempt number.

  Returns:
  - A prompt string for the re-run attempt, reminding the LLM to strictly follow the schema.
  """
  return (
      f"This is re-run attempt number {attempt} for generating the territory '{territory_name}'. "
      "Ensure your output strictly conforms to the JSON schema below:\n\n"
      f"{schema_json}\n\n"
      "Output only valid JSON with no additional commentary."
  )
