from typing import Optional

from fastapi import FastAPI, Form
from pydantic import BaseModel

app = FastAPI()
# 表单数据
@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    print(f"用户名为:{username}")
    print(f"密码为:{password}")
    return {"username": username}

# 通过json 方式传递参数
@app.post("/json_data/")
async def login2(data: dict):
    print(f"数据是{data}")
    return {"received_data":data}

#通过pydatic方式传递参数, 这个会进行参数的校验
# 通过Pydantic方式进行传参
class Item(BaseModel):
    name: str
    description: str
    price:float

# 接收JSON数据的POST接口
@app.post("/items/")
async def create_item(item: Item):
    # 可以直接使用item对象，FastAPI会自动解析JSON
    print(item.model_dump())
    return {"item": item.model_dump(), "message": "Item created successfully"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)