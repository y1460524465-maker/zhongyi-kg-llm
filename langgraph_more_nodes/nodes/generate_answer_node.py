
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph_more_nodes.agent_state import AgentState
from common.llm import my_llm
from api.msg_queue_manager import msg_queue_manager


def format_cypher_results(results: list) -> str:
    """格式化Cypher查询结果为可读文本"""
    if not results:
        return "暂无查询结果"

    formatted = []
    for i, record in enumerate(results, 1):
        formatted.append(f"{i}. {record}")
    return "\n".join(formatted)


def generate_answer_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    根据用户输入和Cypher查询结果生成最终回答
    - 输入：state["input_semantic_trans"], state["cypher_results"]
    - 输出：state["neo4j_answer"], state["output"]
    """
    user_id = config.get("configurable", {}).get("thread_id", "default")

    print("开始生成最终回答")
    msg_queue_manager.put_msg_content(user_id, "📝 正在生成最终回答...")

    user_input = state.get("input_semantic_trans", "")
    cypher_results = state.get("cypher_results", [])

    results_text = format_cypher_results(cypher_results)

    prompt = f"""
用户问题: {user_input}

知识图谱查询结果:
{results_text}

【任务要求】
根据用户问题和查询结果，生成一个完整、友好的回答。

【回答要求】
1. 直接回答用户的问题
2. 如果查询结果为空，说明无法从知识图谱中找到相关信息
3. 使用清晰的中文表述
4. 可以适当总结和整理查询结果
5. 如果有多个相关信息，可以分点说明

【输出格式】
直接输出回答内容，不要额外解释。
"""

    try:
        response = my_llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

        state["neo4j_answer"] = answer
        state["output"] = answer

        print(f"✅ 回答生成成功，长度: {len(answer)} 字符")
        print(f"\n回答内容:\n{answer}")

    except Exception as e:
        error_msg = f"生成回答失败: {str(e)}"
        print(f"❌ {error_msg}")
        state["neo4j_answer"] = error_msg
        state["output"] = "抱歉，生成回答时出现问题。"
    history_messages = state.get("history_messages", [])
    history_messages.append({"role": "assistant", "content": state["output"].strip()})
    state["history_messages"] = history_messages

    msg_queue_manager.put_reply_content(user_id, state["output"])
    msg_queue_manager.put_done_content(user_id)
    return state


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 生成回答节点测试")
    print("=" * 60)

    test_cases = [
        {
            "input": "我感冒了，有点咳嗽和发热，应该吃什么药？",
            "cypher_results": [
                {"疾病": "感冒", "症状": ["咳嗽", "发热", "恶寒"]},
                {"中药": "麻黄", "功效": "发汗解表"},
                {"方剂": "桂枝汤", "功效": "解表散寒"}
            ]
        },
        {
            "input": "人参的性味归经是什么？",
            "cypher_results": [
                {"中药": "人参", "性味归经": "甘温，归脾肺经", "功效": "大补元气"}
            ]
        },
        {
            "input": "测试问题",
            "cypher_results": []
        },
    ]

    for i, test_state in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}")
        print("=" * 60)
        print(f"用户输入: {test_state['input']}")

        result = generate_answer_node(test_state)

        print(f"\n生成的回答:")
        print(f"  neo4j_answer: {result.get('neo4j_answer', '')}")
        print(f"  output: {result.get('output', '')}")