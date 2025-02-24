def generate_equipment_system_prompt(schema_json: str) -> str:
  """
  Generates the system prompt for Necromunda equipment/weapon generation.

  Parameters:
  - schema_json: A string containing the JSON schema that the output must conform to.

  Returns:
  - A prompt string instructing the LLM to output valid JSON with no extra text.
  """
  return (
      "You are a Necromunda equipment database. "
      "Your task is to generate a valid JSON object that strictly conforms to the JSON schema below.\n\n"
      f"{schema_json}\n\n"
      "Use the references from Necromunda: Core Rulebook (2023), p264, as a foundation for weapon stats, "
      "including the examples of Autopistol and Bolt Pistol. "
      "Do not include any commentary—only the JSON object."
  )

def generate_equipment_user_prompt(equipment_name: str, ammo_variants: str = "") -> str:
  """
  Generates the user prompt for requesting details of a specific piece of Necromunda equipment.

  Parameters:
  - equipment_name: The name of the equipment or weapon to generate (e.g., 'Autopistol', 'Bolt Pistol').
  - ammo_variants: Optional text describing additional ammo types (e.g., 'static rounds, shock rounds').

  Returns:
  - A prompt string to instruct the LLM on which equipment details to produce.
  """
  base_prompt = f"Provide the stats for the '{equipment_name}'."
  if ammo_variants:
      base_prompt += f" Include ammo variants: {ammo_variants}."
  return base_prompt

def generate_equipment_rerun_prompt(equipment_name: str, schema_json: str, attempt: int) -> str:
  """
  Generates a re-run prompt with additional instructions if the first generation fails.

  Parameters:
  - equipment_name: Name of the equipment/weapon (e.g., 'Autopistol').
  - schema_json: The JSON schema for validation.
  - attempt: Current attempt number.

  Returns:
  - A prompt string for the re-run attempt, reminding the LLM to strictly follow the schema.
  """
  return (
      f"This is re-run attempt number {attempt} for generating the '{equipment_name}'. "
      "Ensure your output strictly conforms to the JSON schema below:\n\n"
      f"{schema_json}\n\n"
      "Do not include any extra commentary—only valid JSON."
  )

# --- Example Usage ---
if __name__ == '__main__':
  # This JSON schema is just an illustrative example. Adjust to match your actual fields.
  # For instance, you might include stats like short_range, long_range, ammo, traits, cost, etc.
  equipment_schema_json = (
      '{\n'
      '  "title": "EquipmentSchema",\n'
      '  "type": "object",\n'
      '  "properties": {\n'
      '    "name": { "type": "string" },\n'
      '    "range_short": { "type": "string" },\n'
      '    "range_long": { "type": "string" },\n'
      '    "strength": { "type": "string" },\n'
      '    "armor_penetration": { "type": "string" },\n'
      '    "damage": { "type": "string" },\n'
      '    "ammo_roll": { "type": "string" },\n'
      '    "traits": { "type": "array", "items": { "type": "string" } },\n'
      '    "cost": { "type": "string" },\n'
      '    "ammo_variants": {\n'
      '      "type": "array",\n'
      '      "items": {\n'
      '        "type": "object",\n'
      '        "properties": {\n'
      '          "name": { "type": "string" },\n'
      '          "traits": { "type": "array", "items": { "type": "string" } },\n'
      '          "cost": { "type": "string" }\n'
      '        }\n'
      '      }\n'
      '    }\n'
      '  }\n'
      '}'
  )

  # Generate a system prompt for general Necromunda equipment stats
  system_prompt = generate_equipment_system_prompt(equipment_schema_json)

  # Generate a user prompt for requesting Autopistol details, including ammo variants
  user_prompt = generate_equipment_user_prompt("Autopistol", "Static rounds, Shock rounds")

  # Generate a re-run prompt (for example, if the first attempt fails)
  rerun_prompt = generate_equipment_rerun_prompt("Autopistol", equipment_schema_json, attempt=2)

  print("=== System Prompt ===")
  print(system_prompt)
  print("\n=== User Prompt ===")
  print(user_prompt)
  print("\n=== Re-run Prompt ===")
  print(rerun_prompt)
