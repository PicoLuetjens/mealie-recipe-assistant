from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.core.security import current_user
from app.models.user import User
from app.schemas import MealieCreateResponse, RecipeDraft, RecipeGenerateRequest
from app.services.mealie_service import create_and_upload_image, create_recipe
from app.services.recipe_service import generate_recipe, transcribe_audio

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.post("/generate", response_model=RecipeDraft)
async def generate(body: RecipeGenerateRequest, _: User = Depends(current_user)):
    try: return await generate_recipe(body.message, body.servings)
    except Exception as exc: raise HTTPException(502, f"Rezeptentwurf fehlgeschlagen: {exc}") from exc

@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...), _: User = Depends(current_user)):
    try: return {"text": await transcribe_audio(audio.filename or "aufnahme.webm", await audio.read(), audio.content_type or "audio/webm")}
    except Exception as exc: raise HTTPException(502, f"Transkription fehlgeschlagen: {exc}") from exc

@router.post("/publish", response_model=MealieCreateResponse)
async def publish(recipe: RecipeDraft, with_image: bool = True, _: User = Depends(current_user)):
    try:
        slug = await create_recipe(recipe)
        image_status = await create_and_upload_image(recipe, slug) if with_image else "skipped"
        return MealieCreateResponse(slug=slug, image_status=image_status)
    except Exception as exc: raise HTTPException(502, f"Mealie-Speicherung fehlgeschlagen: {exc}") from exc

