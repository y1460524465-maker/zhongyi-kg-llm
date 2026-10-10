import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
#定义 fastapi 对象
app = FastAPI()

#定义接口
@app.get("/")
async def read_index():
    print("read_index:静态页")
    return FileResponse("index.html")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

