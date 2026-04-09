# backend/data_engine/generator.py
import sqlite3
import json
import random
from faker import Faker
from datetime import datetime, timedelta
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_engine.models import DOCTORS, DEPARTMENTS, DIAGNOSES, get_doctors_by_department
from data_engine.models import DRUGS, TREATMENTS, IMAGING_REPORTS, NOTES_OPTIONS

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage', 'hospital.db')
TOTAL_RECORDS = 10000

fake = Faker('zh_CN')

def get_doctor_for_department(dept):
    """根据科室返回对应的医生"""
    doctors_by_dept = get_doctors_by_department()
    available = doctors_by_dept.get(dept, [])
    if available:
        return random.choice(available)
    # 默认返回第一个医生
    return DOCTORS[0]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id TEXT UNIQUE,
            id_card TEXT,
            name TEXT,
            gender TEXT,
            age INTEGER,
            admission_date TEXT,
            discharge_date TEXT,
            diagnosis TEXT,
            treatments TEXT,
            prescriptions TEXT,
            lab_results TEXT,
            imaging_reports TEXT,
            doctor_id TEXT,
            doctor_name TEXT,
            department TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    return conn

def generate_data():
    conn = init_db()
    cursor = conn.cursor()
    
    print(f"🚀 开始生成 {TOTAL_RECORDS} 条病历数据...")
    print(f"📋 医生数量: {len(DOCTORS)} 人")
    print("=" * 50)
    
    history_patients = []
    batch_size = 1000
    buffer = []
    
    dept_count = {dept: 0 for dept in DEPARTMENTS}
    doctor_count = {doc["username"]: 0 for doc in DOCTORS}

    for i in range(TOTAL_RECORDS):
        # 30% 概率复用老患者
        if history_patients and random.random() < 0.3:
            patient = random.choice(history_patients)
        else:
            gender = random.choice(['M', 'F'])
            id_card = fake.ssn(min_age=18, max_age=90)
            patient = {
                "id_card": id_card,
                "name": fake.name_male() if gender == 'M' else fake.name_female(),
                "gender": gender,
                "age": random.randint(18, 90)
            }
            history_patients.append(patient)
        
        # 就诊信息
        record_id = f"MR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{i:06d}"
        dept = random.choice(DEPARTMENTS)
        diagnosis = random.choice(DIAGNOSES[dept])
        doctor = get_doctor_for_department(dept)
        
        adm_date = fake.date_between(start_date='-3y', end_date='today')
        stay_days = random.randint(1, 14)
        disc_date = adm_date + timedelta(days=stay_days)
        
        lab_info = {
            "血糖": f"{round(random.uniform(4.0, 9.0), 1)}",
            "血压": f"{random.randint(100, 160)}/{random.randint(60, 100)}",
            "胆固醇": f"{round(random.uniform(3.0, 6.5), 1)}"
        }
        
        treatments = json.dumps(random.sample(TREATMENTS, k=random.randint(2, 4)), ensure_ascii=False)
        prescriptions = json.dumps([{"drug": random.choice(DRUGS), "dosage": f"{random.randint(1, 3)}次/日"}], ensure_ascii=False)
        imaging_reports = random.choice(IMAGING_REPORTS)
        notes = random.choice(NOTES_OPTIONS)
        
        row = (
            record_id,
            patient['id_card'],
            patient['name'],
            patient['gender'],
            patient['age'],
            adm_date.strftime("%Y-%m-%d"),
            disc_date.strftime("%Y-%m-%d"),
            diagnosis,
            treatments,
            prescriptions,
            json.dumps(lab_info, ensure_ascii=False),
            imaging_reports,
            doctor["username"],
            doctor["name"],
            dept,
            notes
        )
        buffer.append(row)
        
        dept_count[dept] += 1
        doctor_count[doctor["username"]] += 1

        if len(buffer) >= batch_size:
            cursor.executemany('''
                INSERT INTO records (
                    record_id, id_card, name, gender, age, 
                    admission_date, discharge_date, diagnosis, 
                    treatments, prescriptions, lab_results, 
                    imaging_reports, doctor_id, doctor_name, department, notes
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', buffer)
            conn.commit()
            buffer = []
            print(f"   已生成 {i + 1} / {TOTAL_RECORDS} 条...")

    if buffer:
        cursor.executemany('''
            INSERT INTO records (
                record_id, id_card, name, gender, age, 
                admission_date, discharge_date, diagnosis, 
                treatments, prescriptions, lab_results, 
                imaging_reports, doctor_id, doctor_name, department, notes
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', buffer)
        conn.commit()
    
    conn.close()
    
    print("=" * 50)
    print("✅ 数据生成完成！")
    print(f"\n📊 各科室病历分布:")
    for dept, count in dept_count.items():
        print(f"   {dept}: {count} 条")
    
    print(f"\n👨‍⚕️ 各医生接诊量:")
    for doc in DOCTORS:
        count = doctor_count[doc["username"]]
        print(f"   {doc['name']}({doc['title']}): {count} 条")
    
    print(f"\n💾 数据库位置: {DB_PATH}")

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ 删除旧数据库")
    generate_data()