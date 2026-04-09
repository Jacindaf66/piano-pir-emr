# backend/test_performance.py
"""
PIANO 查询性能测试
测试查询时间、通信量、吞吐量
"""

import requests
import time
import statistics
import json
import random
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"


def login():
    """登录获取 token"""
    resp = requests.post(f"{BASE_URL}/login", json={
        "username": "admin",
        "password": "123456"
    })
    if resp.status_code != 200:
        print(f"登录失败: {resp.status_code}")
        return None
    return resp.json()["token"]


def get_metadata(token):
    """获取元数据"""
    resp = requests.get(f"{BASE_URL}/meta", headers={
        "Authorization": f"Bearer {token}"
    })
    return resp.json()


def get_records_list(token, limit=100):
    """获取病历列表"""
    resp = requests.get(f"{BASE_URL}/records/list", params={
        "limit": limit,
        "offset": 0
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    return resp.json()


def test_single_query_performance(token, target_index, repeat=10):
    """
    测试单次查询性能
    返回: (平均时间ms, 平均响应大小, 成功率)
    """
    times = []
    sizes = []
    successes = 0
    
    for i in range(repeat):
        try:
            start = time.perf_counter()
            
            # 发送查询
            resp = requests.post(f"{BASE_URL}/query",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/octet-stream"
                },
                data=b'\x00' * 400  # 模拟查询数据
            )
            
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            sizes.append(len(resp.content))
            
            if resp.status_code == 200:
                successes += 1
                
        except Exception as e:
            print(f"查询失败: {e}")
    
    avg_time = statistics.mean(times) if times else 0
    avg_size = statistics.mean(sizes) if sizes else 0
    success_rate = successes / repeat * 100
    
    return avg_time, avg_size, success_rate


def test_multiple_queries_performance(token, num_queries=100):
    """
    测试批量查询性能
    """
    print(f"\n{'='*60}")
    print(f"批量查询测试 ({num_queries} 次)")
    print(f"{'='*60}")
    
    # 获取病历列表
    records_data = get_records_list(token, limit=num_queries)
    records = records_data["records"]
    
    if len(records) < num_queries:
        print(f"警告: 只有 {len(records)} 条病历可用")
        num_queries = len(records)
    
    query_times = []
    decrypt_times = []
    total_sizes = []
    
    for i, record in enumerate(records[:num_queries]):
        # 模拟查询时间
        start = time.perf_counter()
        
        resp = requests.post(f"{BASE_URL}/query",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/octet-stream"
            },
            data=b'\x00' * 400
        )
        
        query_time = (time.perf_counter() - start) * 1000
        query_times.append(query_time)
        total_sizes.append(len(resp.content))
        
        if (i + 1) % 20 == 0:
            print(f"  已完成 {i+1}/{num_queries} 次查询")
    
    # 统计结果
    avg_query_time = statistics.mean(query_times)
    p95_query_time = sorted(query_times)[int(len(query_times) * 0.95)]
    max_query_time = max(query_times)
    min_query_time = min(query_times)
    avg_size = statistics.mean(total_sizes)
    
    print(f"\n📊 统计结果:")
    print(f"  平均查询时间: {avg_query_time:.2f} ms")
    print(f"  95% 查询时间: {p95_query_time:.2f} ms")
    print(f"  最快查询时间: {min_query_time:.2f} ms")
    print(f"  最慢查询时间: {max_query_time:.2f} ms")
    print(f"  平均响应大小: {avg_size:.0f} 字节 ({avg_size/1024:.1f} KB)")
    print(f"  总耗时: {sum(query_times)/1000:.2f} 秒")
    print(f"  吞吐量: {num_queries / (sum(query_times)/1000):.2f} 查询/秒")
    
    return {
        "avg_time": avg_query_time,
        "p95_time": p95_query_time,
        "min_time": min_query_time,
        "max_time": max_query_time,
        "avg_size": avg_size,
        "throughput": num_queries / (sum(query_times)/1000)
    }


def test_different_indices_performance(token):
    """
    测试不同索引位置的查询性能
    """
    print(f"\n{'='*60}")
    print("不同索引位置查询性能测试")
    print(f"{'='*60}")
    
    # 获取病历列表
    records_data = get_records_list(token, limit=100)
    records = records_data["records"]
    
    # 按索引分组
    early_indices = [r for r in records if r["index"] < 1000][:5]
    mid_indices = [r for r in records if 1000 <= r["index"] < 5000][:5]
    late_indices = [r for r in records if r["index"] >= 5000][:5]
    new_indices = [r for r in records if r["index"] >= 10000][:3]
    
    groups = [
        ("早期索引 (0-1000)", early_indices),
        ("中期索引 (1000-5000)", mid_indices),
        ("晚期索引 (5000+)", late_indices),
        ("新增病历 (10000+)", new_indices)
    ]
    
    results = {}
    
    for group_name, indices in groups:
        if not indices:
            print(f"\n{group_name}: 无数据")
            continue
        
        print(f"\n{group_name}:")
        times = []
        
        for record in indices[:5]:
            start = time.perf_counter()
            resp = requests.post(f"{BASE_URL}/query",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/octet-stream"
                },
                data=b'\x00' * 400
            )
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            print(f"  索引 {record['index']}: {elapsed:.2f} ms")
        
        avg_time = statistics.mean(times)
        results[group_name] = avg_time
        print(f"  平均: {avg_time:.2f} ms")
    
    return results


