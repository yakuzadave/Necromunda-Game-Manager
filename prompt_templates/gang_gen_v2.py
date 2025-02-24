def generate_system_prompt(faction_name: str, schema_json: str, credit_limit: int, rules: str) -> str:
  """
  Generates a system prompt with strict model-aware validation.
  """
  return (
      f"You are a Necromunda rules validator specializing in {faction_name} gangs. "
      "Generate JSON data that strictly conforms to these requirements:\n\n"
      "1. **Fighter Validation**:\n"
      "- Stat values (m, ws, bs, etc.) must be within 1-6 range\n"
      "- Intelligence (int) must be 1-6\n"
      "- Equipment lists must include ALL carried items with quantities\n"
      "- Injuries must specify severity (Minor/Major/Critical) and permanence\n"
      "- Skills must match fighter type restrictions\n\n"
      "2. **Gang Composition**:\n"
      f"- {rules}\n"
      "- Stash equipment must be separate from fighter inventories\n"
      "- Territories must exist in campaign data\n\n"
      "3. **Economic Rules**:\n"
      f"- Total gang value (fighters + equipment) ≤ {credit_limit}\n"
      "- Individual fighter costs must include equipment value\n"
      "- Stash items count toward total gang value\n\n"
      "4. **Temporal Consistency**:\n"
      "- datetime_added must be ISO format\n"
      "- Advancement dates must be chronologically ordered\n\n"
      "5. **Model Relationships**:\n"
      "- Injuries must reference valid injury IDs\n"
      "- Territories must match existing campaign territories\n"
      "- Equipment traits must use official trait names\n\n"
      f"Output must EXACTLY match this JSON Schema:\n{schema_json}\n"
      "Include ALL model fields except optional images\n"
      "Use official names from Necromunda Rulebook\n"
      "No markdown - ONLY valid JSON"
  )

def generate_user_prompt(gang_name: str) -> str:
  """
  Generates a user prompt with model-specific details.
  """
  return (
      f"Create '{gang_name}' with:\n"
      "- Realistic stat distributions per fighter type\n"
      "- 2-4 equipment items per fighter (include traits)\n"
      "- At least one injury for 25% of fighters\n"
      "- 1-2 advancements per experienced fighter\n"
      "- 3-5 territory effects for controlled territories\n"
      "- Minimum 3 skills for Leaders/Champions\n"
      "- Gang-specific weapon preferences (e.g., Escher=needle weapons)\n"
      "- Chronologically consistent datetime fields\n"
      "- Unique UUIDs for all entities"
  )

def generate_rerun_prompt(gang_name: str, schema_json: str, credit_limit: int, 
                      rules: str, attempt: int, validation_errors: list) -> str:
  """
  Generates an error-specific rerun prompt.
  """
  return (
      f"Re-attempt #{attempt} for {gang_name} - Fix these model errors:\n"
      "VALIDATION ISSUES:\n- " + "\n- ".join(validation_errors) + "\n\n"
      "REQUIRED CORRECTIONS:\n"
      "1. Maintain all UUID relationships\n"
      "2. Verify stat ranges:\n"
      "   - m/ws/bs/s/t/w/i/a: 1-6\n"
      "   - ld/cl/wil/int: 1-6\n"
      "3. Ensure datetime formats: YYYY-MM-DDTHH:MM:SS\n"
      "4. Validate equipment traits against:\n"
      "   - Gas, Rapid Fire, Scarce, etc.\n"
      "5. Check injury severity levels\n\n"
      "JSON REQUIREMENTS:\n"
      f"{json.dumps(json.loads(schema_json), indent=2)}\n\n"
      "Output ONLY the corrected JSON with:\n"
      "- Valid model relationships\n"
      "- Proper UUID formatting\n"
      "- Chronological timestamps\n"
      "NO EXPLANATIONS"
  )