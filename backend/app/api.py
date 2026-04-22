from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordBearer
import numpy as np
import json
import os
import requests
import time

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import Response
from fastapi import Request
from pydantic import BaseModel

from .database import get_db
from .models import User, Role
from .security import hash_password, verify_password, create_token, SECRET_KEY, ALGORITHM
from pydantic import BaseModel
from typing import Optional
from datetime import date

import sqlite3
import os
import json
from datetime import datetime, timedelta
import random
# ======================
# 定义 BASE_DIR
# ======================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 导入 PIR 核心
from core.piano_core import PianoServer

router = APIRouter()

# 加载环境变量
load_dotenv()

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")

# ======================
# 初始化 PIR 数据
# ======================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
NPY_PATH = os.path.join(BASE_DIR, 'storage', 'db.npy')
META_PATH = os.path.join(BASE_DIR, 'storage', 'metadata.json')

# 检查 PIR 数据文件是否存在
if os.path.exists(NPY_PATH) and os.path.exists(META_PATH):
    try:
        db_matrix = np.load(NPY_PATH)
        with open(META_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        server = PianoServer([row.tobytes() for row in db_matrix])
        BLOCK_SIZE = db_matrix.shape[1]
        DB_SIZE = db_matrix.shape[0]
        print(f"✅ PIR 数据加载成功: {DB_SIZE} 条记录")
    except Exception as e:
        print(f"⚠️ PIR 数据加载失败: {e}")
        db_matrix = None
        server = None
        BLOCK_SIZE = 0
        DB_SIZE = 0
else:
    print(f"⚠️ PIR 数据文件不存在，请先运行数据生成脚本")
    db_matrix = None
    server = None
    BLOCK_SIZE = 0
    DB_SIZE = 0


# 加载预处理表
PIANO_TABLES_PATH = os.path.join(BASE_DIR, 'storage', 'piano_tables.json')
piano_tables = None
if os.path.exists(PIANO_TABLES_PATH):
    with open(PIANO_TABLES_PATH, 'r') as f:
        piano_tables = json.load(f)
    print(f"✅ 加载 PIANO 预处理表: M1={piano_tables['params']['M1']}, M2={piano_tables['params']['M2']}")

class AIChatRequest(BaseModel):
    messages: list
    model: str = "deepseek"  # deepseek 或 doubao


class AIAssistant:
    """AI 助手类，支持豆包和 DeepSeek"""
    
    def __init__(self):
        # 豆包配置
        self.doubao_api_key = "91be1b79-0621-44a1-a725-a59462602582"
        self.doubao_base_url = "https://ark.cn-beijing.volces.com/api/v3/"
        self.doubao_model = "doubao-seed-1-6-250615"
        
        # DeepSeek 配置
        self.deepseek_api_key = "sk-edmctfrdmjllptnrkqyqlwhunenwdhaqgzcfxzkkcvadvesp"
        self.deepseek_base_url = "https://api.siliconflow.cn/v1"
        self.deepseek_model = "deepseek-ai/DeepSeek-V3"
    
    def call_doubao(self, messages):
        """调用豆包 API"""
        headers = {
            "Authorization": f"Bearer {self.doubao_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.doubao_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        try:
            response = requests.post(
                f"{self.doubao_base_url}chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"豆包API错误: {response.status_code}")
                return None
        except Exception as e:
            print(f"豆包调用失败: {e}")
            return None
    
    def call_deepseek(self, messages):
        """调用 DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.deepseek_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        try:
            response = requests.post(
                f"{self.deepseek_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"DeepSeek API错误: {response.status_code}")
                return None
        except Exception as e:
            print(f"DeepSeek调用失败: {e}")
            return None

   

class AIDiagnoseRequest(BaseModel):
    messages: list
    model: str = "doubao"  # doubao 或 deepseek

# ======================
# 请求/响应模型
# ======================

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    department: str

class LoginResponse(BaseModel):
    token: str
    username: str
    name: str
    role: str
    department: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    role: str
    department: Optional[str] = None


# OAuth2 配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", auto_error=False)

# ======================
# 辅助函数
# ======================

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """从 token 获取当前用户"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user

def get_current_user_required(current_user: User = Depends(get_current_user)):
    """要求必须登录"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

# ======================
# 公开接口（无需登录）
# ======================

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    print(f"[登录] 尝试: {request.username}")
    
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user:
        print(f"[登录失败] 用户不存在: {request.username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if not verify_password(request.password, user.password):
        print(f"[登录失败] 密码错误: {request.username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    token = create_token({
        "sub": user.username,
        "role": user.role.value,
        "name": user.name
    })
    
    print(f"[登录成功] {user.username} ({user.role.value})")
    
    return LoginResponse(
        token=token,
        username=user.username,
        name=user.name,
        role=user.role.value,
        department=user.department
    )

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """医生自助注册"""
    print(f"[注册] 尝试: {request.username}")
    
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        print(f"[注册失败] 用户名已存在: {request.username}")
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少6位")
    
    try:
        new_user = User(
            username=request.username,
            password=hash_password(request.password),
            name=request.name,
            role=Role.DOCTOR,
            department=request.department
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"[注册成功] {request.username} (医生, {request.department})")
        
        return {
            "success": True,
            "message": "注册成功，请登录",
            "username": request.username,
            "name": request.name
        }
        
    except Exception as e:
        db.rollback()
        print(f"[注册失败] 数据库错误: {e}")
        raise HTTPException(status_code=500, detail="注册失败，请稍后重试")

# ======================
# 需要登录的接口
# ======================

@router.get("/user/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user_required)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        name=current_user.name,
        role=current_user.role.value,
        department=current_user.department
    )

#创建医生
@router.post("/admin/create-user")
def admin_create_user(
    request: RegisterRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """管理员创建用户"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="无权限")
    
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    new_user = User(
        username=request.username,
        password=hash_password(request.password),
        name=request.name,
        role=Role.DOCTOR,
        department=request.department,
        join_date=date.today()
    )
    
    db.add(new_user)
    db.commit()
    
    return {"message": f"用户 {request.username} 创建成功"}

# ======================
# PIR 查询接口（需要登录）
# ======================

@router.get("/meta")
def get_meta(current_user: User = Depends(get_current_user_required)):
    """获取数据库元数据"""
    if db_matrix is None:
        raise HTTPException(status_code=503, detail="数据库未初始化")
    return {
        "db_size": DB_SIZE,
        "block_size": BLOCK_SIZE,
        "records_count": len(metadata) if metadata else 0
    }

@router.get("/hint")
def get_hint(sample_size: int = 10, current_user: User = Depends(get_current_user_required)):
    """获取样本数据提示"""
    if db_matrix is None:
        raise HTTPException(status_code=503, detail="数据库未初始化")
    sample_size = min(sample_size, DB_SIZE)
    indices = np.random.choice(DB_SIZE, sample_size, replace=False)
    hints = {str(i): db_matrix[i].tolist() for i in indices}
    return hints


@router.post("/query")
async def post_query(
    request: Request,
    current_user: User = Depends(get_current_user_required)
):
    """
    执行 PIR 查询
    接收二进制数据作为 query seed
    """
    if server is None:
        raise HTTPException(status_code=503, detail="PIR服务未初始化")
    
    try:
        # 从请求体中读取二进制数据
        query_seed = await request.body()
        
        if not query_seed:
            raise HTTPException(status_code=400, detail="空的查询数据")
        
        print(f"[API] 收到查询，seed 大小: {len(query_seed)} bytes")
        
        # 调用 PianoServer 处理查询
        result = server.process_query(query_seed)
        
        # 返回二进制结果
        return Response(content=result, media_type="application/octet-stream")
        
    except Exception as e:
        print(f"[API] PIR查询错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# ======================
# 医生专用接口
# ======================

# ============ 医生仪表盘数据 ============
@router.get("/doctor/dashboard")
def doctor_dashboard(current_user: User = Depends(get_current_user_required)):
    """医生仪表盘数据"""
    if current_user.role != Role.DOCTOR and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="仅医生可访问")
    
    return {
        "total_records": 1240,
        "today_new": 32,
        "pending_audit": 12,
        "pass_rate": "96.2%",
        "archive_rate": "91.8%"
    }

# ============ 总体统计（管理员） ============
# @router.get("/stats/overall")
# def get_overall_stats(current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)):
#     """获取总体统计（仅管理员）"""
#     if current_user.role != Role.ADMIN:
#         raise HTTPException(status_code=403, detail="无权限")
    
#     import sqlite3
#     import os
#     from datetime import datetime, timedelta
    
#     BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#     DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
    
#     today = datetime.now().strftime('%Y-%m-%d')
#     month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
#     # 总病历数
#     cursor.execute("SELECT COUNT(*) FROM records")
#     total_records = cursor.fetchone()[0]
    
#     # 今日新增
#     cursor.execute("SELECT COUNT(*) FROM records WHERE admission_date = ?", (today,))
#     today_new = cursor.fetchone()[0]
    
#     # 本月新增
#     cursor.execute("SELECT COUNT(*) FROM records WHERE admission_date >= ?", (month_ago,))
#     month_new = cursor.fetchone()[0]
    
#     # 医生总数
#     cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'DOCTOR'")
#     doctor_count = cursor.fetchone()[0]
    
#     conn.close()
    
#     return {
#         "total_records": total_records,
#         "doctor_count": doctor_count,
#         "today_new": today_new,
#         "month_new": month_new
#     }
@router.get("/stats/overall")
def get_overall_stats(current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)):
    """获取总体统计（仅管理员）"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="无权限")
    
    import sqlite3
    import os
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 计算时间范围
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 上月时间范围
    now = datetime.now()
    first_day_this_month = now.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    last_month_start = first_day_last_month.strftime('%Y-%m-%d')
    last_month_end = last_day_last_month.strftime('%Y-%m-%d')
    
    # 1. 总病历数
    cursor.execute("SELECT COUNT(*) FROM records")
    total_records = cursor.fetchone()[0]
    
    # 2. 今日新增
    cursor.execute("SELECT COUNT(*) FROM records WHERE admission_date = ?", (today,))
    today_new = cursor.fetchone()[0]
    
    # 3. 昨日新增
    cursor.execute("SELECT COUNT(*) FROM records WHERE admission_date = ?", (yesterday,))
    yesterday_new = cursor.fetchone()[0]
    
    # 4. 本月新增
    cursor.execute("SELECT COUNT(*) FROM records WHERE admission_date >= ?", (first_day_this_month.strftime('%Y-%m-%d'),))
    month_new = cursor.fetchone()[0]
    
    # 5. 上月新增
    cursor.execute("""
        SELECT COUNT(*) FROM records 
        WHERE admission_date >= ? AND admission_date <= ?
    """, (last_month_start, last_month_end))
    last_month_new = cursor.fetchone()[0]
    
    # 6. 上月总病历数（截止上月底）
    cursor.execute("SELECT COUNT(*) FROM records WHERE admission_date <= ?", (last_month_end,))
    last_month_total = cursor.fetchone()[0]
    
    # 7. 当前医生总数
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'DOCTOR'")
    doctor_count = cursor.fetchone()[0]
    
    # 8. 上月医生总数（入职日期 <= 上月底）
    cursor.execute("""
        SELECT COUNT(*) FROM users 
        WHERE role = 'DOCTOR' AND (join_date <= ? OR join_date IS NULL)
    """, (last_month_end,))
    last_month_doctor_count = cursor.fetchone()[0]
    
    conn.close()
    
    # 计算环比
    total_trend = ((total_records - last_month_total) / last_month_total * 100) if last_month_total > 0 else 0
    doctor_trend = ((doctor_count - last_month_doctor_count) / last_month_doctor_count * 100) if last_month_doctor_count > 0 else 0
    today_trend = ((today_new - yesterday_new) / yesterday_new * 100) if yesterday_new > 0 else (100 if today_new > 0 else 0)
    month_trend = ((month_new - last_month_new) / last_month_new * 100) if last_month_new > 0 else 0
    
    return {
        "total_records": total_records,
        "doctor_count": doctor_count,
        "today_new": today_new,
        "month_new": month_new,
        "total_trend": round(total_trend, 1),
        "doctor_trend": round(doctor_trend, 1),
        "today_trend": round(today_trend, 1),
        "month_trend": round(month_trend, 1)
    }

# ============ 科室详细统计 ============
@router.get("/stats/department")
def get_department_stats_detailed(current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)):
    """获取科室详细统计（包含今日和本月新增）"""
    import sqlite3
    import os
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    if current_user.role == Role.ADMIN:
        # 管理员：统计所有科室
        cursor.execute("""
            SELECT 
                department,
                COUNT(*) as total,
                SUM(CASE WHEN admission_date = ? THEN 1 ELSE 0 END) as today_count,
                SUM(CASE WHEN admission_date >= ? THEN 1 ELSE 0 END) as month_count
            FROM records 
            GROUP BY department
        """, (today, month_ago))
    else:
        # 医生：只统计自己科室
        cursor.execute("""
            SELECT 
                department,
                COUNT(*) as total,
                SUM(CASE WHEN admission_date = ? THEN 1 ELSE 0 END) as today_count,
                SUM(CASE WHEN admission_date >= ? THEN 1 ELSE 0 END) as month_count
            FROM records 
            WHERE department = ?
            GROUP BY department
        """, (today, month_ago, current_user.department))
    
    results = cursor.fetchall()
    conn.close()
    
    stats = []
    for row in results:
        stats.append({
            "department": row[0],
            "total": row[1],
            "today": row[2] or 0,
            "month": row[3] or 0
        })
    
    # 如果医生科室没有数据，返回默认值
    if not stats and current_user.role != Role.ADMIN:
        stats.append({
            "department": current_user.department,
            "total": 0,
            "today": 0,
            "month": 0
        })
    
    return {
        "stats": stats,
        "user_role": current_user.role.value,
        "user_department": current_user.department
    }

# ============ 用户列表查询（管理员） ============
@router.get("/users/list")
def get_users_list(current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)):
    """获取所有医生列表（仅管理员）"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="无权限")
    
    import sqlite3
    import os
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询所有字段
    cursor.execute("""
        SELECT id, username, name, department, role, 
               gender, title, phone, email, join_date, bio
        FROM users 
        WHERE role = 'DOCTOR'
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    users = []
    for row in rows:
        users.append({
            "id": row[0],
            "username": row[1],
            "name": row[2],
            "department": row[3],
            "role": row[4],
            "gender": row[5] or '',
            "title": row[6] or '主治医师',
            "phone": row[7] or '',
            "email": row[8] or '',
            "join_date": row[9] or '',
            "bio": row[10] or ''
        })
    
    return {
        "total": len(users),
        "users": users
    }

# ============ 删除医生账号（管理员） ============
@router.delete("/admin/delete-user/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """删除医生账号（仅管理员）"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="无权限")
    
    user = db.query(User).filter(User.id == user_id, User.role == Role.DOCTOR).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    
    return {"message": "删除成功"}

# ============ 重置医生密码（管理员） ============
@router.post("/admin/reset-password/{user_id}")
def reset_password(
    user_id: int,
    password_data: dict,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """重置医生密码（仅管理员）"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="无权限")
    
    user = db.query(User).filter(User.id == user_id, User.role == Role.DOCTOR).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    new_password = password_data.get("password")
    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="密码至少6位")
    
    user.password = hash_password(new_password)
    db.commit()
    
    return {"message": "密码重置成功"}

# ============ 检查用户名是否存在 ============
@router.get("/check-username/{username}")
def check_username(username: str, db: Session = Depends(get_db)):
    """检查用户名是否已存在（用于前端实时验证）"""
    user = db.query(User).filter(User.username == username).first()
    return {"exists": user is not None, "available": user is None}

# 添加病历请求模型
class CreateRecordRequest(BaseModel):
    name: str
    gender: str  # 'M' 或 'F'
    age: int
    id_card: str
    department: str
    doctor_id: str
    admission_date: str
    diagnosis: str
    treatments: list = []
    prescriptions: list = []
    lab_results: dict = {}
    imaging_reports: str = ""
    notes: str = ""

# ============ 创建新病历 ============
@router.post("/records/create")
def create_record(
    req: CreateRecordRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """创建新病历 - 同步重建 PIR 数据"""
    import sqlite3
    import json
    import os
    import random
    import subprocess
    import sys
    from datetime import datetime, timedelta
    from core.piano_preprocess import PianoPreprocess
    from core.piano_core import PianoServer

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    NPY_PATH = os.path.join(BASE_DIR, 'storage', 'db.npy')
    TABLE_PATH = os.path.join(BASE_DIR, 'storage', 'piano_tables.json')

    # 1. 插入新病历
    record_id = f"MR-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
    adm_date = datetime.strptime(req.admission_date, "%Y-%m-%d")
    disc_date = adm_date + timedelta(days=random.randint(0, 10))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ⭐ 修改：使用前端传递的 doctor_id，不再随机选择
    doctor_id = req.doctor_id
    cursor.execute("SELECT name FROM users WHERE username = ?", (doctor_id,))
    row = cursor.fetchone()
    if row:
        doctor_name = row[0]
    else:
        # 降级处理：如果找不到，按科室随机选一个
        cursor.execute(
            "SELECT username, name FROM users WHERE role = 'DOCTOR' AND department = ?",
            (req.department,)
        )
        doctors = cursor.fetchall()
        doctor_id, doctor_name = random.choice(doctors) if doctors else ("doc001", "张明")

    treatments_json = json.dumps(req.treatments, ensure_ascii=False)
    prescriptions_json = json.dumps(req.prescriptions, ensure_ascii=False)
    lab_results_json = json.dumps(req.lab_results, ensure_ascii=False)

    cursor.execute('''
        INSERT INTO records (
            record_id, id_card, name, gender, age,
            admission_date, discharge_date, diagnosis,
            treatments, prescriptions, lab_results,
            imaging_reports, doctor_id, doctor_name, department, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        record_id, req.id_card, req.name, req.gender, req.age,
        req.admission_date, disc_date.strftime("%Y-%m-%d"), req.diagnosis,
        treatments_json, prescriptions_json, lab_results_json,
        req.imaging_reports, doctor_id, doctor_name, req.department, req.notes
    ))
    conn.commit()
    cursor.execute("SELECT last_insert_rowid()")
    rowid = cursor.fetchone()[0]
    conn.close()

    # 2. 同步重建 PIR 数据（确保新病历立即可查）
    print("🔄 同步重建 PIR 数据...")
    
    # 重建 db.npy
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM records ORDER BY id ASC")
    rows = cursor.fetchall()
    data_bytes = []
    for row in rows:
        record = {
            "id": row[0],
            "record_id": row[1],
            "id_card": row[2],
            "name": row[3],
            "gender": row[4],
            "age": row[5],
            "admission_date": row[6],
            "discharge_date": row[7],
            "diagnosis": row[8],
            "treatments": json.loads(row[9]),
            "prescriptions": json.loads(row[10]),
            "lab_results": json.loads(row[11]),
            "imaging_reports": row[12],
            "doctor_id": row[13],
            "doctor_name": row[14],
            "department": row[15],
            "notes": row[16]
        }
        raw = json.dumps(record, ensure_ascii=False).encode('utf-8')
        if len(raw) < 8192:
            raw += b'\x00' * (8192 - len(raw))
        else:
            raw = raw[:8192]
        data_bytes.append(np.frombuffer(raw, dtype=np.uint8))
    db_matrix = np.array(data_bytes)
    np.save(NPY_PATH, db_matrix)
    conn.close()

    # 重建预处理表
    pre = PianoPreprocess(NPY_PATH, NPY_PATH, None)
    pre.load_db()
    tables = pre.save_tables(TABLE_PATH)

    # 更新全局变量
    global server, piano_tables, DB_SIZE
    server = PianoServer([row.tobytes() for row in db_matrix])
    piano_tables = tables
    DB_SIZE = len(db_matrix)

    print(f"✅ PIR 数据重建完成，总记录数: {DB_SIZE}")

    return {
        "success": True,
        "message": "病历创建成功，PIR 数据已更新",
        "record_id": record_id,
        "index": rowid - 1,
        "doctor": {
            "id": doctor_id,
            "name": doctor_name
        }
    }

# ============ 医生列表查询 ============
@router.get("/doctors/list")
def get_doctors_list(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
    department: str = None
):
    """获取医生列表"""
    import sqlite3
    import os
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"【接口收到的科室】: '{department}'")

    if department:
        cursor.execute(
            "SELECT username, name, department FROM users WHERE role = 'DOCTOR' AND department LIKE ?",
            (f"%{department}%",)  # 加%包裹，模糊匹配，绕过编码/隐藏字符问题
        )
    else:
        cursor.execute("SELECT username, name, department FROM users WHERE role = 'DOCTOR'")
    
    doctors = [{"id": row[0], "name": row[1], "department": row[2]} for row in cursor.fetchall()]
    print(f"【查询到的医生数量】: {len(doctors)}")
    conn.close()
    
    return {"doctors": doctors}

#     current_user: User = Depends(get_current_user_required),
#     limit: int = 100,
#     offset: int = 0,
#     department: str = None,
#     doctor_name: str = None, 
#     search: str = None
# ):
#     """获取病历列表（支持科室、医生、搜索筛选）"""
#     import sqlite3
#     import os
    
#     BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#     DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
    
#     conditions = []
#     params = []
    
#     # 权限控制
#     if current_user.role != Role.ADMIN:
#         conditions.append("department = ?")
#         params.append(current_user.department)
    
#     # 科室筛选（仅管理员）
#     if department and current_user.role == Role.ADMIN:
#         conditions.append("department = ?")
#         params.append(department)
    
#     # 医生筛选（新增）
#     if doctor_name:
#         conditions.append("doctor_name = ?")
#         params.append(doctor_name)
#         print(f"🔍 筛选医生: {doctor_name}")  # 添加日志
    
#     # 搜索筛选
#     if search and search.strip():
#         conditions.append("(record_id LIKE ? OR name LIKE ?)")
#         search_pattern = f"%{search.strip()}%"
#         params.append(search_pattern)
#         params.append(search_pattern)
    
#     where_clause = ""
#     if conditions:
#         where_clause = " WHERE " + " AND ".join(conditions)
    
#      # 打印最终查询（调试用）
#     print(f"📝 SQL: {where_clause}")
#     print(f"📝 参数: {params}")
    
#     # 总数
#     cursor.execute(f"SELECT COUNT(*) FROM records{where_clause}", params)
#     total = cursor.fetchone()[0]
    
#     # 查询数据
#     query = f"""
#         SELECT id, record_id, name, gender, age, department, 
#                admission_date, diagnosis, doctor_id, doctor_name
#         FROM records{where_clause}
#         ORDER BY admission_date DESC, record_id DESC
#         LIMIT ? OFFSET ?
#     """
#     cursor.execute(query, params + [limit, offset])
#     rows = cursor.fetchall()
    
#     records = []
#     for row in rows:
#         records.append({
#             "index": row[0] - 1,
#             "record_id": row[1],
#             "name": row[2],
#             "gender": row[3],
#             "age": row[4],
#             "department": row[5],
#             "admission_date": row[6],
#             "diagnosis": row[7],
#             "doctor_id": row[8],
#             "doctor_name": row[9]
#         })
    
#     conn.close()
    
#     return {
#         "records": records,
#         "total": total,
#         "limit": limit,
#         "offset": offset
#     }
# ============ 病历列表查询 ============
@router.get("/records/list")
def get_records_list(
    current_user: User = Depends(get_current_user_required),
    limit: int = 100,
    offset: int = 0,
    department: str = None,
    doctor_name: str = None,
    admission_date: str = None,  # ← 添加这个参数
    search: str = None
):
    """获取病历列表（支持科室、医生、入院日期、搜索筛选）"""
    import sqlite3
    import os
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    # 权限控制
    if current_user.role != Role.ADMIN:
        conditions.append("department = ?")
        params.append(current_user.department)
    
    # 科室筛选（仅管理员）
    if department and current_user.role == Role.ADMIN:
        conditions.append("department = ?")
        params.append(department)
    
    # 医生筛选
    if doctor_name:
        conditions.append("doctor_name = ?")
        params.append(doctor_name)
        print(f"🔍 筛选医生: {doctor_name}")
    
    # ⭐ 入院日期筛选
    if admission_date:
        conditions.append("admission_date = ?")
        params.append(admission_date)
        print(f"📅 筛选日期: {admission_date}")
    
    # 搜索筛选
    if search and search.strip():
        conditions.append("(record_id LIKE ? OR name LIKE ?)")
        search_pattern = f"%{search.strip()}%"
        params.append(search_pattern)
        params.append(search_pattern)
    
    where_clause = ""
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)
    
    print(f"📝 SQL: {where_clause}")
    print(f"📝 参数: {params}")
    
    # 总数
    cursor.execute(f"SELECT COUNT(*) FROM records{where_clause}", params)
    total = cursor.fetchone()[0]
    
    # 查询数据
    query = f"""
        SELECT id, record_id, name, gender, age, department, 
               admission_date, discharge_date, diagnosis, doctor_id, doctor_name
        FROM records{where_clause}
        ORDER BY admission_date DESC, record_id DESC
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, params + [limit, offset])
    rows = cursor.fetchall()
    
    records = []
    for row in rows:
        records.append({
            "index": row[0] - 1,
            "record_id": row[1],
            "name": row[2],
            "gender": row[3],
            "age": row[4],
            "department": row[5],
            "admission_date": row[6],
            "discharge_date": row[7], 
            "diagnosis": row[8],
            "doctor_id": row[9],
            "doctor_name": row[10]
        })
    
    conn.close()
    
    return {
        "records": records,
        "total": total,
        "limit": limit,
        "offset": offset
    }

# ============ 医生接诊统计排行 ============
@router.get("/stats/doctors")
def get_doctor_stats(
    current_user: User = Depends(get_current_user_required),
    department: str = None
):
    """获取医生接诊数量统计排行"""
    import sqlite3
    import os
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 权限控制：非管理员只能看自己科室
    if current_user.role != Role.ADMIN:
        dept_filter = current_user.department
    else:
        dept_filter = department if department else None
    
    # 查询医生接诊数量
    if dept_filter:
        cursor.execute("""
            SELECT 
                doctor_name,
                doctor_id,
                department,
                COUNT(*) as patient_count
            FROM records 
            WHERE department = ?
            GROUP BY doctor_name, doctor_id, department
            ORDER BY patient_count DESC
        """, (dept_filter,))
    else:
        cursor.execute("""
            SELECT 
                doctor_name,
                doctor_id,
                department,
                COUNT(*) as patient_count
            FROM records 
            GROUP BY doctor_name, doctor_id, department
            ORDER BY patient_count DESC
        """)
    
    results = cursor.fetchall()
    conn.close()
    
    doctors = []
    for row in results:
        doctors.append({
            "doctor_name": row[0],
            "doctor_id": row[1],
            "department": row[2],
            "patient_count": row[3]
        })
    
    return {
        "success": True,
        "doctors": doctors,
        "total": len(doctors)
    }

# ============ PIR 总记录数查询 ============
@router.get("/stats/total")
def get_total_stats(current_user: User = Depends(get_current_user_required)):
    """获取总记录数（基础+增量）"""
    if server:
        return {"total_records": server.get_current_total_count()}
    return {"total_records": 0}

# ============ PIR 预处理表获取 ============
@router.get("/piano/tables")
def get_piano_tables(current_user: User = Depends(get_current_user_required)):
    import json
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    PIANO_TABLES_PATH = os.path.join(BASE_DIR, 'storage', 'piano_tables.json')
    if os.path.exists(PIANO_TABLES_PATH):
        with open(PIANO_TABLES_PATH, 'r') as f:
            return json.load(f)
    return {"primary_table": [], "backup_table": {}, "replacement_entries": {}, "params": {}}

# ============ 科室月度统计 ============
@router.get("/stats/department/month")
def get_department_stats_month(
    current_user: User = Depends(get_current_user_required),
    department: str = None
):
    """获取上月科室统计"""
    import sqlite3
    import os
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 计算上月时间范围
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    
    start = first_day_last_month.strftime("%Y-%m-%d")
    end = last_day_last_month.strftime("%Y-%m-%d")
    
    if current_user.role != Role.ADMIN:
        dept_filter = current_user.department
    else:
        dept_filter = department
    
    if dept_filter:
        # ⭐ 修改：total 统计上月底之前的全部病历（admission_date <= 上月底）
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM records WHERE department = ? AND admission_date <= ?) as total,
                SUM(CASE WHEN admission_date >= ? AND admission_date <= ? THEN 1 ELSE 0 END) as month_count,
                SUM(CASE WHEN admission_date = ? THEN 1 ELSE 0 END) as today_count
            FROM records 
            WHERE department = ?
        """, (dept_filter, end, start, end, today.strftime("%Y-%m-%d"), dept_filter))
    else:
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM records WHERE admission_date <= ?) as total,
                SUM(CASE WHEN admission_date >= ? AND admission_date <= ? THEN 1 ELSE 0 END) as month_count,
                SUM(CASE WHEN admission_date = ? THEN 1 ELSE 0 END) as today_count
            FROM records
        """, (end, start, end, today.strftime("%Y-%m-%d")))
    
    row = cursor.fetchone()
    conn.close()
    
    return {
        "stats": [{
            "total": row[0] or 0,
            "month": row[1] or 0,
            "today": row[2] or 0
        }]
    }

# ============ 科室昨日统计 ============
@router.get("/stats/department/yesterday")
def get_department_stats_yesterday(
    current_user: User = Depends(get_current_user_required),
    department: str = None
):
    """获取昨日科室统计"""
    import sqlite3
    import os
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 权限控制
    if current_user.role != Role.ADMIN:
        dept_filter = current_user.department
    else:
        dept_filter = department
    
    if dept_filter:
        cursor.execute("""
            SELECT COUNT(*) FROM records 
            WHERE department = ? AND admission_date = ?
        """, (dept_filter, yesterday))
    else:
        cursor.execute("""
            SELECT COUNT(*) FROM records 
            WHERE admission_date = ?
        """, (yesterday,))
    
    count = cursor.fetchone()[0] or 0
    conn.close()
    
    return {"stats": [{"today": count}]}


# ============ 上月总体统计 ============
@router.get("/stats/overall/lastmonth")
def get_overall_stats_lastmonth(current_user: User = Depends(get_current_user_required)):
    """获取上月总体统计（用于同比）"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="无权限")
    
    import sqlite3
    import os
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    
    start = first_day_last_month.strftime("%Y-%m-%d")
    end = last_day_last_month.strftime("%Y-%m-%d")
    
    # 上月总病历数
    cursor.execute("SELECT COUNT(*) FROM records WHERE admission_date <= ?", (end,))
    total_records = cursor.fetchone()[0]
    
    # 上月医生总数
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor'")
    doctor_count = cursor.fetchone()[0]
    
    # 上月新增病历数
    cursor.execute("SELECT COUNT(*) FROM records WHERE admission_date BETWEEN ? AND ?", (start, end))
    month_new = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_records": total_records,
        "doctor_count": doctor_count,
        "month_new": month_new,
        "today_new": 0
    }

