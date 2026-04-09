# backend/test_ai_api.py
import requests

# 1. 登录获取 token
print("=" * 50)
print("1. 登录获取 token")
print("=" * 50)

login_res = requests.post(
    "http://127.0.0.1:8000/api/login",
    json={"username": "admin", "password": "123456"}
)

if login_res.status_code != 200:
    print(f"登录失败: {login_res.status_code}")
    print(login_res.text)
    exit()

token = login_res.json()["token"]
print(f"✅ 登录成功")
print(f"Token: {token[:50]}...")

# 2. 测试 AI 接口
print("\n" + "=" * 50)
print("2. 测试 AI 接口")
print("=" * 50)

ai_res = requests.post(
    "http://127.0.0.1:8000/api/ai/chat",
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    },
    json={
        "messages": [{"role": "user", "content": "患者发热38.5度，咳嗽3天"}],
        "model": "deepseek"
    },
    timeout=60
)

print(f"状态码: {ai_res.status_code}")
print(f"响应头: {ai_res.headers.get('content-type')}")
print(f"响应内容: {ai_res.text[:1000] if ai_res.text else '空'}")

if ai_res.status_code == 200:
    data = ai_res.json()
    if data.get("success"):
        print("\n✅ AI 响应内容:")
        print(data.get("content", "无内容"))
    else:
        print("\n❌ AI 返回错误:", data)
else:
    print(f"\n❌ 请求失败: {ai_res.status_code}")