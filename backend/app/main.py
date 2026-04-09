from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import api
from app.database import init_db, SessionLocal
from app.models import User, Role
from app.security import hash_password

app = FastAPI(title="Piano-PIR EMR Backend")

# CORS 设置 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时初始化数据库并创建管理员账号
@app.on_event("startup")
def startup_event():
    print("\n" + "="*50)
    print("正在初始化用户系统...")
    print("="*50)
    
    # 创建用户表
    init_db()
    print("✅ 用户表初始化完成")
    
    # 创建管理员和测试医生
    db = SessionLocal()
    try:
        # 检查并创建管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                password=hash_password("123456"),
                name="系统管理员",
                role=Role.ADMIN,
                department="系统管理部"
            )
            db.add(admin_user)
            db.commit()
            print("✅ 管理员账号创建成功: admin / 123456")
        else:
            print("✅ 管理员账号已存在: admin")
        
        # 检查并创建测试医生
        test_doctor = db.query(User).filter(User.username == "test_doctor").first()
        if not test_doctor:
            doctor_user = User(
                username="test_doctor",
                password=hash_password("123456"),
                name="测试医生",
                role=Role.DOCTOR,
                department="内科"
            )
            db.add(doctor_user)
            db.commit()
            print("✅ 测试医生账号创建成功: test_doctor / 123456")
        
        # 显示所有用户
        users = db.query(User).all()
        print(f"\n📊 当前系统用户 ({len(users)}人):")
        for user in users:
            print(f"   - {user.username} ({user.role.value}) - {user.name}")
            
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
    finally:
        db.close()
    
    print("="*50 + "\n")

    # 加载历史增量数据到 PIR 引擎
    import numpy as np
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    NEW_RECORDS_PATH = os.path.join(BASE_DIR, 'storage', 'new_records.npy')
    
    # 获取 server 对象（需要在 api.py 中导入）
    from app.api import server
    
    if server and os.path.exists(NEW_RECORDS_PATH):
        try:
            incremental_matrix = np.load(NEW_RECORDS_PATH)
            count = 0
            for row in incremental_matrix:
                server.add_record(row.tobytes())
                count += 1
            print(f"✅ 成功恢复 {count} 条历史增量记录到 PIR 引擎")
        except Exception as e:
            print(f"❌ 恢复增量记录失败: {e}")

# 注册路由（所有接口都有 /api 前缀）
app.include_router(api.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Piano-PIR EMR Backend",
        "status": "running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)