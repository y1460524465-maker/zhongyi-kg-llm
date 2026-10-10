#导包
import requests

#用form表达方式
# response= requests.post("http://127.0.0.1:8000/login", data={"username": "小明", "password": "123456"})
# print(response.status_code)
# print(response.json())

# #利用json方式传递参数
response= requests.post("http://127.0.0.1:8000/json_data", json={ "password": "123456"})
print(response.status_code)
print(response.json())

# #pydatic方式
# # response = requests.post("http://127.0.0.1:8000/items/",
# #                          json={"name": "钢笔", "description": "这是一个描述", "price": 10.5})
#
# #{'detail': [{'type': 'missing', 'loc': ['body', 'name'], 'msg': 'Field required', 'input': {'description': '这是一个描述', 'price': 10.5}}]}
# response = requests.post("http://127.0.0.1:8000/items/",
#                          json={"description": "这是一个描述", "price": 10.5})
print(response.json())