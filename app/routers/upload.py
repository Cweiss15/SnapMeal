from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.responses import AnalysisResponse, Ingredient, ChatRequest, ChatResponse, RecipeRequest, RecipeResponse
from app.storage.file_storage import save_uploads
from app.services.vision import analyze_fridge_image
from app.services.recipes import get_recipes
from app.services.chat import chat_with_ai
from app.database import get_db
from app.models.user import User
from app.models.image import UploadedImage
from app.models.food_preference import FoodPreference
from app.services.auth import get_current_user

router = APIRouter()

MAX_FILES = 20
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _get_user_preferences(db: Session, user: User) -> list[str]:
    prefs = db.query(FoodPreference).filter(FoodPreference.user_id == user.id).all()
    return [f"{p.preference_type}: {p.value}" for p in prefs]


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze fridge images",
    description=(
        "Upload up to 20 fridge/pantry images for ingredient detection and recipe "
        "suggestions. Accepts JPEG, PNG, and WebP files."
    ),
)
async def analyze_fridge(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
                detail=f"Unsupported file type '{f.content_type}' for '{f.filename}'. Allowed: JPEG, PNG, WebP.",
            )

    image_paths = await save_uploads(files)

    try:
        for path, upload_file in zip(image_paths, files):
            db.add(UploadedImage(
                user_id=current_user.id,
                file_path=str(path),
                original_filename=upload_file.filename,
            ))
        db.commit()

        all_ingredients: list[str] = []
        for path in image_paths:
            all_ingredients.extend(await analyze_fridge_image(path))

        seen: set[str] = set()
        unique_ingredients: list[str] = []
        for ingredient in all_ingredients:
            normalized = ingredient.lower()
            if normalized not in seen:
                seen.add(normalized)
                unique_ingredients.append(ingredient)

        preferences = _get_user_preferences(db, current_user)
        recipe_data = await get_recipes(unique_ingredients, preferences=preferences)
    finally:
        for path in image_paths:
            path.unlink(missing_ok=True)

    return AnalysisResponse(
        ingredients=[Ingredient(name=i) for i in unique_ingredients],
        recipes=recipe_data["recipes"],
        shopping_list=recipe_data.get("shopping_list", []),
    )


@router.post(
    "/recipes",
    response_model=RecipeResponse,
    summary="Regenerate recipes from ingredients",
)
async def regenerate_recipes(
    req: RecipeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not req.ingredients:
        raise HTTPException(status_code=400, detail="At least one ingredient is required.")

    preferences = _get_user_preferences(db, current_user)
    recipe_data = await get_recipes(req.ingredients, preferences=preferences)

    return RecipeResponse(
        recipes=recipe_data["recipes"],
        shopping_list=recipe_data.get("shopping_list", []),
    )


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat to refine recipes",
)
async def chat_refine(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    preferences = _get_user_preferences(db, current_user)
    result = await chat_with_ai(messages, req.ingredients, req.recipes, preferences=preferences)

    return ChatResponse(
        reply=result["reply"],
        updated_recipes=result.get("updated_recipes"),
        updated_shopping_list=result.get("updated_shopping_list"),
    )
