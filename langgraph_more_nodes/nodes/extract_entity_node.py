
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph_more_nodes.agent_state import AgentState
from common.llm import my_llm
from api.msg_queue_manager import msg_queue_manager
import json
import re


def extract_entity_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    从用户输入中抽取中医实体
    - 输入：state["input_semantic_trans"]
    - 输出：实体列表更新到 user_input_* 字段
    """
    user_id = config.get("configurable", {}).get("thread_id", "default")

    print("开始从用户输入中抽取中医实体")
    msg_queue_manager.put_msg_content(user_id, "📋 正在提取中医实体...")

    user_input = state.get("input_semantic_trans", "")

    prompt = f"""
用户输入: {user_input}

你是一个实体抽取专家。请从用户输入中抽取以下类型的中医实体：

【实体类型】
- Symptom（症状）：如咳嗽、腹泻、发热、失眠等
- Disease（疾病）：如风寒感冒、脾虚泄泻等
- Formula（方剂）：如桂枝汤、麻黄汤等
- Herb（药材）：如人参、黄芪、当归等
- Effect（功效）：如清热、补气、祛湿、活血等
- Source（出处）：如《伤寒论》《本草纲目》等典籍

【输出要求】
- 以 JSON 格式输出，字段名为：symptoms, diseases, formulas, herbs, effects, sources
- 每个字段是字符串列表
- 如果某类实体不存在，输出空列表
- 不要输出任何解释或其他文字

【输出格式】
```json
{{
    "symptoms": ["症状1", "症状2"],
    "diseases": ["疾病1"],
    "formulas": ["方剂1", "方剂2"],
    "herbs": ["药材1"],
    "effects": ["功效1", "功效2"],
    "sources": ["出处1"]
}}
```
"""

    try:
        response = my_llm.invoke([HumanMessage(content=prompt)])
        model_answer = response.content.strip()

        json_match = re.search(r'\{[\s\S]*\}', model_answer)
        if json_match:
            entities = json.loads(json_match.group())
            state["user_input_symptoms"] = entities.get("symptoms", [])
            state["user_input_diseases"] = entities.get("diseases", [])
            state["user_input_formulas"] = entities.get("formulas", [])
            state["user_input_herbs"] = entities.get("herbs", [])
            state["user_input_effects"] = entities.get("effects", [])
            state["user_input_sources"] = entities.get("sources", [])

            print(f"抽取到 {len(state['user_input_symptoms'])} 个症状")
            print(f"抽取到 {len(state['user_input_diseases'])} 个疾病")
            print(f"抽取到 {len(state['user_input_formulas'])} 个方剂")
            print(f"抽取到 {len(state['user_input_herbs'])} 个药材")
            print(f"抽取到 {len(state['user_input_effects'])} 个功效")
            print(f"抽取到 {len(state['user_input_sources'])} 个出处")
        else:
            print(f"大模型返回格式异常: {model_answer}")
            state["user_input_symptoms"] = []
            state["user_input_diseases"] = []
            state["user_input_formulas"] = []
            state["user_input_herbs"] = []
            state["user_input_effects"] = []
            state["user_input_sources"] = []
    except Exception as e:
        print(f"实体抽取出错: {e}")
        state["user_input_symptoms"] = []
        state["user_input_diseases"] = []
        state["user_input_formulas"] = []
        state["user_input_herbs"] = []
        state["user_input_effects"] = []
        state["user_input_sources"] = []

    return state


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 实体抽取节点测试")
    print("=" * 60)

    test_cases = [
        "我感冒了，有点咳嗽和发热，想问问有什么中药可以治疗？",
        "请问《伤寒论》中记载的桂枝汤有什么功效？",
        "最近失眠，而且感觉气血不足，有什么方剂推荐吗？",
        "今天天气不错，我们去吃饭吧！"
    ]

    for i, user_input in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {user_input}")
        print("=" * 60)

        state: AgentState = {"input": user_input}
        result = extract_entity_node(state)

        print("\n抽取结果:")
        print(f"  症状 (symptoms): {result.get('user_input_symptoms', [])}")
        print(f"  疾病 (diseases): {result.get('user_input_diseases', [])}")
        print(f"  方剂 (formulas): {result.get('user_input_formulas', [])}")
        print(f"  药材 (herbs): {result.get('user_input_herbs', [])}")
        print(f"  功效 (effects): {result.get('user_input_effects', [])}")
        print(f"  出处 (sources): {result.get('user_input_sources', [])}")