# ============ 昨日总体统计 ============
@router.get("/stats/overall/yesterday")
def get_overall_stats_yesterday(current_user: User = Depends(get_current_user_required)):
    """获取昨日总体统计（用于今日对比）"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="无权限")
    
    import sqlite3
    import os
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    cursor.execute("SELECT COUNT(*) FROM records WHERE admission_date = ?", (yesterday,))
    today_new = cursor.fetchone()[0]
    
    conn.close()
    
    return {"today_new": today_new}

# ============ 病历趋势统计 ============
@router.get("/stats/trend")
def get_trend_stats(
    current_user: User = Depends(get_current_user_required),
    department: str = None,
    start_date: str = None,
    end_date: str = None,
    unit: str = "month"
):
    """获取病历趋势统计"""
    import sqlite3
    import os
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 权限控制
    if current_user.role != Role.ADMIN:
        dept_filter = current_user.department
    else:
        dept_filter = department
    
    # 解析日期范围
    start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now() - timedelta(days=180)
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
    
    # 根据单位生成分组格式
    if unit == "day":
        format_str = "%Y-%m-%d"
        step = timedelta(days=1)
    elif unit == "week":
        format_str = "%Y-%W"  # 年-周数
        step = timedelta(weeks=1)
    elif unit == "month":
        format_str = "%Y-%m"
        step = timedelta(days=30)
    else:  # year
        format_str = "%Y"
        step = timedelta(days=365)
    
    # 构建查询
    if dept_filter:
        cursor.execute("""
            SELECT admission_date, COUNT(*) 
            FROM records 
            WHERE department = ? AND admission_date BETWEEN ? AND ?
            GROUP BY admission_date
            ORDER BY admission_date
        """, (dept_filter, start_date, end_date))
    else:
        cursor.execute("""
            SELECT admission_date, COUNT(*) 
            FROM records 
            WHERE admission_date BETWEEN ? AND ?
            GROUP BY admission_date
            ORDER BY admission_date
        """, (start_date, end_date))
    
    rows = cursor.fetchall()
    conn.close()
    
    # 聚合数据
    from collections import defaultdict
    aggregated = defaultdict(int)
    
    for date_str, count in rows:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if unit == "week":
            key = date_obj.strftime("%Y-W%W")
        elif unit == "month":
            key = date_obj.strftime("%Y-%m")
        elif unit == "year":
            key = date_obj.strftime("%Y")
        else:
            key = date_str
        aggregated[key] += count
    
    # 生成完整的时间序列
    labels = []
    values = []
    current = start
    while current <= end:
        if unit == "day":
            key = current.strftime("%Y-%m-%d")
        elif unit == "week":
            key = current.strftime("%Y-W%W")
        elif unit == "month":
            key = current.strftime("%Y-%m")
        else:
            key = current.strftime("%Y")
        labels.append(key)
        values.append(aggregated.get(key, 0))
        current += step
    
    return {
        "labels": labels,
        "values": values,
        "unit": unit,
        "start_date": start_date,
        "end_date": end_date
    }

# ============ 各科室医生数量分布 ============
@router.get("/stats/doctor/distribution")
def get_doctor_distribution(current_user: User = Depends(get_current_user_required)):
    """获取各科室医生数量分布"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="无权限")
    
    import sqlite3
    import os
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT department, COUNT(*) as count 
        FROM users 
        WHERE role = 'DOCTOR' 
        GROUP BY department
        ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    return [{"department": row[0], "count": row[1]} for row in results]

