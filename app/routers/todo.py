from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import AuthDep
from fastapi import status

todo_router = APIRouter(tags=["Todo Management"])

@todo_router.get("/todos", response_model=list[TodoResponse])
async def get_todos(db:SessionDep, user:AuthDep):
    return user.todos

@todo_router.get("/todo/{id}", response_model=TodoResponse)
async def get_todo(id:int, db:SessionDep, user:AuthDep):
    todo = db.exec(select(Todo).where(Todo.user_id == user.id, Todo.id == id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate":"Bearer"}
        )
    return todo

@todo_router.post("/todos", response_model=TodoCreate)
async def create_todo(db:SessionDep, user:AuthDep, todo_data:TodoCreate):
    new_todo = Todo(user_id=user.id, text=todo_data.text)
    try:
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        return new_todo
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while creating an item",
        )

@todo_router.delete("/todo/{id}", status_code=status.HTTP_200_OK)
def update_todo(id:int, db:SessionDep, user:AuthDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    try:
        db.delete(todo)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while deleting an item",
        )