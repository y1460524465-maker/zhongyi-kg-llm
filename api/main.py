import asyncio
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel
from typing import Optional
import sys
import os
import logging

from starlette.responses import StreamingResponse

from api.msg_queue_manager import msg_queue_manager

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入工作流
from langgraph_more_nodes.full_workflow import run_workflow, build_graph

#定义了fastapi对象
app = FastAPI(title="中医知识图谱问答系统", description="基于FastAPI和LangGraph的中医知识图谱智能问答系统")
# 常驻 LangGraph 实例
_memory = InMemorySaver()
# _workflow_app = build_graph().compile()
#添加记忆功能
_workflow_app = build_graph().compile(_memory)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

#请求体
class QueryRequest(BaseModel):
    """查询请求模型"""
    input: str
    session_id: Optional[str] = None

#响应体
class QueryResponse(BaseModel):
    """查询响应模型"""
    input: str
    output: str

#主要是判断我们的接口是否正常，系统是否挂掉
@app.get("/")
async def root():
    """健康检查接口"""
    return {"status": "ok", "message": "中医知识图谱问答系统服务运行正常"}

#中医问答的核心业务接口
@app.post("/process", response_model=QueryResponse)
async def process(request: QueryRequest):
    """
    中医问答接口（核心接口）

    接收用户问题，返回中医知识图谱的智能回答

    Args:
        request: 请求对象，包含JSON格式的用户输入

    Returns:
        QueryResponse: 包含输入和输出的响应
    """
    try:
        input_text = request.input
        thread_id = request.session_id or "default"
        
        if not input_text:
            return JSONResponse(
                content={"input": "", "output": "请输入问题！"},
                status_code=200
            )
        
        logger.info(f"收到查询请求: {input_text[:50]}...")
        
        # 调用工作流（使用常驻实例以保留多轮历史）
        result = _workflow_app.invoke(
            {"input": input_text},
            config={"configurable": {"thread_id": thread_id}}
        )
        # 如下就没有区分用户,导致用户的记忆混乱
        # result = _workflow_app.invoke(
        #     {"input": input_text},
        #     config={"configurable": {"thread_id": "default"}}
        # )
        
        output = result.get("output", "")
        
        # 处理空输出情况
        if not output:
            output = result.get("direct_out", "系统出错了，请重试！")
        
        logger.info(f"查询完成，输出长度: {len(output)}")
        
        return {
            "input": input_text,
            "output": output
        }
        
    except Exception as e:
        logger.error(f"查询处理失败: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"input": "", "output": "系统出错了，请重试！"},
            status_code=500
        )


async def zhongyi_response(input: str, thread_id: str):
    config = RunnableConfig(configurable={
        "thread_id": thread_id
    })
    result = await _workflow_app.ainvoke({"input": input}, config=config)
    return result["output"]

async def my_zhongyi_project(input, user_id):
    await zhongyi_response(input, user_id)


async def generate_data(input, user_id):
    # 确保 queue 存在，并把当前事件循环注入 manager（节点线程需要它）
    msg_queue_manager.set_loop(asyncio.get_running_loop())
    msg_queue_manager.get_msg_queue(user_id)  # 提前创建队列，避免节点线程里创建时竞争

    # 异步执行任务
    asyncio.create_task(my_zhongyi_project(input, user_id))

    while True:
        msg = await msg_queue_manager.get_msg_queue(user_id).get()
        print(msg)
        # 推送 SSE
        yield json.dumps(msg)
        if msg.get("type") == "done":
            break

@app.post("/process_stream")
async def process_data(request: QueryRequest):
    input_text = request.input
    user_id = request.session_id or "default"
    return StreamingResponse(generate_data(input_text, user_id), media_type="text/plain")



# 挂载静态文件目录（可选）
# app.mount("/picture", StaticFiles(directory="path/to/pictures"), name="picture")


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 启动中医知识图谱问答系统服务...")
    # 使用导入字符串格式以支持 reload 模式
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)