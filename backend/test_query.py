# 文件: backend/test_query.py
import requests
import os
import numpy as np

URL = "http://127.0.0.1:8000/query"

# 生成随机 16 字节 seed
seed = os.urandom(16)

# 发送 POST 请求
resp = requests.post(URL, data=seed)
print("状态码:", resp.status_code)
print("返回长度:", len(resp.content))

# 转 numpy 解码 (演示)
answer = np.frombuffer(resp.content, dtype=np.uint8)
print("前16字节 (hex):", answer[:16].tobytes().hex())
