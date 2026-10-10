# LangGraph 节点生成提示词模板

## 使用说明
使用 `{三引号}` 中的内容作为系统提示词模板，每次只需替换 `{业务描述}` 部分即可。

## 系统提示词模板

```
你是一位 LangGraph 开发专家，负责为 {系统名称} 编写工作流节点代码。

## 固定信息（不变）
1. **状态类**: AgentState (TypedDict) - 定义在 langgraph_more_nodes/agent_state.py
2. **LLM调用**: common.llm.my_llm.invoke([HumanMessage(content=...)])
3. **消息格式**: from langchain_core.messages import HumanMessage

## 公共工具类（common 目录）
- **common.config.Config**: 配置管理，获取环境变量
- **common.llm.my_llm**: 封装好的大模型实例
- **common.neo4j_manager.Neo4jClient / neo4j_client**: Neo4j 数据库客户端
- **common.embedding_model.embedding_model**: 文本嵌入模型
- **common.path_utils.get_file_path**: 文件路径解析工具

## 当前任务
{业务描述}

## 代码规范
1. 函数签名: def node_name(state: AgentState) -> AgentState:
2. 输入: state["input"] 获取用户输入
3. 输出: 返回更新后的 state 字典
4. 必须字段: 在 state 中设置对应的结果字段
5. 日志: 添加 print 语句输出处理进度
6. 防御: 对异常情况做兜底处理

## 通用防御代码（必须包含）
try:
    # 业务逻辑
except Exception as e:
    print(f"处理出错: {e}")
    # 设置合理的默认值

请生成完整的 Python 代码。
```

---

## AgentState 完整字段说明

```python
class AgentState(TypedDict):
    # 输入
    input: str  # 用户原始输入

    # 中医意图识别
    is_zhongyi_intent: bool  # 是否与中医相关

    # 直接回答（非中医问题）
    direct_out: str

    # 用户输入的实体抽取（从用户输入中抽取）
    user_input_symptoms: List[str]
    user_input_diseases: List[str]
    user_input_formulas: List[str]
    user_input_herbs: List[str]
    user_input_effects: List[str]
    user_input_sources: List[str]

    # 匹配的实体（通过FAISS匹配到的标准实体）
    matched_symptoms: List[str]
    matched_diseases: List[str]
    matched_formulas: List[str]
    matched_herbs: List[str]
    matched_effects: List[str]
    matched_sources: List[str]

    # Cypher查询
    cypher_query: List[str]  # 生成的Cypher语句
    is_all_validate_cypher: bool  # Cypher是否合法
    cypher_results: List[Any]  # Cypher执行结果

    # 输出
    neo4j_answer: str  # Neo4j查询生成的回答
    output: str  # 最终输出
```

---

## 已实现节点示例

### 节点1：中医意图识别 (zhongyi_intent_node)

**业务描述**：
```
判断用户输入是否与中医相关
- 知识图谱范围：中药、方剂、症状、疾病、功效、典籍等
- 输出：是/否
- 字段：is_zhongyi_intent: bool
```

**完整代码**：
```python
from agent_state import AgentState
from langchain_core.messages import HumanMessage
from common.llm import my_llm


def zhongyi_intent_node(state: AgentState) -> AgentState:
    """
    判断用户输入是否与中医相关
    - 知识图谱范围：中药、方剂、症状、疾病、功效、典籍等
    - 输出：是/否
    - 字段：is_zhongyi_intent: bool
    """
    print("开始判断用户输入是否与中医相关")
    user_input = state.get("input", "")

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
```

---

### 节点2：直接大模型输出 (llm_direct_out_node)

**业务描述**：
```
当用户问题不涉及中医时，直接调用大模型生成回答
- 输入：state["input"]
- 输出：state["direct_out"], state["output"]
```



---

### 节点3：实体抽取 (extract_entity_node)

**业务描述**：
```
从用户输入中抽取中医实体
- 实体类型：Symptom、Disease、Formula、Herb、Effect、Source
- 输出：实体列表更新到 user_input_* 字段
```

---

### 节点4：实体匹配 (match_entity_node)

**业务描述**：
```
从FAISS向量数据库匹配标准实体名
- 输入：从 user_input_* 字段获取实体列表
- 输出：匹配结果写入 matched_* 字段
- 参数：similarity_threshold 相似度阈值，默认0.8
```



---

### 节点5：生成Cypher (generate_cypher_node)

**业务描述**：
```
根据用户输入、匹配实体和Neo4j元数据生成Cypher查询语句
- 输入：state["input"] 和 matched_* 字段
- 输出：cypher_query 列表
```



---

### 节点6：检查Cypher (check_cypher_node)

**业务描述**：
```
检查Cypher语句是否合法
- 输入：state["cypher_query"]
- 输出：state["is_all_validate_cypher"]
```



---

### 节点7：执行Cypher (run_cypher_node)

**业务描述**：
```
执行Cypher查询语句
- 输入：state["cypher_query"]
- 输出：state["cypher_results"]
```



---

### 节点8：生成回答 (generate_answer_node)

**业务描述**：
```
根据用户输入和Cypher查询结果生成最终回答
- 输入：state["input"], state["cypher_results"]
- 输出：state["neo4j_answer"], state["output"]
```



---

## 完整工作流

```
START
  │
  ▼
┌──────────────────┐
│  中医意图识别     │
│ zhongyi_intent   │
└────────┬─────────┘
         │
    ┌────┴────┐
    │ 条件分支 │
    └────┬────┘
    是   │   否
    ▼    │    ▼
┌──────────┐  ┌────────────────┐
│ 实体抽取 │  │ 直接大模型输出 │
│ extract  │  │ llm_direct_out│
└────┬─────┘  └───────┬────────┘
     │                 │
     ▼                 ▼
┌──────────┐      END
│ 实体匹配 │
│  match   │
└────┬─────┘
     │
     ▼
┌──────────┐
│生成Cypher│
│generate  │
└────┬─────┘
     │
     ▼
┌──────────┐
│检查Cypher │
│  check   │
└────┬─────┘
     │
  ┌──┴──┐
  │条件  │
  └──┬──┘
 合法 │ 不合法
  ▼    │
┌────┐ │
│执行│ │  ┌────────────────┐
│run │ └►│ 直接大模型输出 │
└─┬──┘   │ llm_direct_out │
  │      └───────┬────────┘
  ▼              │
┌──────────┐     │
│生成回答  │     │
│generate  │     │
│ _answer  │     │
└────┬─────┘     │
     │            │
     ▼            ▼
    END         END
```

---

## 文件清单

| 文件名 | 节点名称 | 功能 |
|--------|---------|------|
| `agent_state.py` | - | AgentState 状态定义 |
| `zhongyi_intent_node.py` | zhongyi_intent_node | 判断是否中医相关 |
| `llm_direct_out_node.py` | llm_direct_out_node | 非中医问题直接回答 |
| `extract_entity_node.py` | extract_entity_node | 从用户输入抽取实体 |
| `match_entity_from_neo4j_node.py` | match_entity_node | FAISS向量匹配标准实体 |
| `generate_neo4j_cypher_node.py` | generate_cypher_node | 生成Cypher查询语句 |
| `check_cypher_node.py` | check_cypher_node | 验证Cypher语法 |
| `run_cypher_node.py` | run_cypher_node | 执行Cypher查询 |
| `neo4j_answer_generate_node.py` | generate_answer_node | 生成最终回答 |
| `full_workflow.py` | - | 完整工作流串接 |