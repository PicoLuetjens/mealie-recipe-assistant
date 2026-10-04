import base64
import httpx
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas import RecipeDraft


def recipe_payload(recipe: RecipeDraft) -> dict:
    return {"name": recipe.name, "description": recipe.description, "recipeYield": str(recipe.servings), "prepTime": f"PT{recipe.prep_minutes}M", "performTime": f"PT{recipe.cook_minutes}M", "recipeIngredient": [{"quantity": item.amount, "unit": item.unit, "note": " ".join(part for part in [item.name, item.note] if part)} for item in recipe.ingredients], "recipeInstructions": [{"text": step} for step in recipe.instructions], "extras": {"recipe-assistant": {"baseServings": recipe.servings, "source": "openai"}}}


async def create_recipe(recipe: RecipeDraft) -> str:
    if not settings.mealie_ready:
        raise RuntimeError("Mealie ist nicht konfiguriert.")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{settings.mealie_base_url.rstrip('/')}/api/recipes", headers={"Authorization": f"Bearer {settings.mealie_api_token}"}, json=recipe_payload(recipe))
        response.raise_for_status()
    return response.json()


async def create_and_upload_image(recipe: RecipeDraft, slug: str) -> str:
    if not settings.openai_ready or not recipe.image_prompt:
        return "skipped"
    image = await AsyncOpenAI(api_key=settings.openai_api_key).images.generate(model=settings.openai_image_model, prompt=recipe.image_prompt, size="1024x1024")
    raw = base64.b64decode(image.data[0].b64_json)
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.put(f"{settings.mealie_base_url.rstrip('/')}/api/recipes/{slug}/image", headers={"Authorization": f"Bearer {settings.mealie_api_token}"}, files={"image": ("recipe.png", raw, "image/png")})
        response.raise_for_status()
    return "uploaded"

