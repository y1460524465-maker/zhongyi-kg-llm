# 创建请求客户端
import requests

# 默认获取
# response = requests.get("http://127.0.0.1:8000/")
# print(f"请求码：{response.status_code}")  # 200
# print(f"获取到文本数据:{response.text}")
# print(f"获取到的json数据为：{response.json()}")  # {'message': 'Hello World'}

print("*" * 100)
# # 路径传参数
# response = requests.get("http://127.0.0.1:8000/items/899")
# print(f"获取到的json数据为：{response.json()}")
# print("*" * 100)

# # 查询传参数
# response = requests.get("http://127.0.0.1:8000/users/", params={"name": "小明", "age": 18})
# print(f"获取到的json数据为：{response.json()}")
# 会报错:获取到的json数据为：{'detail': [{'type': 'missing', 'loc': ['query', 'age'], 'msg': 'Field required', 'input': None}]}
# response = requests.get("http://127.0.0.1:8000/users/", params={"name": "小明"})
# print(f"获取到的json数据为：{response.json()}")
#
# print("*" * 100)
# # 默认参数
response = requests.get("http://127.0.0.1:8000/read_user2/", params={"age": 19})
print(f"获取到的json数据为：{response.json()}")