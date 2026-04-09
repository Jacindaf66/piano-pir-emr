# backend/check_size.py
import sqlite3
import json

conn = sqlite3.connect('storage/hospital.db')
cursor = conn.cursor()
cursor.execute('SELECT record_id, name, treatments, prescriptions, lab_results, imaging_reports, notes FROM records LIMIT 10')

max_size = 0
for row in cursor.fetchall():
    record = {
        "record_id": row[0],
        "name": row[1],
        "treatments": row[2],
        "prescriptions": row[3],
        "lab_results": row[4],
        "imaging_reports": row[5],
        "notes": row[6]
    }
    json_str = json.dumps(record, ensure_ascii=False)
    size = len(json_str.encode('utf-8'))
    max_size = max(max_size, size)
    print(f"{row[0]}: {size} 字节")

print(f"\n最大记录大小: {max_size} 字节")
print(f"建议 block_size: {max_size + 1024}")

conn.close()