from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    database_url: str = "postgresql://postgres:postgres@localhost:5432/fridge_recipe_ai"
    jwt_secret: str = "change-me-in-production"

    model_config = {"env_file": ".env"}


settings = Settings()