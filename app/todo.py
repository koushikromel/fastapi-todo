from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status, APIRouter
from sqlmodel import Session, select

from app.db import engine
from app.models import Todo, TodoUpdate, TodoBase


from fastapi import Depends
from app.dependencies import get_current_user

todo_router = APIRouter(dependencies=[Depends(get_current_user)])


@todo_router.get("/home")
async def todo_home():
    return "Todo Home"


@todo_router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(completed: bool | None = None):
    with Session(engine) as session:
        results = session.exec(
            select(Todo).where(Todo.completed == completed)
            if completed is not None
            else select(Todo)
        ).all()
    return results


@todo_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoBase):
    new_todo = Todo(title=todo.title)
    with Session(engine) as session:
        session.add(new_todo)
        session.commit()
        session.refresh(new_todo)
    return new_todo


@todo_router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_todo(id: UUID, data: TodoUpdate):
    with Session(engine) as session:
        statement = select(Todo).where(Todo.id == id)
        todo = session.exec(statement).one_or_none()
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id: {id} not found",
            )

        todo.completed = data.completed
        todo.updated_at = datetime.now(timezone.utc)

        session.add(todo)
        session.commit()
        session.refresh(todo)
    return todo


@todo_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(id: UUID) -> None:
    with Session(engine) as session:
        statement = select(Todo).where(Todo.id == id)
        todo = session.exec(statement).one_or_none()
        if todo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo not foudn with id: {id}",
            )
        session.delete(todo)
        session.commit()
    return
