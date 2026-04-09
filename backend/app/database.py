from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# 使用现有的 hospital.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./storage/hospital.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """只创建 users 表，不影响已有的 records 表"""
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()