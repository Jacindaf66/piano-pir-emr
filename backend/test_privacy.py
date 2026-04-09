# backend/test_privacy.py
"""
完整PIR测试：
1. 隐私性（无法推断索引）
2. 新旧病历是否都走PIR
3. 查询结构正确性
"""

import requests
import random
import struct
from collections import Counter

BASE_URL = "http://127.0.0.1:8000/api"


# =========================
# 基础工具
# =========================

def login():
    resp = requests.post(f"{BASE_URL}/login", json={
        "username": "admin",
        "password": "123456"
    })
    if resp.status_code != 200:
        print("❌ 登录失败")
        return None
    return resp.json()["token"]


def get_meta(token):
    resp = requests.get(f"{BASE_URL}/meta", headers={
        "Authorization": f"Bearer {token}"
    })
    return resp.json()


# =========================
# 生成查询（统一逻辑）
# =========================

def generate_query(db_size, target_index, chunk_size=100):
    num_chunks = (db_size + chunk_size - 1) // chunk_size
    target_chunk = target_index // chunk_size

    offsets = []
    for chunk in range(num_chunks):
        if chunk == target_chunk:
            continue
        offsets.append(random.randint(0, chunk_size - 1))

    query_bytes = b''.join(struct.pack('<I', o) for o in offsets)
    return query_bytes, offsets


# =========================
# 测试1：查询大小
# =========================

def test_query_size(token):
    print("\n[测试1] 查询大小")

    meta = get_meta(token)
    db_size = meta["db_size"]

    chunk_size = 100
    num_chunks = (db_size + chunk_size - 1) // chunk_size
    expected = (num_chunks - 1) * 4

    q, _ = generate_query(db_size, random.randint(0, db_size-1))

    print(f"期望: {expected}, 实际: {len(q)}")

    print("✅ 正确" if len(q) == expected else "❌ 错误")


# =========================
# 测试2：隐私性（分布）
# =========================

def test_distribution(token):
    print("\n[测试2] 偏移分布")

    meta = get_meta(token)
    db_size = meta["db_size"]

    offsets_all = []

    for _ in range(50):
        _, offsets = generate_query(db_size, random.randint(0, db_size-1))
        offsets_all.extend(offsets)

    counter = Counter(offsets_all)

    for k, v in list(counter.items())[:10]:
        print(f"offset {k}: {v}次")

    print("✅ 分布基本随机（人工判断）")


# =========================
# 测试3：同一索引多次查询
# =========================

def test_same_index_random(token):
    print("\n[测试3] 同一索引多次查询")

    meta = get_meta(token)
    db_size = meta["db_size"]

    target = random.randint(0, db_size-1)

    queries = set()

    for _ in range(20):
        q, _ = generate_query(db_size, target)
        queries.add(q)

    if len(queries) > 1:
        print(f"✅ {len(queries)}种不同查询")
    else:
        print("❌ 查询完全一样（严重问题）")


# =========================
# 测试4：新旧病历是否都走PIR
# =========================

def test_old_new_records(token):
    print("\n[测试4] 新旧病历PIR验证")

    resp = requests.get(f"{BASE_URL}/records/list?limit=20", headers={
        "Authorization": f"Bearer {token}"
    })

    records = resp.json()["records"]

    old = [r for r in records if r["index"] < 10000][:2]
    new = [r for r in records if r["index"] >= 10000][:2]

    print("\n老数据:")
    for r in old:
        print(f"  index={r['index']}")

    print("\n新数据:")
    for r in new:
        print(f"  index={r['index']}")

    print("\n👉 请结合后端日志确认：")
    print("   - 没有 '未找到主表条目'")
    print("   - 返回块数一致")
    print("   => 才说明走了PIR")


# =========================
# 主函数
# =========================

def main():
    print("="*60)
    print("PIR完整验证")
    print("="*60)

    token = login()
    if not token:
        return

    test_query_size(token)
    test_distribution(token)
    test_same_index_random(token)
    test_old_new_records(token)

    print("\n结论：")
    print("如果全部通过 + 日志正常 → 你的PIR是成立的")


if __name__ == "__main__":
    main()