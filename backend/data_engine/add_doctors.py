# backend/data_engine/add_doctor.py
"""
添加新医生
同时更新 users 表和 DOCTORS 列表
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User, Role
from data_engine.models import DOCTORS  # 导入当前医生列表
import hashlib
import base64

def simple_hash(password: str) -> str:
    salt = "piano-pir-salt"
    salted = password + salt
    hash_obj = hashlib.sha256(salted.encode())
    return base64.b64encode(hash_obj.digest()).decode()

def add_doctor(username, name, department, password="123456", title="住院医师"):
    """添加新医生"""
    print(f"添加医生: {username} - {name} ({department})")
    
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"❌ 医生 {username} 已存在")
            return False
        
        # 创建用户
        new_user = User(
            username=username,
            password=simple_hash(password),
            name=name,
            role=Role.DOCTOR,
            department=department
        )
        db.add(new_user)
        db.commit()
        print(f"✅ 医生账号创建成功: {username} / {password}")
        
        # 提示：需要手动更新 models.py 中的 DOCTORS 列表
        print(f"\n⚠️ 请手动更新 data_engine/models.py 中的 DOCTORS 列表，添加:")
        print(f'    {{"username": "{username}", "name": "{name}", "department": "{department}", "password": "{password}", "title": "{title}"}},')
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        add_doctor(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("用法: python add_doctor.py <用户名> <姓名> <科室> [密码]")
        print("示例: python add_doctor.py doc021 新医生 心内科")