# ============ 医生工作量排行(完整数据) ============
@router.get("/stats/doctor/workload")
def get_doctor_workload(
    current_user: User = Depends(get_current_user_required),
    start_date: str = None,
    end_date: str = None,
    department: str = None,
    limit: int = 1000
):
    import sqlite3
    import os
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 构建查询
    if start_date and end_date:
        # 有时间范围
        query = """
            SELECT doctor_name, doctor_id, department, COUNT(*) as count
            FROM records 
            WHERE admission_date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
    else:
        # 无时间范围，统计全部
        query = """
            SELECT doctor_name, doctor_id, department, COUNT(*) as count
            FROM records 
        """
        params = []
    
    # 科室筛选
    if department:
        query += " AND department = ?" if start_date and end_date else " WHERE department = ?"
        params.append(department)
    
    # 分组和排序
    query += " GROUP BY doctor_name, doctor_id, department ORDER BY count DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "name": row[0],
            "id": row[1],
            "department": row[2],
            "count": row[3]
        }
        for row in results
    ]

# ============ 科室同比变化 ============
@router.get("/stats/department/yoy")
def get_department_yoy(
    current_user: User = Depends(get_current_user_required),
    year: int = None
):
    """获取各科室病历同比变化（较去年同期）"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="无权限")
    
    import sqlite3
    import os
    from datetime import datetime
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if not year:
        year = datetime.now().year
    
    current_start = f"{year}-01-01"
    current_end = f"{year}-12-31"
    last_start = f"{year-1}-01-01"
    last_end = f"{year-1}-12-31"
    
    # 获取今年各科室数据
    cursor.execute("""
        SELECT department, COUNT(*) as count 
        FROM records 
        WHERE admission_date BETWEEN ? AND ?
        GROUP BY department
    """, (current_start, current_end))
    current_data = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 获取去年各科室数据
    cursor.execute("""
        SELECT department, COUNT(*) as count 
        FROM records 
        WHERE admission_date BETWEEN ? AND ?
        GROUP BY department
    """, (last_start, last_end))
    last_data = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 获取所有科室列表
    cursor.execute("SELECT DISTINCT department FROM records")
    departments = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    current_list = [{"department": dept, "count": current_data.get(dept, 0)} for dept in departments]
    last_year_counts = [last_data.get(dept, 0) for dept in departments]
    growth = {}
    for dept in departments:
        last = last_data.get(dept, 0)
        curr = current_data.get(dept, 0)
        if last == 0:
            growth[dept] = 100 if curr > 0 else 0
        else:
            growth[dept] = round((curr - last) / last * 100, 1)
    
    return {
        "departments": departments,
        "current": current_list,
        "last_year_counts": last_year_counts,
        "growth": growth
    }

