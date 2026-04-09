from pydantic import BaseModel
from enum import Enum
from typing import Optional  # 加这个

class Role(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"

class LoginRequest(BaseModel):
    username: str
    password: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    name: str
    role: Role
    department: Optional[str] = None  # 改这行