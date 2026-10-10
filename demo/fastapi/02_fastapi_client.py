#一般是用reqeusts 这个库来模型请求, requests 可以做爬虫
import requests

#模拟请求
response = requests.get("http://127.0.0.1:8000")
print(response.text) # 这里获得的是一个字符串
print(response.json()) # 这里获得是一个字典