# ============ 单个医生接诊趋势 ============
@router.get("/stats/doctor/trend")
def get_doctor_trend(
    current_user: User = Depends(get_current_user_required),
    doctor_name: str = None,
    months: int = 12
):
    """获取单个医生的接诊趋势"""
    import sqlite3
    import os
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months*30)
    
    cursor.execute("""
        SELECT strftime('%Y-%m', admission_date) as month, COUNT(*) as count
        FROM records
        WHERE doctor_name = ? AND admission_date BETWEEN ? AND ?
        GROUP BY month
        ORDER BY month
    """, (doctor_name, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
    
    results = cursor.fetchall()
    conn.close()
    
    months_list = []
    counts_list = []
    for row in results:
        months_list.append(row[0])
        counts_list.append(row[1])
    
    return {
        "months": months_list,
        "counts": counts_list
    }


@router.post("/ai/chat")
def ai_chat(
    req: AIChatRequest,
    current_user: User = Depends(get_current_user_required)
):
    """
    AI 对话接口
    支持 DeepSeek-R1 和豆包模型
    """
    ai = AIAssistant()
    
    # 系统提示词
    system_prompt = {
        "role": "system",
        "content": """你是一个专业的医疗问诊助手，名叫"仁爱医助"。你的职责是：
1. 根据患者描述的症状，给出初步的诊断建议
2. 建议必要的检查项目
3. 给出治疗和用药建议
4. 提醒注意事项

注意：
- 回答要专业、准确、简洁
- 不确定的情况建议进一步检查
- 所有建议仅供参考，最终诊断需由医生决定
- 回答请使用中文
"""
    }
    
    # 构建完整消息
    full_messages = [system_prompt] + req.messages
    
    # 调用 AI
    if req.model == "doubao":
        result = ai.call_doubao(full_messages)
    else:
        result = ai.call_deepseek(full_messages)
    
    if result:
        return {
            "success": True,
            "content": result,
            "model": req.model
        }
    else:
        raise HTTPException(status_code=500, detail="AI服务调用失败，请稍后重试")
 

# ============ 医生科室排名 ============
@router.get("/stats/doctor/rank")
def get_doctor_rank(
    current_user: User = Depends(get_current_user_required),
    doctor_name: str = None
):
    """获取医生在全院同科室中的接诊量排名"""
    import sqlite3
    import os
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 如果没有指定医生名称，使用当前登录用户
    if not doctor_name:
        doctor_name = current_user.name
    
    # 获取该医生的科室
    cursor.execute("""
        SELECT department FROM users 
        WHERE name = ? AND role = 'DOCTOR'
    """, (doctor_name,))
    dept_row = cursor.fetchone()
    
    if not dept_row:
        conn.close()
        return {"rank": 0, "total": 0}
    
    department = dept_row[0]
    
    # 统计该科室所有医生的接诊量
    cursor.execute("""
        SELECT doctor_name, COUNT(*) as count
        FROM records
        WHERE department = ?
        GROUP BY doctor_name
        ORDER BY count DESC
    """, (department,))
    
    results = cursor.fetchall()
    conn.close()
    
    # 计算排名
    rank = 0
    total = len(results)
    
    for i, row in enumerate(results):
        if row[0] == doctor_name:
            rank = i + 1
            break
    
    return {
        "rank": rank,
        "total": total,
        "department": department
    }


# ============ 获取个人资料 ============
@router.get("/user/profile")
def get_user_profile(
    current_user: User = Depends(get_current_user_required)
):
    """获取当前登录用户的个人资料"""
    import sqlite3
    import os
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, department, gender, birth_date, title, phone, email, join_date, bio, avatar
        FROM users 
        WHERE username = ?
    """, (current_user.username,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "name": row[0],
            "department": row[1],
            "gender": row[2] or '男',
            "birth_date": row[3],
            "title": row[4] or '主治医师',
            "phone": row[5] or '',
            "email": row[6] or '',
            "join_date": row[7],
            "bio": row[8] or '',
            "avatar": row[9] or ''
        }
    return {"error": "用户不存在"}


# ============ 更新个人资料 ============
@router.post("/user/profile")
def update_user_profile(
    profile: dict,
    current_user: User = Depends(get_current_user_required)
):
    """更新当前登录用户的个人资料"""
    import sqlite3
    import os
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users 
        SET gender = ?, birth_date = ?, title = ?, phone = ?, 
            email = ?, join_date = ?, bio = ?, avatar = ?
        WHERE username = ?
    """, (
        profile.get('gender', '男'),
        profile.get('birth_date'),
        profile.get('title', '主治医师'),
        profile.get('phone', ''),
        profile.get('email', ''),
        profile.get('join_date'),
        profile.get('bio', ''),
        profile.get('avatar', ''),
        current_user.username
    ))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "资料更新成功"}

