from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.food_preference import FoodPreference
from app.services.auth import get_current_user

router = APIRouter(prefix="/preferences", tags=["preferences"])


class PreferenceCreate(BaseModel):
    preference_type: str  # allergy, dislike, diet, cuisine_preference
    value: str


class PreferenceResponse(BaseModel):
    id: int
    preference_type: str
    value: str

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[PreferenceResponse])
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(FoodPreference).filter(FoodPreference.user_id == current_user.id).all()


@router.post("/", response_model=PreferenceResponse, status_code=201)
def add_preference(
    data: PreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    valid_types = {"allergy", "dislike", "diet", "cuisine_preference"}
    if data.preference_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"preference_type must be one of: {valid_types}")

    pref = FoodPreference(
        user_id=current_user.id,
        preference_type=data.preference_type,
        value=data.value,
    )
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref


@router.delete("/{preference_id}", status_code=204)
def delete_preference(
    preference_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pref = db.query(FoodPreference).filter(
        FoodPreference.id == preference_id,
        FoodPreference.user_id == current_user.id,
    ).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    db.delete(pref)
    db.commit()
