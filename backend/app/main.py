from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, recipes, users
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.user import User

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.query(User).first():
            db.add(User(email=settings.first_admin_email.lower(), display_name="Administrator", password_hash=hash_password(settings.first_admin_password), is_admin=True))
            db.commit()
    yield

app = FastAPI(title="Mealie Recipe Assistant API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")

@app.get("/api/health")
def health(): return {"status": "ok", "openai_configured": settings.openai_ready, "mealie_configured": settings.mealie_ready}

