from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import uvicorn
import json

msg_queue: asyncio.Queue = asyncio.Queue()
app = FastAPI()

# 这种方式是使用最多的方式 StreamingResponse+asyncio.Queue  生产者+消费者模式
async def my_test_project():
    res_list = ["我", "是", "一个", "测试", "程序"]
    for msg in res_list:
        await msg_queue.put({"type": "msg", "msg": msg})
        await asyncio.sleep(0.5)
    await msg_queue.put({"type": "done", "msg": ""})


async def generate_data():
    # 异步执行任务 ,这个异步任务就是用来生产数据,把数据放到异步队列中
    # msg_queue: asyncio.Queue = asyncio.Queue()
    asyncio.create_task(my_test_project())

    while True:
        # 从异步队列中获取数据  消费者
        msg = await msg_queue.get()
        # 推送 SSE
        yield json.dumps(msg)
        if msg.get("type") == "done":
            break


@app.post("/stream")
async def stream_data():
    return StreamingResponse(generate_data(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)