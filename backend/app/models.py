from sqlalchemy import Column, Integer, String, Enum, Date, Text
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import date 

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

    gender = Column(String(10), default='男')
    birth_date = Column(Date, nullable=True)
    title = Column(String(50), default='主治医师')
    phone = Column(String(20), default='')
    email = Column(String(100), default='')
    join_date = Column(Date, default=date.today)  # 入职日期，默认为今天
    bio = Column(Text, default='')
    avatar = Column(Text, default='')