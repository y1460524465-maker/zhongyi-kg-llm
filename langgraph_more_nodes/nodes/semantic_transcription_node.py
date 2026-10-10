import asyncio

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph_more_nodes.agent_state import AgentState
from common.llm import my_llm
from common.config import Config
from api.msg_queue_manager import msg_queue_manager

conf = Config()


def semantic_transcription_node(state: AgentState, config: RunnableConfig) -> AgentState:
    user_id = config.get("configurable", {}).get("thread_id", "default")

    print("开始生成语义转写...")
    msg_queue_manager.put_msg_content(user_id, "🔄 正在理解您的问题...")

    user_input = state["input"]
    history_messages = state.get("history_messages", [])
    history_context = history_messages[-(conf.history_num):]
    history_messages.append({"role": "user", "content": user_input})
    state["history_messages"] = history_messages

    prompt = f"""
你是一名语言理解专家，负责将用户输入转写为清晰、简洁、语义明确的问题或意图表达。
你需要基于以下上下文（最近6轮对话），分析用户真正想表达的意思。
请不要编造不存在的信息，也不要直接回答问题，只需输出语义转写后的句子。

【历史对话】
{history_context}

【当前用户输入】
{user_input}

请输出：
1. 一句自然语言，清楚表达用户当前真正的问题或意图；
2. 不要包含解释性文字；
3. 如果用户输入含糊不清，请基于上下文合理补全语义；
4. 输出格式：直接输出转写结果，无需加前缀。
"""

    response = my_llm.invoke([HumanMessage(content=prompt)])
    result = response.content.strip()

    state["input_semantic_trans"] = result
    print(f"完成生成语义转写：{result}")
    return state
