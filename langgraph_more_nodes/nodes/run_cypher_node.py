from langchain_core.runnables import RunnableConfig
from langgraph_more_nodes.agent_state import AgentState
from common.neo4j_manager import neo4j_client
from api.msg_queue_manager import msg_queue_manager


def run_cypher_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    执行Cypher查询语句
    - 输入：state["cypher_query"]
    - 输出：state["cypher_results"]
    """
    user_id = config.get("configurable", {}).get("thread_id", "default")

    print("开始执行Cypher查询")
    msg_queue_manager.put_msg_content(user_id, "🗄️ 正在查询知识图谱...")

    cypher_list = state.get("cypher_query", [])

    if not cypher_list:
        print("  无Cypher语句需要执行")
        state["cypher_results"] = []
        return state

    print(f"  共有 {len(cypher_list)} 条Cypher语句需要执行")

    all_results = []

    for i, cypher in enumerate(cypher_list, 1):
        print(f"  执行语句 {i}: {cypher[:60]}...")
        try:
            result = neo4j_client.run_cypher(cypher)
            records = [record.data() for record in result]
            all_results.extend(records)
            print(f"    ✅ 成功，返回 {len(records)} 条记录")
        except Exception as e:
            error_msg = str(e)
            print(f"    ❌ 执行失败: {error_msg[:80]}")

    state["cypher_results"] = all_results
    print(f"\n执行完成: 共返回 {len(all_results)} 条记录")

    return state


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 执行Cypher节点测试")
    print("=" * 60)

    test_cases = [
        {
            "cypher_query": [
                "MATCH (d:Disease {name: '感冒'})-[:HAS_SYMPTOM]->(s:Symptom) RETURN d.name AS 疾病, collect(s.name) AS 症状 LIMIT 5",
                "MATCH (h:Herb)-[:HAS_EFFECT]->(e:Effect) RETURN h.name AS 中药, e.name AS 功效 LIMIT 5"
            ]
        },
        {
            "cypher_query": []
        },
    ]

    for i, test_state in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}")
        print("=" * 60)

        result = run_cypher_node(test_state)

        print("\n查询结果:")
        for j, record in enumerate(result.get("cypher_results", [])[:5], 1):
            print(f"  {j}. {record}")