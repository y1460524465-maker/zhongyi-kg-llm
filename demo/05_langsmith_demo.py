"""
LangGraph Agent with LangSmith Tracing
展示如何使用 LangSmith 追踪 Agent 的执行过程
"""

import os
import time
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
import operator

from common.llm import conf

# ========== 1. 配置 LangSmith ==========

# LangSmith 密钥从 common/.env 读取（common.llm 已统一注入），此处仅指定项目名
os.environ["LANGCHAIN_TRACING_V2"] = conf.LANGSMITH_TRACING or "false"
os.environ["LANGCHAIN_PROJECT"] = "langgraph-agent-demo5"
if conf.LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = conf.LANGSMITH_API_KEY

# ========== 2. 定义工具 ==========

@tool
def search_weather(city: str) -> str:
    """查询指定城市的天气信息"""
    # 模拟天气 API
    time.sleep(20)
    weather_data = {
        "北京": "晴天，25°C，空气质量良好",
        "上海": "多云，28°C，湿度较高",
        "深圳": "小雨，30°C，建议带伞",
    }
    return weather_data.get(city, f"未找到{city}的天气信息")

@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def search_knowledge(query: str) -> str:
    """搜索知识库"""
    # 模拟知识库
    knowledge = {
        "LangGraph": "LangGraph 是一个用于构建有状态多 Actor 应用的库",
        "LangSmith": "LangSmith 是 LangChain 的可观测性平台",
    }
    for key, value in knowledge.items():
        if key.lower() in query.lower():
            return value
    return "未找到相关信息"

tools = [search_weather, calculate, search_knowledge]

# ========== 3. 初始化 LLM ==========

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=conf.MODEL_API_KEY
)
llm_with_tools = llm.bind_tools(tools)

# ========== 4. 定义 State ==========

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

# ========== 5. 定义节点函数 ==========

def call_model(state: AgentState) -> dict:
    """调用 LLM"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """判断是否需要继续调用工具"""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# ========== 6. 构建 Graph ==========

graph = StateGraph(AgentState)

# 添加节点
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))

# 添加边
graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", END: END}
)
graph.add_edge("tools", "agent")

# 编译
agent = graph.compile()

# ========== 7. 运行 Agent ==========

if __name__ == "__main__":
    # 测试 1: 天气查询
    print("=" * 50)
    print("测试 1: 天气查询")
    print("=" * 50)

    result = agent.invoke({
        "messages": [
            SystemMessage(content="你是一个有用的助手，可以查询天气、计算数学表达式、搜索知识。"),
            HumanMessage(content="北京今天天气怎么样？")
        ]
    })
    print(f"回答: {result['messages'][-1].content}\n")

    # 测试 2: 多工具调用
    print("=" * 50)
    print("测试 2: 多工具调用")
    print("=" * 50)

    result = agent.invoke({
        "messages": [
            SystemMessage(content="你是一个有用的助手，可以查询天气、计算数学表达式、搜索知识。"),
            HumanMessage(content="请帮我做三件事：1) 查询上海的天气 2) 计算 123 * 456 3) 介绍一下 LangGraph")
        ]
    })
    print(f"回答: {result['messages'][-1].content}\n")

    print("=" * 50)
    print("追踪数据已发送到 LangSmith")
    print("访问 https://smith.langchain.com 查看详细追踪")
    print("=" * 50)
