from fastapi import APIRouter, UploadFile, File, HTTPException

from app.schemas.responses import AnalysisResponse, Ingredient
from app.storage.file_storage import save_uploads
from app.services.vision import analyze_fridge_image
from app.services.recipes import get_recipes

router = APIRouter()

MAX_FILES = 20
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze fridge images",
    description=(
        "Upload up to 20 fridge/pantry images for ingredient detection and recipe "
        "suggestions. Accepts JPEG, PNG, and WebP files. Requests with zero files "
        "or more than 20 files are rejected."
    ),
)
async def analyze_fridge(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="At least one image file is required.")

    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=422,
            detail=f"Too many files. Maximum is {MAX_FILES}, but {len(files)} were provided.",
        )

    for f in files:
        if f.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported file type '{f.content_type}' for file '{f.filename}'. Allowed types: JPEG, PNG, WebP.",
            )

    image_paths = await save_uploads(files)

    all_ingredients: list[str] = []
    for path in image_paths:
        ingredients = await analyze_fridge_image(path)
        all_ingredients.extend(ingredients)

    seen: set[str] = set()
    unique_ingredients: list[str] = []
    for ingredient in all_ingredients:
        normalized = ingredient.lower()
        if normalized not in seen:
            seen.add(normalized)
            unique_ingredients.append(ingredient)

    recipe_data = await get_recipes(unique_ingredients)

    return AnalysisResponse(
        ingredients=[Ingredient(name=i) for i in unique_ingredients],
        recipes=recipe_data["recipes"],
        shopping_list=recipe_data.get("shopping_list", []),
    )