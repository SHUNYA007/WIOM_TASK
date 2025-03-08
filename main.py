from fastapi import FastAPI, Depends, HTTPException, status
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Optional
from models import UserCreate, UserOut, Token, TaskCreate, TaskOut, SubTaskCreate, SubTaskOut
from service import UserService
from db import users_db, tasks_db, subtasks_db

app = FastAPI()

task_id_counter = 1
subtask_id_counter = 1
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@app.post("/register", response_model=UserOut, status_code=201)
def register(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    users_db[user.username] = UserService.get_password_hash(user.password)
    return {"username": user.username}


@app.post("/login", response_model=Token)
def login(user: UserCreate):
    if user.username not in users_db or not UserService.verify_password(user.password, users_db[user.username]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = UserService.create_access_token({"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(task: TaskCreate, token: str):
    global task_id_counter, subtask_id_counter
    username = UserService.get_current_user(token)
    task_id = task_id_counter
    task_id_counter += 1
    subtasks = []
    for subtask in task.subtasks:
        subtask_id = subtask_id_counter
        subtask_id_counter += 1
        subtasks.append({"id": subtask_id, "title": subtask.title, "completed": subtask.completed})
    tasks_db[task_id] = {"id": task_id, "title": task.title, "description": task.description, "completed": task.completed, "owner": username, "subtasks": subtasks}
    return tasks_db[task_id]

@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: TaskCreate, token: str):
    username = UserService.get_current_user(token)
    if task_id not in tasks_db or tasks_db[task_id]["owner"] != username:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks_db[task_id].update(task.dict())
    return tasks_db[task_id]

@app.put("/tasks/{task_id}/subtasks/{subtask_id}", response_model=SubTaskOut)
def update_subtask(task_id: int, subtask_id: int, subtask: SubTaskCreate, token: str):
    username = UserService.get_current_user(token)
    if task_id not in tasks_db or tasks_db[task_id]["owner"] != username:
        raise HTTPException(status_code=404, detail="Task not found")
    for s in tasks_db[task_id]["subtasks"]:
        if s["id"] == subtask_id:
            s.update(subtask.dict())
            return s
    raise HTTPException(status_code=404, detail="Subtask not found")

@app.patch("/tasks/{task_id}/status")
def update_task_status(task_id: int, completed: bool, token: str):
    username = UserService.get_current_user(token)
    if task_id not in tasks_db or tasks_db[task_id]["owner"] != username:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks_db[task_id]["completed"] = completed
    return {"message": "Task status updated"}

@app.patch("/tasks/{task_id}/subtasks/{subtask_id}/status")
def update_subtask_status(task_id: int, subtask_id: int, completed: bool, token: str):
    username = UserService.get_current_user(token)
    if task_id not in tasks_db or tasks_db[task_id]["owner"] != username:
        raise HTTPException(status_code=404, detail="Task not found")
    for s in tasks_db[task_id]["subtasks"]:
        if s["id"] == subtask_id:
            s["completed"] = completed
            return {"message": "Subtask status updated"}
    raise HTTPException(status_code=404, detail="Subtask not found")

@app.post("/tasks/{task_id}/subtasks", response_model=SubTaskOut, status_code=201)
def create_subtask(subtask: SubTaskCreate, task_id: int, token: str):
    global subtask_id_counter
    username = UserService.get_current_user(token)
    if task_id not in tasks_db or tasks_db[task_id]["owner"] != username:
        raise HTTPException(status_code=404, detail="Task not found")
    subtask_id = subtask_id_counter
    subtask_id_counter += 1
    new_subtask = {"id": subtask_id, "title": subtask.title, "completed": subtask.completed}
    tasks_db[task_id]["subtasks"].append(new_subtask)
    return new_subtask

@app.get("/tasks/{task_id}/subtasks", response_model=List[SubTaskOut])
def get_subtasks(task_id: int, token: str):
    username = UserService.get_current_user(token)
    if task_id not in tasks_db or tasks_db[task_id]["owner"] != username:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]["subtasks"]

@app.get("/tasks", response_model=List[TaskOut])
def get_tasks(token: str):
    username = UserService.get_current_user(token)
    return [task for task in tasks_db.values() if task["owner"] == username]

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, token: str):
    username = UserService.get_current_user(token)
    if task_id not in tasks_db or tasks_db[task_id]["owner"] != username:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return {"message": "Task deleted"}
