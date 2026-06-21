from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str
    quantity: str | None = None


class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    instructions: list[str]


class AnalysisResponse(BaseModel):
    ingredients: list[Ingredient]
    recipes: list[Recipe]
    shopping_list: list[str]


class RecipeRequest(BaseModel):
    ingredients: list[str]


class RecipeResponse(BaseModel):
    recipes: list[Recipe]
    shopping_list: list[str]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    ingredients: list[str]
    recipes: list[dict] | None = None


class ChatResponse(BaseModel):
    reply: str
    updated_recipes: list[Recipe] | None = None
    updated_shopping_list: list[str] | None = None