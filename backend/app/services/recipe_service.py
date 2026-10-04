import json
import re
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas import Ingredient, RecipeDraft


def demo_recipe(servings: int) -> RecipeDraft:
    return RecipeDraft(name="Cremige Zitronen-Spinat-Pasta", description="Schnelle vegetarische Pasta mit frischer Zitrone.", servings=servings, prep_minutes=10, cook_minutes=15, ingredients=[Ingredient(amount=300, unit="g", name="Pasta"), Ingredient(amount=200, unit="g", name="Babyspinat"), Ingredient(amount=150, unit="ml", name="Kochsahne"), Ingredient(amount=1, unit="Stück", name="Bio-Zitrone"), Ingredient(amount=40, unit="g", name="Parmesan", note="gerieben"), Ingredient(name="Salz und Pfeffer", scalable=False)], instructions=["Pasta in Salzwasser kochen.", "Sahne mit Zitronenabrieb und -saft erhitzen.", "Spinat und Parmesan unterheben.", "Pasta mit etwas Kochwasser einrühren und abschmecken."], tags=["vegetarisch", "schnell"], image_prompt="Editorial food photography of creamy lemon spinach pasta, natural daylight, overhead")


def parse_draft(text: str, servings: int) -> RecipeDraft:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("Das Modell lieferte kein Rezept-JSON.")
    data = json.loads(match.group(0))
    data["servings"] = servings
    return RecipeDraft.model_validate(data)


async def generate_recipe(message: str, servings: int) -> RecipeDraft:
    if not settings.openai_ready:
        return demo_recipe(servings)
    schema = """Gib ausschließlich valides JSON zurück: {name,description,servings,prep_minutes,cook_minutes,ingredients:[{amount,unit,name,note,scalable}],instructions,tags,image_prompt}. Verwende metrische Einheiten. qualitative Mengen wie Salz nach Geschmack erhalten scalable:false."""
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.responses.create(model=settings.openai_recipe_model, instructions=schema, input=f"Entwirf ein Rezept für {servings} Personen. Wunsch: {message}")
    return parse_draft(response.output_text, servings)


async def transcribe_audio(filename: str, content: bytes, content_type: str) -> str:
    if not settings.openai_ready:
        raise RuntimeError("OpenAI ist nicht konfiguriert.")
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    result = await client.audio.transcriptions.create(model=settings.openai_transcribe_model, file=(filename, content, content_type))
    return result.text

