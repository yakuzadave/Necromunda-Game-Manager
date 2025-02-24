def generate_system_prompt(faction_name: str, schema_json: str, credit_limit: int, rules: str) -> str:
  """
  Generates the system prompt for gang generation.

  Parameters:
  - faction_name: Name of the faction (e.g., "Escher").
  - schema_json: A string containing the JSON schema for the gang.
  - credit_limit: The maximum credit limit for the gang (e.g., 1000).
  - rules: A description of the composition rules (e.g., "exactly one Leader, at most two Champions, and at least three Gangers").

  Returns:
  - A prompt string to instruct the LLM.
  """
  return (
      f"You are a Necromunda gang database for the {faction_name} faction. "
      "Your task is to generate a valid JSON object that strictly conforms to the JSON schema provided below.\n\n"
      f"{schema_json}\n\n"
      f"The gang must be built within a {credit_limit}-credit limit and abide by the following rules: {rules}. "
      "Do not include any extra commentary or text; output only the JSON object."
  )

def generate_user_prompt(gang_name: str) -> str:
  """
  Generates the user prompt for gang generation.

  Parameters:
  - gang_name: The name of the gang to generate (e.g., "The Wild Bunch").

  Returns:
  - A prompt string to instruct the LLM on what gang details to produce.
  """
  return f"Provide the details for the gang named '{gang_name}'."

def generate_rerun_prompt(gang_name: str, schema_json: str, credit_limit: int, rules: str, attempt: int) -> str:
  """
  Generates a re-run prompt with additional instructions in case the first generation fails.

  Parameters:
  - gang_name: The name of the gang (e.g., "The Wild Bunch").
  - schema_json: A string containing the JSON schema for the gang.
  - credit_limit: The maximum credit limit (e.g., 1000).
  - rules: A description of the composition rules.
  - attempt: The current re-run attempt number.

  Returns:
  - A prompt string for the re-run attempt.
  """
  return (
      f"This is re-run attempt number {attempt} for generating the gang '{gang_name}'. "
      "Ensure your output strictly conforms to the JSON schema below:\n\n"
      f"{schema_json}\n\n"
      f"The gang must be built within a {credit_limit}-credit limit and adhere to the following rules: {rules}. "
      "Output only valid JSON without any additional commentary."
  )

# --- Example Usage ---
if __name__ == '__main__':
  # Define your parameters
  faction_name = "Escher"
  credit_limit = 1000
  rules = "exactly one Leader, at most two Champions, and at least three Gangers"

  # Example JSON schema string (typically you would use something like json.dumps(GangSchema.model_json_schema(), indent=2))
  schema_json = (
      '{\n'
      '  "title": "GangSchema",\n'
      '  "type": "object",\n'
      '  "properties": {\n'
      '    "gang_name": { "type": "string" },\n'
      '    "members": {\n'
      '      "type": "array",\n'
      '      "items": {\n'
      '        "type": "object",\n'
      '        "properties": {\n'
      '          "name": { "type": "string" },\n'
      '          "rank": { "type": "string" },\n'
      '          "cost": { "type": "integer" },\n'
      '          "skills": { "type": "array", "items": { "type": "string" } },\n'
      '          "weapons": {\n'
      '            "type": "array",\n'
      '            "items": {\n'
      '              "type": "object",\n'
      '              "properties": {\n'
      '                "name": { "type": "string" },\n'
      '                "cost": { "type": "integer" },\n'
      '                "type": { "type": "string" },\n'
      '                "restrictions": { "type": "array", "items": { "type": "string" } }\n'
      '              }\n'
      '            }\n'
      '          },\n'
      '          "equipment": {\n'
      '            "type": "array",\n'
      '            "items": {\n'
      '              "type": "object",\n'
      '              "properties": {\n'
      '                "name": { "type": "string" },\n'
      '                "cost": { "type": "integer" }\n'
      '              }\n'
      '            }\n'
      '          }\n'
      '        }\n'
      '      }\n'
      '    },\n'
      '    "territories": { "type": "array", "items": { "type": "string" } }\n'
      '  }\n'
      '}'
  )

  gang_name = "The Wild Bunch"

  # Generate the prompts
  system_prompt = generate_system_prompt(faction_name, schema_json, credit_limit, rules)
  user_prompt = generate_user_prompt(gang_name)
  rerun_prompt = generate_rerun_prompt(gang_name, schema_json, credit_limit, rules, attempt=2)

  # Print the prompts for review
  print("=== System Prompt ===")
  print(system_prompt)
  print("\n=== User Prompt ===")
  print(user_prompt)
  print("\n=== Re-run Prompt ===")
  print(rerun_prompt)
