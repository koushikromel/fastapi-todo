from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Depends
from sqlmodel import SQLModel
from starlette.middleware.sessions import SessionMiddleware

from app.db import engine
from app.todo import todo_router
from app.auth import auth_router
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)

settings = get_settings()
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY.get_secret_value())

app.include_router(auth_router)


from app.dependencies import get_current_user

@app.get("/")
async def home(user: dict = Depends(get_current_user)):
    time = datetime.now(timezone.utc).isoformat()
    return f"Hello, {user.get('name', 'world')}! Current time: {time}"


app.include_router(todo_router, prefix="/todo")
