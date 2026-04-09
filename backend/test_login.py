import requests

# 测试登录
response = requests.post(
    "http://127.0.0.1:8000/api/login",
    json={"username": "admin", "password": "123456"}
)

print("登录响应:")
print(response.json())
print(f"状态码: {response.status_code}")

# 测试注册
response2 = requests.post(
    "http://127.0.0.1:8000/api/register",
    json={
        "username": "newdoctor",
        "password": "123456",
        "name": "新医生",
        "department": "外科"
    }
)

print("\n注册响应:")
print(response2.json())