# 创建请求客户端
import requests

# 单文件上传
file_path = "index.html"
# 发送单文件上传请求
url = "http://127.0.0.1:8000/uploadfile/"
with open(file_path, "rb") as f:
    files = {"file": (file_path, f)}
    response = requests.post(url, files=files)

print("单文件上传响应:")
print(f"状态码: {response.status_code}")
print(f"响应内容: {response.json()}")