from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=12, max_length=128)
    is_admin: bool = False


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=100)
    is_active: bool | None = None
    is_admin: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    display_name: str
    is_admin: bool
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class Ingredient(BaseModel):
    amount: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=30)
    name: str = Field(min_length=1, max_length=160)
    note: str | None = Field(default=None, max_length=500)
    scalable: bool = True


class RecipeDraft(BaseModel):
    name: str
    description: str
    servings: int = Field(ge=1, le=100)
    prep_minutes: int = Field(ge=0, le=1440)
    cook_minutes: int = Field(ge=0, le=1440)
    ingredients: list[Ingredient] = Field(min_length=1)
    instructions: list[str] = Field(min_length=1)
    tags: list[str] = []
    image_prompt: str | None = None


class RecipeGenerateRequest(BaseModel):
    message: str = Field(min_length=3, max_length=2000)
    servings: int = Field(default=4, ge=1, le=100)


class MealieCreateResponse(BaseModel):
    slug: str
    image_status: str | None = None

