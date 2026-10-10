from typing import TypedDict, List, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langgraph_more_nodes.agent_state import AgentState

# 导入nodes目录中的所有节点
from langgraph_more_nodes.nodes.zhongyi_intent_node import zhongyi_intent_node
from langgraph_more_nodes.nodes.llm_direct_out_node import llm_direct_out_node
from langgraph_more_nodes.nodes.extract_entity_node import extract_entity_node
from langgraph_more_nodes.nodes.match_entity_node import match_entity_node
from langgraph_more_nodes.nodes.generate_cypher_node import generate_cypher_node
from langgraph_more_nodes.nodes.check_cypher_node import check_cypher_node
from langgraph_more_nodes.nodes.run_cypher_node import run_cypher_node
from langgraph_more_nodes.nodes.generate_answer_node import generate_answer_node
from langgraph_more_nodes.nodes.semantic_transcription_node import semantic_transcription_node


def should_use_knowledge_graph(state: AgentState) -> str:
    """
    判断是否使用知识图谱
    - 如果 is_zhongyi_intent 为 True → 走知识图谱路径
    - 否则 → 直接大模型输出
    """
    is_zhongyi = state.get("is_zhongyi_intent", False)
    if is_zhongyi:
        print(f"判定为中医相关，使用知识图谱")
        return "extract_entity"
    else:
        print(f"判定为非中医相关，直接大模型输出")
        return "llm_direct_out"


def check_cypher_result(state: AgentState) -> str:
    """
    检查Cypher是否合法
    - 如果合法 → 执行查询
    - 如果不合法 → 返回重新生成Cypher（最多重试3次）
    """
    is_valid = state.get("is_all_validate_cypher", False)
    retry_count = state.get("_cypher_retry_count", 0)
    
    if is_valid:
        print(f"Cypher合法，执行查询")
        return "run_cypher"
    else:
        if retry_count < 3:
            print(f"Cypher不合法，重新生成（第{retry_count+1}次尝试）")
            state["_cypher_retry_count"] = retry_count + 1
            return "generate_cypher"
        else:
            print(f"Cypher生成失败超过3次，直接大模型输出")
            return "llm_direct_out"


def build_graph() -> StateGraph:
    """构建LangGraph工作流"""
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("semantic_transcription", semantic_transcription_node)
    graph.add_node("zhongyi_intent", zhongyi_intent_node)
    graph.add_node("llm_direct_out", llm_direct_out_node)
    graph.add_node("extract_entity", extract_entity_node)
    graph.add_node("match_entity", match_entity_node)
    graph.add_node("generate_cypher", generate_cypher_node)
    graph.add_node("check_cypher", check_cypher_node)
    graph.add_node("run_cypher", run_cypher_node)
    graph.add_node("generate_answer", generate_answer_node)

    # 添加边
    graph.add_edge(START, "semantic_transcription")
    graph.add_edge("semantic_transcription", "zhongyi_intent")

    # 条件分支：意图识别后
    graph.add_conditional_edges(
        "zhongyi_intent",
        should_use_knowledge_graph,
        {
            "extract_entity": "extract_entity",
            "llm_direct_out": "llm_direct_out"
        }
    )

    # 知识图谱路径
    graph.add_edge("extract_entity", "match_entity")
    graph.add_edge("match_entity", "generate_cypher")
    graph.add_edge("generate_cypher", "check_cypher")

    # 条件分支：Cypher检查后（支持循环重试）
    graph.add_conditional_edges(
        "check_cypher",
        check_cypher_result,
        {
            "run_cypher": "run_cypher",
            "generate_cypher": "generate_cypher",
            "llm_direct_out": "llm_direct_out"
        }
    )

    graph.add_edge("run_cypher", "generate_answer")
    graph.add_edge("generate_answer", END)
    graph.add_edge("llm_direct_out", END)

    return graph


def run_workflow(user_input: str) -> dict:
    """
    运行完整工作流
    :param user_input: 用户输入
    :return: 最终状态
    """
    print("=" * 80)
    print("中医知识图谱问答系统 - LangGraph工作流")
    print("=" * 80)
    print(f"用户输入: {user_input}")
    print()

    # 构建图
    graph = build_graph()
    app = graph.compile()

    # 初始状态
    initial_state: AgentState = {
        "input": user_input,
        "input_semantic_trans": "",
        "is_zhongyi_intent": False,
        "user_input_symptoms": [],
        "user_input_diseases": [],
        "user_input_formulas": [],
        "user_input_herbs": [],
        "user_input_effects": [],
        "user_input_sources": [],
        "matched_symptoms": [],
        "matched_diseases": [],
        "matched_formulas": [],
        "matched_herbs": [],
        "matched_effects": [],
        "matched_sources": [],
        "cypher_query": [],
        "is_all_validate_cypher": False,
        "cypher_results": [],
        "neo4j_answer": "",
        "output": "",
        "direct_out": "",
        "_cypher_retry_count": 0  # 内部计数，用于重试
    }

    # 运行
    result = app.invoke(initial_state)

    print("\n" + "=" * 80)
    print("最终输出:")
    print("=" * 80)
    print(result.get("output", ""))

    return result


if __name__ == '__main__':
    print("=" * 80)
    print("🧪 完整工作流测试")
    print("=" * 80)

    test_cases = [
        "我感冒了，有点咳嗽和发热，应该吃什么药？",
        # "请问《伤寒论》中记载的桂枝汤有什么功效？",
        "今天天气怎么样？",
        # "人参的性味归经是什么？",
        # "如何编程Python？"
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试 {i}: {test_input}")
        print("=" * 80)

        try:
            result = run_workflow(test_input)
        except Exception as e:
            print(f"❌ 执行出错: {e}")
            import traceback
            traceback.print_exc()