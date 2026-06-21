from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    preferences = relationship("FoodPreference", back_populates="user", cascade="all, delete-orphan")
    favorite_recipes = relationship("FavoriteRecipe", back_populates="user", cascade="all, delete-orphan")
    uploaded_images = relationship("UploadedImage", back_populates="user", cascade="all, delete-orphan")