# ============ 疾病排行榜 ============
@router.get("/stats/disease-ranking")
def get_disease_ranking(
    current_user: User = Depends(get_current_user_required),
    limit: int = 10,
    department: str = None,  # 新增科室筛选
    start_date: str = None,
    end_date: str = None
):
    """获取疾病排行榜 TOP N"""
    import sqlite3
    import os
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 权限控制：非管理员只能看自己科室
    if current_user.role != Role.ADMIN:
        dept_filter = current_user.department
    else:
        dept_filter = department
    
    # 构建查询条件
    conditions = []
    params = []
    
    if dept_filter:
        conditions.append("department = ?")
        params.append(dept_filter)
    
    if start_date and end_date:
        conditions.append("admission_date BETWEEN ? AND ?")
        params.extend([start_date, end_date])
    
    where_clause = ""
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)
    
    query = f"""
        SELECT diagnosis, COUNT(*) as count
        FROM records
        {where_clause}
        GROUP BY diagnosis
        ORDER BY count DESC
        LIMIT ?
    """
    params.append(limit)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return [
        {"name": row[0], "count": row[1]}
        for row in results
    ]


# ============ 药品排行榜 ============
@router.get("/stats/drug-ranking")
def get_drug_ranking(
    current_user: User = Depends(get_current_user_required),
    limit: int = 10,
    department: str = None,  # 新增科室筛选
    start_date: str = None,
    end_date: str = None
):
    """获取药品使用排行榜 TOP N"""
    import sqlite3
    import os
    import json
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 权限控制：非管理员只能看自己科室
    if current_user.role != Role.ADMIN:
        dept_filter = current_user.department
    else:
        dept_filter = department
    
    # 构建查询条件
    conditions = []
    params = []
    
    if dept_filter:
        conditions.append("department = ?")
        params.append(dept_filter)
    
    if start_date and end_date:
        conditions.append("admission_date BETWEEN ? AND ?")
        params.extend([start_date, end_date])
    
    where_clause = ""
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)
    
    query = f"""
        SELECT prescriptions
        FROM records
        {where_clause}
    """
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # 统计药品使用次数
    drug_count = {}
    for row in rows:
        try:
            prescriptions = json.loads(row[0])
            for p in prescriptions:
                if isinstance(p, dict):
                    drug_name = p.get('drug', '')
                    if drug_name:
                        drug_count[drug_name] = drug_count.get(drug_name, 0) + 1
                elif isinstance(p, str):
                    if p:
                        drug_count[p] = drug_count.get(p, 0) + 1
        except:
            continue
    
    sorted_drugs = sorted(drug_count.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    return [
        {"name": name, "count": count}
        for name, count in sorted_drugs
    ]

# ============ 获取上月科室医生数 ============
@router.get("/stats/department/doctor-history")
def get_department_doctor_history(
    current_user: User = Depends(get_current_user_required),
    department: str = None
):
    """获取指定科室上月末的医生数量（用于环比计算）"""
    import sqlite3
    import os
    from datetime import datetime, timedelta
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 计算上个月的最后一天
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    last_month_end = last_day_last_month.strftime("%Y-%m-%d")
    
    # 权限控制
    if current_user.role != Role.ADMIN:
        dept_filter = current_user.department
    else:
        dept_filter = department
    
    if dept_filter:
        # ⭐ 使用 join_date 统计上月末已入职的医生
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE role = 'DOCTOR' 
            AND department = ?
            AND (join_date <= ? OR join_date IS NULL)
        """, (dept_filter, last_month_end))
    else:
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE role = 'DOCTOR'
            AND (join_date <= ? OR join_date IS NULL)
        """, (last_month_end,))
    
    count = cursor.fetchone()[0] or 0
    conn.close()
    
    return {"doctor_count": count, "month": last_day_last_month.strftime("%Y-%m")}

