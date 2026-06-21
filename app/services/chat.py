import json

from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = (
    "You are a helpful cooking assistant for the SnapMeal app. "
    "The user has uploaded photos of their fridge and you identified ingredients. "
    "Now the user wants to refine the results. They might:\n"
    "- Tell you they don't actually have certain ingredients\n"
    "- Tell you they have additional ingredients not detected\n"
    "- Request specific types of recipes (e.g., Italian, quick meals, vegetarian, desserts)\n"
    "- Ask for more or fewer recipes\n"
    "- Ask for substitutions\n"
    "- Ask questions about recipes, cooking techniques, ingredient storage, etc.\n"
    "When the user's request involves changing the given recipes or regenrating based on new requests, include a JSON block "
    "wrapped in ```json\\n...\\n``` with this format:\n"
    '{"recipes": [{"name": "...", "ingredients": ["2 cups flour", "1 tbsp oil"], '
    '"instructions": ["Step 1: ...", "Step 2: ..."]}], "shopping_list": ["..."]}\n\n'
    "IMPORTANT RULES:\n"
    "- Recipes must be real, highly-rated recipes with exact measurements.\n"
    "- The shopping_list should only include items NOT in the user's ingredient list.\n"
    "- Do NOT list the recipes in your conversational reply. Just say something like "
    "'I\\'ve regenerated your recipes to match your preferences!' and include the JSON block.\n"
    "- If the user is just chatting or asking questions without needing recipe updates, "
    "reply conversationally without any JSON block."
)


async def chat_with_ai(
    messages: list[dict],
    ingredients: list[str],
    recipes: list[dict] | None = None,
    preferences: list[str] | None = None,
) -> dict:
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if ingredients:
        context = f"Currently detected ingredients: {', '.join(ingredients)}"
        if recipes:
            recipe_names = [r.get("name", "Unknown") for r in recipes]
            context += f"\nCurrent recipes: {', '.join(recipe_names)}"
        if preferences:
            context += "\n\nUser food preferences/restrictions:\n" + "\n".join(f"- {p}" for p in preferences)
        api_messages.append({"role": "system", "content": context})

    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=api_messages,
        max_tokens=2000,
    )

    reply_text = response.choices[0].message.content.strip()

    updated_recipes = None
    updated_shopping_list = None

    if "```json" in reply_text:
        try:
            json_start = reply_text.index("```json") + 7
            json_end = reply_text.index("```", json_start)
            json_str = reply_text[json_start:json_end].strip()
            data = json.loads(json_str)
            updated_recipes = data.get("recipes")
            updated_shopping_list = data.get("shopping_list", [])
            reply_text = reply_text[:reply_text.index("```json")].strip()
            if not reply_text:
                reply_text = "I've regenerated your recipes to match your preferences!"
        except (ValueError, json.JSONDecodeError):
            pass

    return {
        "reply": reply_text,
        "updated_recipes": updated_recipes,
        "updated_shopping_list": updated_shopping_list,
    }
