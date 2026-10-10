from typing import Optional

from fastapi import FastAPI

app = FastAPI()

#get 方式路径传参
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# 查询参数传参
@app.get("/users/")
async def read_users(name: str, age: int):
    return {"name": name, "age": age}

#可选参数传参 Optional 关键词,这个参数可有,可不有
@app.get("/read_user2/")
async def read_user2(name: Optional[str] = None , age: int = 18):
    return {"name": name, "age": age}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)