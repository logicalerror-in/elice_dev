from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, posts
from app.core.config import settings
from app.core.errors import register_handlers
from app.db.session import engine
from app.db.base import Base
import app.models.user
import app.models.post


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="elice-dev", version="0.1.0", lifespan=lifespan)

register_handlers(app)

allow_origins = ["*"] if settings.CORS_ALLOW_ALL else settings.cors_origins_list()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])


@app.get("/")
def root():
    return {"status": "ready"}