scenario_schema_json = """{
  "title": "ScenarioSchema",
  "type": "object",
  "properties": {
    "scenario_name": { "type": "string" },
    "source": { "type": "string" },
    "summary": { "type": "string" },
    "battlefield": {
      "type": "object",
      "properties": {
        "zone_mortalis": { "type": "string" },
        "sector_mechanicus": { "type": "string" }
      }
    },
    "crews": {
      "type": "object",
      "properties": {
        "zone_mortalis": { "type": "string" },
        "sector_mechanicus": { "type": "string" }
      }
    },
    "tactics_cards": { "type": "string" },
    "deployment": { "type": "string" },
    "objectives": { "type": "string" },
    "ending_battle": {
      "type": "object",
      "properties": {
        "zone_mortalis": { "type": "string" },
        "sector_mechanicus": { "type": "string" }
      }
    },
    "victory": { "type": "string" },
    "rewards": {
      "type": "object",
      "properties": {
        "zone_mortalis": { "type": "string" },
        "sector_mechanicus": { "type": "string" }
      }
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}"""


def generate_scenario_system_prompt(schema_json: str) -> str:
  """
  Generates the system prompt for Necromunda mission scenario generation.

  Parameters:
  - schema_json: A string containing the JSON schema that the output must conform to.

  Returns:
  - A prompt string instructing the LLM to output valid JSON with no extra commentary.
  """
  return (
      "You are a Necromunda scenario database. "
      "Your task is to generate a valid JSON object that strictly conforms to the JSON schema below.\n\n"
      f"{schema_json}\n\n"
      "In Necromunda, missions may differ between Zone Mortalis and Sector Mechanicus. "
      "Include details for each environment if they differ. "
      "Do not include any commentary—only the JSON object."
  )

def generate_scenario_user_prompt(scenario_name: str, scenario_variant: str = "") -> str:
  """
  Generates the user prompt for requesting details of a specific Necromunda mission scenario.

  Parameters:
  - scenario_name: The name of the scenario (e.g., 'Tunnel Skirmish', 'Stand-off').
  - scenario_variant: Optional text describing a second variant (e.g., 'Zone Mortalis', 'Sector Mechanicus').

  Returns:
  - A prompt string instructing the LLM on which scenario details to produce.
  """
  base_prompt = f"Provide the details for the scenario named '{scenario_name}'."
  if scenario_variant:
      base_prompt += f" Also include the variant: {scenario_variant}."
  return base_prompt

def generate_scenario_rerun_prompt(scenario_name: str, schema_json: str, attempt: int) -> str:
  """
  Generates a re-run prompt with additional instructions if the first generation fails.

  Parameters:
  - scenario_name: Name of the scenario (e.g., 'Tunnel Skirmish / Stand-off').
  - schema_json: The JSON schema for validation.
  - attempt: Current re-run attempt number.

  Returns:
  - A prompt string for the re-run attempt, reminding the LLM to strictly follow the schema.
  """
  return (
      f"This is re-run attempt number {attempt} for generating the scenario '{scenario_name}'. "
      "Ensure your output strictly conforms to the JSON schema below:\n\n"
      f"{schema_json}\n\n"
      "Do not include any extra commentary—only valid JSON."
  )
