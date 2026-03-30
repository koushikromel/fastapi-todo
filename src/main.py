from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status
from sqlmodel import Field, SQLModel, create_engine, Session, select
from typing import Optional


class TodoBase(SQLModel):
    title: str

class Todo(TodoBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TodoUpdate(SQLModel):
    completed: bool

engine = create_engine(
    "sqlite:///database.db",
    echo=True,
    connect_args={"check_same_thread": False}
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)


@app.get('/', status_code=status.HTTP_200_OK)
async def get_todos(completed: bool | None = None):
    with Session(engine) as session:
        results = session.exec(
            select(Todo).where(Todo.completed == completed)
            if completed is not None
            else select(Todo)
        ).all()
    return results

@app.post('/', status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoBase):
    todo = Todo(title=todo.title)
    with Session(engine) as session:
        session.add(todo)
        session.commit()
    return {"message": "Todo Created successfully", "data": todo}

@app.put('/{id}', status_code=status.HTTP_200_OK)
async def update_todo(id: UUID, data: TodoUpdate):
    print('id', id)
    with Session(engine) as session:
        statement = select(Todo).where(Todo.id == id)
        todo = session.exec(statement).one_or_none()
        if not todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id: {id} not found")
        todo.completed = data.completed
        todo.updated_at = datetime.now(timezone.utc)
        session.add(todo)
        session.commit()
        session.refresh(todo)
    return {"message": "Todo updated successfully", "completed": todo.completed}

@app.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(id: UUID):
    with Session(engine) as session:
        statement = select(Todo).where(Todo.id == id)
        todo = session.exec(statement).one_or_none()
        if todo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Todo not foudn with id: {id}')
        session.delete(todo)
        session.commit()
    return
