# backend/check_db.py
import sqlite3
import os

db_path = 'storage/hospital.db'

print(f"数据库路径: {db_path}")
print(f"文件是否存在: {os.path.exists(db_path)}")
print()

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查看所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("所有表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    print()
    
    # 查看 users 表数据
    try:
        cursor.execute("SELECT id, username, name, role, department FROM users;")
        users = cursor.fetchall()
        print(f"users 表数据 ({len(users)}条):")
        for user in users:
            print(f"  ID:{user[0]}, 用户名:{user[1]}, 姓名:{user[2]}, 角色:{user[3]}, 科室:{user[4]}")
    except Exception as e:
        print(f"users 表不存在或无法读取: {e}")
    
    conn.close()
else:
    print("数据库文件不存在！")

# backend/check_db.py
import sqlite3

conn = sqlite3.connect('storage/hospital.db')
cursor = conn.cursor()

print("=" * 50)
print("1. 所有用户的role值:")
cursor.execute("SELECT role FROM users")
roles = cursor.fetchall()
print([r[0] for r in roles])

print("\n2. 小写doctor数量:")
cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor'")
print(cursor.fetchone()[0])

print("\n3. 大写DOCTOR数量:")
cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'DOCTOR'")
print(cursor.fetchone()[0])

print("\n4. 包含doc的数量:")
cursor.execute("SELECT COUNT(*) FROM users WHERE role LIKE '%doc%'")
print(cursor.fetchone()[0])

print("\n5. 所有医生及其科室:")
cursor.execute("SELECT username, name, department, role FROM users WHERE role LIKE '%doc%'")
for row in cursor.fetchall():
    print(f"   {row[0]} | {row[1]} | {row[2]} | role={row[3]}")

print("\n6. 接诊记录中的医生:")
cursor.execute("SELECT doctor_name, COUNT(*) FROM records GROUP BY doctor_name ORDER BY COUNT(*) DESC")
for row in cursor.fetchall():
    print(f"   {row[0]}: {row[1]}条")

conn.close()

