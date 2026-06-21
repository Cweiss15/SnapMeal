from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str
    display_name: str | None = None


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    display_name: str | None

    model_config = {"from_attributes": True}
