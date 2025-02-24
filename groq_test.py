        def generate_detailed_territory_schema() -> str:
            """
            Returns a JSON schema string combining Territory and TerritoryEffect data.
            This schema is derived from the Pydantic models:
              - Territory: fields include name, type, controlled_by, x, y, lat, lng, elevation.
              - TerritoryEffect: fields include effect_id, name, description, income_bonus, reputation_bonus, special_rules.
            """
            schema = {
                "title": "DetailedTerritorySchema",
                "type": "object",
                "properties": {
                    "territory": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "controlled_by": {"type": ["string", "null"]},
                            "x": {"type": ["number", "null"]},
                            "y": {"type": ["number", "null"]},
                            "lat": {"type": ["number", "null"]},
                            "lng": {"type": ["number", "null"]},
                            "elevation": {"type": ["number", "null"]}
                        },
                        "required": ["name", "type"]
                    },
                    "effect": {
                        "type": "object",
                        "properties": {
                            "effect_id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "income_bonus": {"type": "integer"},
                            "reputation_bonus": {"type": "integer"},
                            "special_rules": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["effect_id", "name", "description"]
                    }
                },
                "required": ["territory", "effect"]
            }
            import json
            return json.dumps(schema, indent=2)

        def generate_territory_system_prompt(schema_json: str) -> str:
            """
            Generates a system prompt for detailed Necromunda territory generation.

            The prompt instructs the LLM to output a valid JSON object that strictly conforms
            to the given schema. It emphasizes that all territories are unique and should
            include detailed data on both the territory and its associated effect.
            """
            return (
                "You are a Necromunda territory generator for a Dominion Campaign. "
                "Each territory is unique and plays a critical role in the campaign by granting various boons. "
                "A territory includes both its core properties (such as name, type, control status, and location) "
                "and an associated effect detailing bonuses (income, reputation, and special rules).\n\n"
                "Generate a valid JSON object that strictly conforms to the JSON schema provided below. "
                "Do not include any extra commentary—output only the JSON object.\n\n"
                f"{schema_json}"
            )

        def generate_territory_user_prompt(territory_name: str) -> str:
            """
            Generates a user prompt for requesting detailed information for a specific territory.

            Parameters:
              - territory_name: The name of the territory to generate details for.

            The prompt asks the LLM to produce complete data on the territory and its effect.
            """
            return (
                f"Provide detailed information for the territory named '{territory_name}' in a Dominion Campaign. "
                "Include all relevant data for both the territory and its effect as specified by the JSON schema."
            )

        def generate_territory_rerun_prompt(territory_name: str, schema_json: str, attempt: int) -> str:
            """
            Generates a re-run prompt for territory generation if the initial output fails validation.

            Parameters:
              - territory_name: The name of the territory.
              - schema_json: The JSON schema the output must conform to.
              - attempt: The current attempt number.

            The prompt reminds the LLM to strictly follow the schema and output only valid JSON.
            """
            return (
                f"This is re-run attempt number {attempt} for generating the territory '{territory_name}'. "
                "Ensure that your output strictly conforms to the JSON schema provided below. "
                "Output only valid JSON with no extra commentary.\n\n"
                f"{schema_json}"
            )

        # --- Example Usage ---
        if __name__ == '__main__':
            # Generate the detailed territory JSON schema from the Pydantic models.
            territory_schema_json = generate_detailed_territory_schema()

            # Generate the system prompt.
            system_prompt = generate_territory_system_prompt(territory_schema_json)

            # Generate a user prompt for a territory, e.g., "Gambling Den".
            user_prompt = generate_territory_user_prompt("Gambling Den")

            # Generate a re-run prompt (for instance, on attempt number 2).
            rerun_prompt = generate_territory_rerun_prompt("Gambling Den", territory_schema_json, attempt=2)

            print("=== System Prompt ===")
            print(system_prompt)
            print("\n=== User Prompt ===")
            print(user_prompt)
            print("\n=== Re-run Prompt ===")
            print(rerun_prompt)
