import json

from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)


async def get_recipes(ingredients: list[str]) -> dict:
    ingredient_list = ", ".join(ingredients)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": (
                    f"I have these ingredients: {ingredient_list}\n\n"
                    "Suggest 3 recipes I can make. For each recipe, also list any "
                    "extra ingredients I would need to buy.\n\n"
                    "Return your response as JSON in this exact format:\n"
                    "{\n"
                    '  "recipes": [\n'
                    "    {\n"
                    '      "name": "Recipe Name",\n'
                    '      "ingredients": ["ingredient1", "ingredient2"],\n'
                    '      "instructions": ["Step 1", "Step 2"]\n'
                    "    }\n"
                    "  ],\n"
                    '  "shopping_list": ["item1", "item2"]\n'
                    "}\n\n"
                    "Return ONLY valid JSON, no other text."
                ),
            }
        ],
        max_tokens=1500,
    )

    result_text = response.choices[0].message.content.strip()

    if result_text.startswith("```"):
        result_text = result_text.split("\n", 1)[1]
        result_text = result_text.rsplit("```", 1)[0].strip()

    return json.loads(result_text)