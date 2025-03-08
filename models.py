from typing import Annotated, List, Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class SubTaskCreate(BaseModel):
    title: str
    completed: bool = False

class SubTaskOut(SubTaskCreate):
    id: int

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    subtasks: List[SubTaskCreate] = []

class TaskOut(TaskCreate):
    id: int
    subtasks: List[SubTaskOut] = []
