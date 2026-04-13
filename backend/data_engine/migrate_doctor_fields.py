# backend/data_engine/migrate_doctor_fields.py
"""
医生表字段迁移
1. 添加新字段
2. 给旧医生设置默认值
"""
import sqlite3
import os
from datetime import date

def migrate():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
    
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 获取现有字段
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"现有字段: {columns}")
    
    # 2. 添加新字段
    fields_to_add = [
        ('gender', 'VARCHAR(10)', "'男'"),
        ('birth_date', 'DATE', "NULL"),
        ('title', 'VARCHAR(50)', "'主治医师'"),
        ('phone', 'VARCHAR(20)', "''"),
        ('email', 'VARCHAR(100)', "''"),
        ('join_date', 'DATE', "'2024-01-01'"),
        ('bio', 'TEXT', "''"),
        ('avatar', 'TEXT', "''")
    ]
    
    for field_name, field_type, default_value in fields_to_add:
        if field_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {field_name} {field_type} DEFAULT {default_value}")
                print(f"✅ 添加字段: {field_name}")
            except Exception as e:
                print(f"❌ 添加 {field_name} 失败: {e}")
        else:
            print(f"⏭️ 字段已存在: {field_name}")
    
    # 3. 给旧医生设置默认值
    cursor.execute("""
        UPDATE users 
        SET 
            gender = COALESCE(NULLIF(gender, ''), '男'),
            title = COALESCE(NULLIF(title, ''), '主治医师'),
            phone = COALESCE(phone, ''),
            email = COALESCE(email, ''),
            join_date = COALESCE(join_date, '2024-01-01'),
            bio = COALESCE(bio, ''),
            avatar = COALESCE(avatar, '')
        WHERE role = 'DOCTOR'
    """)
    
    conn.commit()
    
    # 4. 查看结果
    cursor.execute("""
        SELECT id, name, gender, title, join_date, phone, email 
        FROM users WHERE role = 'DOCTOR'
    """)
    doctors = cursor.fetchall()
    
    print("\n✅ 迁移完成！当前医生信息：")
    for doc in doctors:
        print(f"   ID:{doc[0]} | {doc[1]} | 性别:{doc[2]} | 职称:{doc[3]} | 入职:{doc[4]}")
    
    conn.close()
    print("\n🎉 迁移成功！请重启后端服务。")

if __name__ == "__main__":
    migrate()