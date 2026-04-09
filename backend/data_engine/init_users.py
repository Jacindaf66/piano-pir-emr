# backend/data_engine/init_users.py
"""
初始化用户表
从 models.py 导入医生列表，保持数据一致
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, SessionLocal
from app.models import User, Role
from data_engine.models import DOCTORS  # 从共享模型导入
import hashlib
import base64

def simple_hash(password: str) -> str:
    """简单的 SHA256 加密"""
    salt = "piano-pir-salt"
    salted = password + salt
    hash_obj = hashlib.sha256(salted.encode())
    return base64.b64encode(hash_obj.digest()).decode()

def init_users():
    print("=" * 50)
    print("初始化用户系统...")
    print("=" * 50)
    
    # 1. 创建 users 表
    print("\n📋 创建用户表...")
    init_db()
    print("✅ 用户表创建完成")
    
    # 2. 添加用户
    print("\n👥 添加用户...")
    db = SessionLocal()
    try:
        # 创建管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                password=simple_hash("123456"),
                name="系统管理员",
                role=Role.ADMIN,
                department="系统管理部"
            )
            db.add(admin_user)
            print("  ✅ 管理员: admin / 123456")
        else:
            print(f"  ⏭️ 管理员已存在: admin")
        
        # 创建医生（从共享模型导入）
        created = 0
        for doc in DOCTORS:
            user = db.query(User).filter(User.username == doc["username"]).first()
            if not user:
                new_user = User(
                    username=doc["username"],
                    password=simple_hash(doc["password"]),
                    name=doc["name"],
                    role=Role.DOCTOR,
                    department=doc["department"]
                )
                db.add(new_user)
                created += 1
                print(f"  ✅ 医生: {doc['username']} - {doc['name']} ({doc['department']})")
            else:
                print(f"  ⏭️ 医生已存在: {doc['username']} - {doc['name']}")
        
        db.commit()
        
        # 显示最终用户列表
        print("\n" + "=" * 50)
        print("最终用户列表:")
        all_users = db.query(User).all()
        for user in all_users:
            print(f"  {user.username} ({user.role.value}) - {user.name} - {user.department or '无'}")
        print("=" * 50)
        
        print(f"\n📊 统计: 新增医生 {created} 个")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_users()