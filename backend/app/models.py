from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class Role(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(200), nullable=False)
    name = Column(String(50), nullable=False)
    role = Column(Enum(Role), nullable=False)
    department = Column(String(100), nullable=True)