# ============ AI 趋势分析 ==========
@router.post("/ai/analyze-trend")
async def analyze_trend(
    request: Request,
    current_user: User = Depends(get_current_user_required)
):
    """AI 分析病历趋势数据"""
    import requests
    import asyncio
    
    body = await request.json()
    labels = body.get('labels', [])
    values = body.get('values', [])
    unit = body.get('unit', 'day')
    department = body.get('department', '全院')
    
    if not labels or not values:
        return {"analysis": "数据不足，无法分析", "success": False}
    
    # 计算基础统计...
    total = sum(values)
    avg = total / len(values)
    max_val = max(values)
    start_val = values[0]
    end_val = values[-1]
    change = ((end_val - start_val) / start_val * 100) if start_val > 0 else 0
    
    prompt = f"""请分析以下医院{department}的病历接诊数据趋势：

数据概览：
- 时间范围：{labels[0]} 至 {labels[-1]}（{unit}为单位）
- 总接诊量：{total} 例
- 日均接诊：{avg:.1f} 例
- 最高接诊量：{max_val} 例
- 期初接诊量：{start_val} 例
- 期末接诊量：{end_val} 例
- 整体变化：{change:+.1f}%

请用简洁专业的语言回答（100字以内），包括：整体趋势判断、近期变化、管理建议。"""

    try:
        # 使用您已有的豆包配置
        doubao_api_key = "91be1b79-0621-44a1-a725-a59462602582"
        doubao_model = "doubao-seed-1-6-250615"
        
        # 在线程池中运行同步请求
        def call_doubao():
            headers = {
                "Authorization": f"Bearer {doubao_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": doubao_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500
            }
            response = requests.post(
                "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return None
        
        loop = asyncio.get_event_loop()
        analysis = await loop.run_in_executor(None, call_doubao)
        
        if analysis:
            return {"analysis": analysis, "success": True}
        else:
            return {"analysis": "AI服务暂时不可用，请稍后再试", "success": False}
            
    except Exception as e:
        print(f"调用AI分析失败: {e}")
        return {"analysis": "AI服务暂时不可用，请稍后再试", "success": False}

# ============ 患者画像分析 ==========
@router.get("/stats/patient-profile")
def get_patient_profile(
    current_user: User = Depends(get_current_user_required),
    department: str = None
):
    """获取患者画像（年龄分布、性别分布）"""
    import sqlite3
    import os
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 权限控制
    if current_user.role != Role.ADMIN:
        dept_filter = current_user.department
    else:
        dept_filter = department
    
    if dept_filter:
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN age < 18 THEN 1 ELSE 0 END) as age_0_18,
                SUM(CASE WHEN age BETWEEN 18 AND 35 THEN 1 ELSE 0 END) as age_18_35,
                SUM(CASE WHEN age BETWEEN 36 AND 55 THEN 1 ELSE 0 END) as age_36_55,
                SUM(CASE WHEN age > 55 THEN 1 ELSE 0 END) as age_55_plus,
                SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) as male_count,
                SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) as female_count,
                COUNT(*) as total
            FROM records
            WHERE department = ?
        """, (dept_filter,))
    else:
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN age < 18 THEN 1 ELSE 0 END) as age_0_18,
                SUM(CASE WHEN age BETWEEN 18 AND 35 THEN 1 ELSE 0 END) as age_18_35,
                SUM(CASE WHEN age BETWEEN 36 AND 55 THEN 1 ELSE 0 END) as age_36_55,
                SUM(CASE WHEN age > 55 THEN 1 ELSE 0 END) as age_55_plus,
                SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) as male_count,
                SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) as female_count,
                COUNT(*) as total
            FROM records
        """)
    
    row = cursor.fetchone()
    conn.close()
    
    total = row[6] or 1
    
    return {
        "age_distribution": [
            {"range": "0-18岁", "count": row[0] or 0, "percentage": round((row[0] or 0) / total * 100, 1)},
            {"range": "19-35岁", "count": row[1] or 0, "percentage": round((row[1] or 0) / total * 100, 1)},
            {"range": "36-55岁", "count": row[2] or 0, "percentage": round((row[2] or 0) / total * 100, 1)},
            {"range": "56岁以上", "count": row[3] or 0, "percentage": round((row[3] or 0) / total * 100, 1)}
        ],
        "gender_distribution": [
            {"gender": "男", "count": row[4] or 0, "percentage": round((row[4] or 0) / total * 100, 1)},
            {"gender": "女", "count": row[5] or 0, "percentage": round((row[5] or 0) / total * 100, 1)}
        ],
        "total": total
    }

