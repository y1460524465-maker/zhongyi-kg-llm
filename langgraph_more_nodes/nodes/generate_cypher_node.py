import asyncio
import json

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph_more_nodes.agent_state import AgentState
from common.llm import my_llm
from common.config import Config
from api.msg_queue_manager import msg_queue_manager

conf = Config()


def build_metadata_context(metadata: dict) -> str:
    """构建元数据上下文"""
    context = []

    context.append("【节点标签】")
    for label in metadata.get('node_labels', []):
        context.append(f"- {label['label']}: {label['description']}")

    context.append("\n【关系类型】")
    for rel in metadata.get('relation_types', []):
        context.append(f"- {rel['type']}: {rel['description']}")

    context.append("\n【三元组模式】")
    for triple in metadata.get('triple_patterns', []):
        context.append(f"- {triple['source_label']} -> [{triple['relation_type']}] -> {triple['target_label']}: {triple.get('description', '')}")

    return "\n".join(context)


def generate_cypher_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    根据用户输入、匹配实体和Neo4j元数据生成Cypher查询语句
    - 输入：state["input_semantic_trans"] 和 matched_* 字段
    - 输出：cypher_query 列表
    """
    user_id = config.get("configurable", {}).get("thread_id", "default")

    print("开始生成Cypher查询语句")
    msg_queue_manager.put_msg_content(user_id, "⚙️ 正在生成图数据库查询语句...")

    try:
        #加载元数据
        metadata = json.loads(conf.TCM_METADATA)
        metadata_context = build_metadata_context(metadata)
    except Exception as e:
        print(f"元数据加载失败: {e}")
        state["cypher_query"] = []
        return state

    user_input = state.get("input_semantic_trans", "")

    matched_entities = []
    entity_fields = [
        ("症状", state.get("matched_symptoms", [])),
        ("疾病", state.get("matched_diseases", [])),
        ("方剂", state.get("matched_formulas", [])),
        ("药材", state.get("matched_herbs", [])),
        ("功效", state.get("matched_effects", [])),
        ("出处", state.get("matched_sources", [])),
    ]
    for entity_type, entities in entity_fields:
        if entities:
            matched_entities.append(f"{entity_type}: {', '.join(entities)}")

    matched_str = "\n".join(matched_entities) if matched_entities else "无"

    prompt = f"""
用户输入: {user_input}

匹配到的标准实体:
{matched_str}

Neo4j元数据:
{metadata_context}
[提示] metadata_context 中的description 是Neo4j元数据的的描述信息,不是节点和关系的属性,注意下
【任务要求】
根据用户输入和匹配到的实体，生成1-3条合适的Cypher查询语句。

【生成规则】
1. 优先使用匹配到的标准实体名作为查询条件
2. 选择合适的三元组模式（节点标签 -> 关系 -> 节点标签）
3. 使用MATCH或CALL语句
4. 如果有多种查询角度，生成多条语句
5. 结果用中文别名方便阅读

【输出要求】
- 每条Cypher语句单独一行
- 不要输出任何解释或其他文字
- 直接输出Cypher语句
"""

    try:
        response = my_llm.invoke([HumanMessage(content=prompt)])
        cypher_text = response.content.strip()

        cypher_list = [line.strip() for line in cypher_text.split('\n')
                       if line.strip() and (line.strip().startswith('MATCH') or line.strip().startswith('CALL'))]

        state["cypher_query"] = cypher_list
        print(f"生成了 {len(cypher_list)} 条Cypher语句:")
        for i, cypher in enumerate(cypher_list, 1):
            print(f"  {i}. {cypher}")

    except Exception as e:
        print(f"Cypher生成失败: {e}")
        state["cypher_query"] = []

    return state


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 生成Cypher节点测试")
    print("=" * 60)

    test_cases = [
        {
            "input": "我感冒了，有点咳嗽和发热，应该吃什么药？",
            "matched_symptoms": ["咳嗽", "发热"],
            "matched_diseases": ["感冒"],
            "matched_formulas": [],
            "matched_herbs": [],
            "matched_effects": [],
            "matched_sources": []
        },
        {
            "input": "请问《伤寒论》中记载的桂枝汤有什么功效？",
            "matched_symptoms": [],
            "matched_diseases": [],
            "matched_formulas": ["桂枝汤"],
            "matched_herbs": [],
            "matched_effects": ["清热", "补气"],
            "matched_sources": ["伤寒论"]
        },
    ]

    for i, test_state in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}")
        print("=" * 60)
        print(f"用户输入: {test_state['input']}")
        print(f"匹配实体: 症状={test_state['matched_symptoms']}, 疾病={test_state['matched_diseases']}")

        result = generate_cypher_node(test_state)

        print("\n生成的Cypher语句:")
        for j, cypher in enumerate(result.get('cypher_query', []), 1):
            print(f"  {j}. {cypher}")