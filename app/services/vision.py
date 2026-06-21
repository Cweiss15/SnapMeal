import base64
from pathlib import Path

from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def analyze_fridge_image(image_path: Path) -> list[str]:
    suffix = image_path.suffix.lower()
    if suffix == ".png":
        mime_type = "image/png"
    elif suffix == ".webp":
        mime_type = "image/webp"
    else:
        mime_type = "image/jpeg"

    image_data = base64.b64encode(image_path.read_bytes()).decode("utf-8")

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Look at this image of a refrigerator/pantry/cabinet. "
                            "List every food ingredient you can identify. "
                            "Return ONLY a comma-separated list of ingredients, nothing else. "
                            "Example: eggs, milk, butter, cheddar cheese, lettuce, tomatoes"
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_data}"
                        },
                    },
                ],
            }
        ],
        max_tokens=500,
    )

    ingredients_text = response.choices[0].message.content.strip()
    return [i.strip() for i in ingredients_text.split(",") if i.strip()]