# ============ AI 科室综合分析 ==========
@router.post("/ai/analyze-department")
async def analyze_department(
    request: Request,
    current_user: User = Depends(get_current_user_required)
):
    """AI 综合分析科室数据"""
    import asyncio
    import requests
    import sqlite3
    import os
    import json
    
    body = await request.json()
    department = body.get('department', '')
    
    if not department:
        return {"analysis": "请选择科室", "success": False}
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 获取疾病排行榜
    cursor.execute("""
        SELECT diagnosis, COUNT(*) as count
        FROM records
        WHERE department = ? AND diagnosis IS NOT NULL AND diagnosis != ''
        GROUP BY diagnosis
        ORDER BY count DESC
        LIMIT 10
    """, (department,))
    diseases = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    # 2. 获取药品排行榜
    cursor.execute("""
        SELECT prescriptions FROM records
        WHERE department = ? AND prescriptions IS NOT NULL AND prescriptions != '[]'
    """, (department,))
    rows = cursor.fetchall()
    
    drug_count = {}
    for row in rows:
        try:
            prescriptions = json.loads(row[0])
            for p in prescriptions:
                if isinstance(p, dict):
                    drug_name = p.get('drug', '')
                    if drug_name:
                        drug_count[drug_name] = drug_count.get(drug_name, 0) + 1
        except:
            continue
    
    drugs = sorted(drug_count.items(), key=lambda x: x[1], reverse=True)[:10]
    drugs = [{"name": name, "count": count} for name, count in drugs]
    
    # 3. 获取患者画像
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN age < 18 THEN 1 ELSE 0 END) as age_0_18,
            SUM(CASE WHEN age BETWEEN 18 AND 35 THEN 1 ELSE 0 END) as age_18_35,
            SUM(CASE WHEN age BETWEEN 36 AND 55 THEN 1 ELSE 0 END) as age_36_55,
            SUM(CASE WHEN age > 55 THEN 1 ELSE 0 END) as age_55_plus,
            SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) as male_count,
            SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) as female_count,
            COUNT(*) as total
        FROM records
        WHERE department = ?
    """, (department,))
    
    row = cursor.fetchone()
    conn.close()
    
    total = row[6] or 1
    age_distribution = [
        {"range": "0-18岁", "count": row[0] or 0, "percentage": round((row[0] or 0) / total * 100, 1)},
        {"range": "19-35岁", "count": row[1] or 0, "percentage": round((row[1] or 0) / total * 100, 1)},
        {"range": "36-55岁", "count": row[2] or 0, "percentage": round((row[2] or 0) / total * 100, 1)},
        {"range": "56岁以上", "count": row[3] or 0, "percentage": round((row[3] or 0) / total * 100, 1)}
    ]
    male_percentage = round((row[4] or 0) / total * 100, 1)
    female_percentage = round((row[5] or 0) / total * 100, 1)
    
    if not diseases and not drugs:
        return {"analysis": "数据不足，无法分析", "success": False}
    
    # 构建数据摘要
    disease_text = "\n".join([f"{i+1}. {d['name']}：{d['count']}例" for i, d in enumerate(diseases[:10])])
    drug_text = "\n".join([f"{i+1}. {d['name']}：{d['count']}次" for i, d in enumerate(drugs[:10])])
    age_text = "、".join([f"{a['range']}{a['percentage']}%" for a in age_distribution])
    
    prompt = f"""请分析{department}的医疗数据，给出详细专业的分析报告（500字左右）：

