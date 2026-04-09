# backend/app/security.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import hashlib
import base64

SECRET_KEY = "pir-emr-2026"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60 * 24 * 30  # 30天

# 使用更兼容的配置
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)

def simple_hash(password: str) -> str:
    """简单的 SHA256 加密（用于兼容旧数据）"""
    salt = "piano-pir-salt"
    salted = password + salt
    hash_obj = hashlib.sha256(salted.encode())
    return base64.b64encode(hash_obj.digest()).decode()

def hash_password(password: str) -> str:
    """加密密码"""
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码（兼容 bcrypt 和简单加密）"""
    # 确保密码长度不超过72字节
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    
    # 先尝试 bcrypt 验证
    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except:
        pass
    
    # 再尝试简单加密验证（兼容旧数据）
    try:
        return simple_hash(plain_password) == hashed_password
    except:
        return False

def create_token(data: dict) -> str:
    """创建 JWT token"""
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)