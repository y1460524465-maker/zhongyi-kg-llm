
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph_more_nodes.agent_state import AgentState
from common.llm import my_llm
from api.msg_queue_manager import msg_queue_manager


def zhongyi_intent_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    判断用户输入是否与中医相关
    - 输入：state["input_semantic_trans"]
    - 输出：state["is_zhongyi_intent"]
    """
    user_id = config.get("configurable", {}).get("thread_id", "default")

    print("开始判断用户输入是否与中医相关")
    msg_queue_manager.put_msg_content(user_id, "🔍 正在判断问题类型...")

    user_input = state.get("input_semantic_trans", "")

    prompt = f"""
用户输入: {user_input}

你是一个意图分类器。请判断该输入是否与中医相关。

【中医知识图谱范围】
- 中药、方剂、症状、疾病、功效、典籍等

【判断规则】
- 如果涉及中医相关内容，输出"是"
- 如果与中医无关，输出"否"

【输出要求】
- 只能输出"是"或"否"，不要输出任何解释或其他文字。
"""

    try:
        response = my_llm.invoke([HumanMessage(content=prompt)])
        model_answer = response.content.strip()

        if model_answer == "是":
            state["is_zhongyi_intent"] = True
        elif model_answer == "否":
            state["is_zhongyi_intent"] = False
        else:
            state["is_zhongyi_intent"] = False
            print(f"大模型返回异常结果: {model_answer}，默认设置为否")
    except Exception as e:
        print(f"判断出错: {e}")
        state["is_zhongyi_intent"] = False

    print(f"判断结果: {'是' if state['is_zhongyi_intent'] else '否'}")
    return state


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 中医意图识别节点测试")
    print("=" * 60)

    test_cases = [
        "我感冒了，有点咳嗽和发热，应该吃什么药？",
        "请问《伤寒论》中记载的桂枝汤有什么功效？",
        "今天天气怎么样？",
        "人参的性味归经是什么？",
        "如何编程Python？"
    ]

    for i, user_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {user_input}")
        print("=" * 60)

        state: AgentState = {"input": user_input}
        result = zhongyi_intent_node(state)

        print(f"\n最终结果: is_zhongyi_intent = {result['is_zhongyi_intent']}")