【疾病排行 TOP10】
{disease_text}

【药品使用排行 TOP10】
{drug_text}

【患者画像】
- 年龄分布：{age_text}
- 性别分布：男{male_percentage}%，女{female_percentage}%

请从以下维度进行详细分析：

1. **高发疾病分析**
   - 哪些疾病发病率最高，占比多少
   - 可能的原因推测
   - 与去年同期相比的变化趋势

2. **用药规律分析**
   - 最常用的药品及其适应症
   - 用药与高发疾病的匹配度
   - 用药合理性评价

3. **患者群体特征**
   - 主要患病人群的年龄特点
   - 性别分布差异及原因
   - 高危人群特征

4. **管理建议**
   - 针对高发疾病的预防建议
   - 用药管理的优化方向
   - 重点人群的健康干预措施
   - 科室资源配置建议

请用专业、简洁的语言回答，分点阐述。"""

    try:
        doubao_api_key = "91be1b79-0621-44a1-a725-a59462602582"
        doubao_model = "doubao-seed-1-6-250615"
        
        def call_doubao():
            headers = {"Authorization": f"Bearer {doubao_api_key}", "Content-Type": "application/json"}
            payload = {
                "model": doubao_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            response = requests.post(
                "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return None
        
        loop = asyncio.get_event_loop()
        analysis = await loop.run_in_executor(None, call_doubao)
        
        if analysis:
            return {"analysis": analysis, "success": True}
        else:
            return {"analysis": "AI服务暂时不可用，请稍后再试", "success": False}
            
    except Exception as e:
        print(f"调用AI分析失败: {e}")
        return {"analysis": "AI服务暂时不可用，请稍后再试", "success": False}

# ============医生办理出院 ==========
@router.post("/records/discharge/{record_id}")
def discharge_patient(
    record_id: int,
    summary: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    import sqlite3
    import os
    from datetime import date
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查病历存在及权限
    cursor.execute("SELECT department, doctor_id, notes FROM records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="病历不存在")
    
    # 权限：医生只能办理自己科室的病历
    if current_user.role != Role.ADMIN and row[0] != current_user.department:
        conn.close()
        raise HTTPException(status_code=403, detail="无权限办理其他科室出院")
    
    # ⭐ 删除出院检查，直接更新（无论之前有没有出院日期）
    
    today = date.today().isoformat()
    new_notes = (row[2] or "") + f"\n\n【出院小结】{summary}\n【出院日期】{today}"
    
    cursor.execute("UPDATE records SET discharge_date = ?, notes = ? WHERE id = ?",
                   (today, new_notes, record_id))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "已办理出院"}

#