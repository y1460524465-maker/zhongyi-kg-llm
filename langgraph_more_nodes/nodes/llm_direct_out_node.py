
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph_more_nodes.agent_state import AgentState
from common.llm import my_llm
from api.msg_queue_manager import msg_queue_manager


def llm_direct_out_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    当用户问题不涉及中医时，直接调用大模型生成回答
    - 输入：state["input_semantic_trans"]
    - 输出：state["direct_out"], state["output"]
    """
    user_id = config.get("configurable", {}).get("thread_id", "default")

    print("开始生成直接用户回答")
    msg_queue_manager.put_msg_content(user_id, "💬 正在生成回答...")

    user_input = state.get("input_semantic_trans", "")

    prompt = f"""
用户输入: {user_input}

你是一名专业的中医知识助手，回答时请尽量基于中医理论和术语来解释。
要求：
- 优先从中医角度（如症状、方剂、中药材、功效、经络、辨证论治、典籍等）进行回答。
- 如果问题与中医无关，请直接给出简洁的常规回答，不要强行套用中医。
- 回答要准确、简洁，避免无关内容。
- 输出时只给出最终答案，不要解释你是如何推理的。
"""

    try:
        response = my_llm.invoke([HumanMessage(content=prompt)])
        model_answer = response.content.strip()

        state["direct_out"] = model_answer
        state["output"] = model_answer
        print("✅ 完成生成直接用户回答")
    except Exception as e:
        print(f"❌ 生成回答出错: {e}")
        state["direct_out"] = "抱歉，处理您的请求时出现问题。"
        state["output"] = "抱歉，处理您的请求时出现问题。"

    history_messages = state.get("history_messages", [])
    history_messages.append({"role": "assistant", "content": state["output"]})
    state["history_messages"] = history_messages

    msg_queue_manager.put_reply_content(user_id, state["output"])
    msg_queue_manager.put_done_content(user_id)
    return state


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 直接大模型输出节点测试")
    print("=" * 60)

    test_cases = [
        "我感冒了，有点咳嗽和发热，应该吃什么药？",
        "请问《伤寒论》中记载的桂枝汤有什么功效？",
        "今天天气怎么样？",
        "如何编程Python？",
        "人参的性味归经是什么？"
    ]

    for i, user_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {user_input}")
        print("=" * 60)

        state: AgentState = {"input": user_input}
        result = llm_direct_out_node(state)

        print(f"\n生成的回答:")
        print(f"  output: {result.get('output', '')}")