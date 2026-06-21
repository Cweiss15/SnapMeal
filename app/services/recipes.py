import json

from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def get_recipes(ingredients: list[str], preferences: list[str] | None = None) -> dict:
    ingredient_list = ", ".join(ingredients)

    preference_text = ""
    if preferences:
        preference_text = (
            "\n\nIMPORTANT - The user has these food preferences/restrictions:\n"
            + "\n".join(f"- {p}" for p in preferences)
            + "\n\nYou MUST respect these when suggesting recipes."
        )

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": (
                    f"I have these ingredients available: {ingredient_list}\n\n"
                    "Suggest 3 real, well-known, top-rated recipes I can make. "
                    "Prioritize using the ingredients I already have, but you may "
                    "include common pantry staples or a few extra ingredients I'd need to buy.\n\n"
                    "For each recipe, include exact measurements (cups, tablespoons, "
                    "ounces, etc.) in the ingredients list and provide detailed "
                    "step-by-step cooking instructions.\n\n"
                    "Return your response as JSON in this exact format:\n"
                    "{\n"
                    '  "recipes": [\n'
                    "    {\n"
                    '      "name": "Recipe Name",\n'
                    '      "ingredients": ["2 cups flour", "1 tbsp olive oil", "3 eggs"],\n'
                    '      "instructions": ["Step 1: detailed instruction", "Step 2: detailed instruction"]\n'
                    "    }\n"
                    "  ],\n"
                    '  "shopping_list": ["item1", "item2"]\n'
                    "}\n\n"
                    "The shopping_list should ONLY contain ingredients that are NOT in "
                    "my available list above but are needed for the recipes.\n\n"
                    "Return ONLY valid JSON, no other text."
                    + preference_text
                ),
            }
        ],
        max_tokens=2500,
    )

    result_text = response.choices[0].message.content.strip()

    if result_text.startswith("```"):
        result_text = result_text.split("\n", 1)[1]
        result_text = result_text.rsplit("```", 1)[0].strip()

    return json.loads(result_text)
