from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db import engine
from app.todo import todo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def home():
    time = datetime.now(timezone.utc).isoformat()
    return f"asdHello, world! Current time: {time}"


app.include_router(todo_router, prefix="/todo")
