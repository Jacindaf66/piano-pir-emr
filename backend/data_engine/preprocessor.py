# backend/data_engine/preprocessor.py
import sqlite3
import json
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'storage', 'hospital.db')
NPY_PATH = os.path.join(BASE_DIR, 'storage', 'db.npy')
META_PATH = os.path.join(BASE_DIR, 'storage', 'metadata.json')

# 块大小设置为 8192 字节
BLOCK_SIZE = 8192

def process_data():
    print("⚙️ 开始数据预处理...")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM records ORDER BY id")
    rows = cursor.fetchall()
    
    print(f"📊 共 {len(rows)} 条记录")
    
    binary_list = []
    patients_map = {}
    global_index = {}

    for index, row in enumerate(rows):
        row_dict = dict(row)
        
        pid = row_dict['id_card']
        rid = row_dict['record_id']

        # 构建 global_index
        global_index[rid] = index

        # 构建 patients_map
        if pid not in patients_map:
            patients_map[pid] = {
                "name": row_dict['name'],
                "gender": row_dict['gender'],
                "records": []
            }
        
        patients_map[pid]["records"].append({
            "rid": rid,
            "date": row_dict['admission_date'],
            "diagnosis": row_dict['diagnosis'],
            "dept": row_dict['department'],
            "doctor": row_dict['doctor_name']
        })

        # 二进制处理
        json_str = json.dumps(row_dict, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        
        if len(json_bytes) > BLOCK_SIZE:
            print(f"⚠️ 警告: 记录 {rid} 大小 {len(json_bytes)} 超过块大小 {BLOCK_SIZE}")
            padded_bytes = json_bytes[:BLOCK_SIZE]
        else:
            padded_bytes = json_bytes + b'\x00' * (BLOCK_SIZE - len(json_bytes))
        
        binary_list.append(np.frombuffer(padded_bytes, dtype=np.uint8))

    print("📦 拼接大矩阵...")
    final_db = np.array(binary_list)
    np.save(NPY_PATH, final_db)
    
    final_meta = {
        "total_records": len(rows),
        "block_size": BLOCK_SIZE,
        "patients": patients_map,
        "indices": global_index,
        "doctor_stats": {}
    }
    
    with open(META_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_meta, f, ensure_ascii=False, indent=2)

    conn.close()
    print("✅ 预处理完成！")
    print("shape:", final_db.shape)

if __name__ == "__main__":
    process_data()