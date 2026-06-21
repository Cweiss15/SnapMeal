from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.recipe import FavoriteRecipe
from app.services.auth import get_current_user

router = APIRouter(prefix="/favorites", tags=["favorites"])


class FavoriteCreate(BaseModel):
    name: str
    ingredients: list[str]
    instructions: list[str]


class FavoriteResponse(BaseModel):
    id: int
    name: str
    ingredients: list[str]
    instructions: list[str]
    created_at: str | None = None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[FavoriteResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipes = db.query(FavoriteRecipe).filter(FavoriteRecipe.user_id == current_user.id).all()
    return [
        FavoriteResponse(
            id=r.id,
            name=r.name,
            ingredients=r.ingredients,
            instructions=r.instructions,
            created_at=r.created_at.isoformat() if r.created_at else None,
        )
        for r in recipes
    ]


@router.post("/", response_model=FavoriteResponse, status_code=201)
def add_favorite(
    data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = FavoriteRecipe(
        user_id=current_user.id,
        name=data.name,
        ingredients=data.ingredients,
        instructions=data.instructions,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return FavoriteResponse(
        id=recipe.id,
        name=recipe.name,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        created_at=recipe.created_at.isoformat() if recipe.created_at else None,
    )


@router.delete("/{recipe_id}", status_code=204)
def delete_favorite(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = db.query(FavoriteRecipe).filter(
        FavoriteRecipe.id == recipe_id,
        FavoriteRecipe.user_id == current_user.id,
    ).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Favorite recipe not found")
    db.delete(recipe)
    db.commit()
