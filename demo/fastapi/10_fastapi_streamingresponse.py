from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import uvicorn

app = FastAPI()


async def generate_data():
    res_list = ["我", "特别", "喜欢", "玩儿", "大模型"]
    for res in res_list:
        await asyncio.sleep(0.5)
        yield res

# 1.使用StreamingResponse  2. 定义一个数据生成器generate_data
@app.post("/stream")
async def stream_data():
    # 创建流式响应对象，将generate_data函数作为数据源，media_type设置为text/plain
    # 这里返回的不是一个字符串，而是一个可迭代对象,迭代器
    return StreamingResponse(generate_data(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)