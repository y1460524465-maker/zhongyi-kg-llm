"""
LangGraph 节点生成约定：
- LLM调用: common.llm.my_llm.invoke([HumanMessage(content=...)])
- 消息格式: from langchain_core.messages import HumanMessage
- 函数签名: def node_name(state: AgentState) -> AgentState:
- 输入: state["input"] 获取用户输入
- 日志: 添加 print 语句输出处理进度
"""

from typing import TypedDict, List, Any


class AgentState(TypedDict):
    # 输入
    input: str
    # 是否跟中医有关系
    is_zhongyi_intent: bool

    # 直接回答
    direct_out: str

    # 用户输入的实体抽取
    user_input_effects: List[str]
    user_input_diseases: List[str]
    user_input_symptoms: List[str]
    user_input_formulas: List[str]
    user_input_herbs: List[str]
    user_input_sources: List[str]

    # 匹配的实体
    matched_effects: List[str]
    matched_diseases: List[str]
    matched_symptoms: List[str]
    matched_formulas: List[str]
    matched_herbs: List[str]
    matched_sources: List[str]

    # cypher查询语句
    cypher_query: List[str]
    # cypher语句是否合法
    is_all_validate_cypher: bool
    # cypher语句的执行结果
    cypher_results: List[Any]

    neo4j_answer: str
    # 输出
    output: str

    # 历史数据
    history_messages: List[dict]
    # 语义转写
    input_semantic_trans: str