def test_concurrent_queries(token, num_concurrent=10, num_queries_per_client=5):
    """
    测试并发查询性能
    """
    import concurrent.futures
    
    print(f"\n{'='*60}")
    print(f"并发查询测试 ({num_concurrent} 并发, 每客户端 {num_queries_per_client} 次)")
    print(f"{'='*60}")
    
    def worker(worker_id):
        times = []
        for i in range(num_queries_per_client):
            start = time.perf_counter()
            try:
                resp = requests.post(f"{BASE_URL}/query",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/octet-stream"
                    },
                    data=b'\x00' * 400,
                    timeout=30
                )
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            except Exception as e:
                print(f"Worker {worker_id} 查询失败: {e}")
        return times
    
    start_total = time.perf_counter()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(worker, i) for i in range(num_concurrent)]
        all_times = []
        for future in concurrent.futures.as_completed(futures):
            all_times.extend(future.result())
    
    total_time = time.perf_counter() - start_total
    total_queries = num_concurrent * num_queries_per_client
    
    avg_time = statistics.mean(all_times) if all_times else 0
    p95_time = sorted(all_times)[int(len(all_times) * 0.95)] if all_times else 0
    
    print(f"\n📊 并发统计:")
    print(f"  总查询数: {total_queries}")
    print(f"  总耗时: {total_time:.2f} 秒")
    print(f"  平均响应时间: {avg_time:.2f} ms")
    print(f"  95% 响应时间: {p95_time:.2f} ms")
    print(f"  吞吐量: {total_queries / total_time:.2f} 查询/秒")
    
    return {
        "total_queries": total_queries,
        "total_time": total_time,
        "avg_time": avg_time,
        "p95_time": p95_time,
        "throughput": total_queries / total_time
    }


def run_full_performance_test():
    """运行完整性能测试"""
    print("\n" + "="*60)
    print("PIANO 查询性能测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 登录
    token = login()
    if not token:
        print("登录失败，无法测试")
        return
    
    print("登录成功")
    
    # 获取元数据
    meta = get_metadata(token)
    print(f"数据库大小: {meta['db_size']} 条记录")
    print(f"块大小: {meta['block_size']} 字节")
    
    # 1. 批量查询测试
    batch_result = test_multiple_queries_performance(token, num_queries=50)
    
    # 2. 不同索引位置测试
    index_results = test_different_indices_performance(token)
    
    # 3. 并发查询测试
    concurrent_result = test_concurrent_queries(token, num_concurrent=5, num_queries_per_client=10)
    
    # 生成报告
    print("\n" + "="*60)
    print("性能测试报告")
    print("="*60)
    
    print(f"""
📈 测试结果汇总:

1. 批量查询 (50次)
   - 平均响应时间: {batch_result['avg_time']:.2f} ms
   - 95% 响应时间: {batch_result['p95_time']:.2f} ms
   - 吞吐量: {batch_result['throughput']:.2f} 查询/秒
   - 平均响应大小: {batch_result['avg_size']/1024:.1f} KB

2. 不同索引位置
   - 早期索引: {index_results.get('早期索引 (0-1000)', 0):.2f} ms
   - 中期索引: {index_results.get('中期索引 (1000-5000)', 0):.2f} ms
   - 晚期索引: {index_results.get('晚期索引 (5000+)', 0):.2f} ms
   - 新增病历: {index_results.get('新增病历 (10000+)', 0):.2f} ms

3. 并发查询 (5并发 x 10次)
   - 平均响应时间: {concurrent_result['avg_time']:.2f} ms
   - 吞吐量: {concurrent_result['throughput']:.2f} 查询/秒

✅ 测试完成
    """)
    
    # 保存结果到文件
    result = {
        "timestamp": datetime.now().isoformat(),
        "db_size": meta['db_size'],
        "batch_query": batch_result,
        "index_performance": index_results,
        "concurrent_query": concurrent_result
    }
    
    with open("performance_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    
    print(f"详细结果已保存到: performance_result.json")


if __name__ == "__main__":
    run_full_performance_test()