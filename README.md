# 中医药知识图谱智能问答系统

基于 **Neo4j 中医药知识图谱** 与 **LangGraph 多节点工作流** 构建的垂直领域智能问答系统。系统理解中医语义，自动检索相关症状、疾病、方剂、药材与功效关系，支持多轮对话与实时流式输出，**每一条结论均可溯源到具体药材、方剂与中医典籍出处**。

---

## 核心特性

| 特性 | 说明 |
|---|---|
| **图谱约束幻觉** | 大模型只负责语义理解与查询生成，事实性答案全部来自 Neo4j 知识图谱，可溯源、可解释 |
| **Text2Cypher 安全闸门** | LLM 生成的 Cypher 先经 `EXPLAIN` 预检，不执行即验证语法；失败自动重试 ≤3 次，超限降级为直连大模型作答 |
| **口语化实体归一** | FAISS + `bge-large-zh-v1.5` 将用户口语（"拉肚子"）映射为标准中医实体（"泄泻"），阈值 0.65 过滤低置信匹配 |
| **全链路流式输出** | FastAPI 流式接口 + `asyncio.Queue`，实时推送「实体抽取 → 图谱检索 → 生成回答」的推理进度 |
| **多用户会话隔离** | 基于 LangGraph `InMemorySaver` + `session_id`，多用户上下文互不串扰 |
| **私有化部署** | 支持 vLLM 本地部署与多 LoRA 适配器按权重融合推理，满足数据不出域要求 |

---

## 系统架构

### 一、数据构建流水线（一次性离线任务）

```
中医药百科网页
  → clawler/        多级爬虫（列表页 → 详情页），产出 2,100+ 篇原始语料
  → extract_information/   LLM 结构化抽取（Pydantic 约束输出严格 JSON）
  → create_information/   Neo4j 幂等入库 + FAISS 向量索引构建
```

### 二、查询时工作流（LangGraph 九节点）

```
用户提问
  → 语义转写（结合最近 5 轮对话，消解指代与省略）
    → 中医意图识别（是否属于中医领域？）
      ├─ 否 → 直连大模型回答
      └─ 是 → 实体抽取（症状/疾病/方剂/药材/功效/出处）
            → FAISS 向量匹配归一（口语 → 标准实体）
            → Cypher 自动生成（注入图谱 Schema 约束）
            → EXPLAIN 语法校验 ──不通过──→ 回退重生成（≤3 次）
              ↓ 通过                       ↓ 超过 3 次
             执行图谱查询 → 结合结果生成回答   降级为直连大模型作答
```

工作流图见 [`langgraph_more_nodes/graph.jpg`](langgraph_more_nodes/graph.jpg)。

---

## 技术栈

| 方向 | 技术 |
|---|---|
| AI 工作流 | LangGraph、LangChain |
| 大语言模型 | DeepSeek（OpenAI 兼容接口）、Qwen2.5 + LoRA 微调 |
| 知识图谱 | Neo4j 5.x、Cypher（含多跳路径查询） |
| 向量检索 | FAISS、Sentence-Transformers、BGE-large-zh-v1.5 |
| 后端框架 | FastAPI、asyncio、StreamingResponse、Pydantic v2 |
| 前端框架 | Streamlit |
| 数据采集 | requests、BeautifulSoup、Playwright |
| 模型部署 | vLLM（支持多 LoRA 适配器融合推理） |
| 可观测性 | LangSmith（节点延迟与 Token 消耗追踪） |

---

## 知识图谱规模

| 指标 | 数量 |
|---|---|
| 原始语料 | 2,100+ 篇（1,460 味中药、712 首方剂） |
| 结构化知识文件 | 2,029 份 JSON |
| 实体 | **17,496 个** |
| 关系 | **20,899 条** |
| 节点类型 | 6 类：疾病、症状、方剂、药材、功效、出处 |
| 关系类型 | 6 类：治疗疾病、缓解症状、具有功效、包含成分、疾病症状、文献出处 |
| 微调语料 | 2,170 条 Alpaca 格式指令样本 |

---

## 项目结构

```
├── common/                        # 公共模块（配置、大模型、图数据库、向量模型）
│   ├── config.py                  # 统一配置读取（.env）
│   ├── llm.py                     # DeepSeek 大模型封装
│   ├── embedding_model.py         # BGE 向量模型（惰性加载）
│   └── neo4j_manager.py           # Neo4j 客户端（惰性连接）
├── clawler/                # 数据采集：中药/方剂列表与详情爬虫
├── extract_information/    # LLM 知识抽取：实体与关系结构化
├── create_information/    # 图谱构建：Neo4j 导入 + FAISS 索引
├── langgraph_more_nodes/   # LangGraph 工作流与九个节点实现
├── api/                 # FastAPI 后端（同步 + 流式双接口）
├── webui/               # Streamlit 前端
├── fine_tune/              # vLLM 推理客户端（含多 LoRA 融合）
└── demo/                   # 各技术栈的独立验证 Demo
```

---

## 快速开始

### 1. 环境要求

- Python 3.10+
- Neo4j 5.x（本地或远程）
- 本地 BGE 向量模型（`bge-large-zh-v1.5`）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

在 `common/` 下新建 `.env`（该文件已被 `.gitignore` 忽略，不会入库）：

```env
# 大模型
MODEL_API_KEY=your_api_key
MODEL_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# 向量模型（必须指向本地 BGE 模型目录）
EMBEDDING_MODEL_PATH=/path/to/bge-large-zh-v1.5

# 以下均为可选
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
FAISS_INDEX_PATH=
FAISS_ID2TEXT_PATH=
VLLM_BASE_URL=http://localhost:8000/v1
VLLM_MODEL_NAME=
```

### 4. 构建知识图谱（可选）

仓库已包含抽取后的结构化 JSON，如需从零重建：

```bash
python clawler/zhongyao_crawler.py          # 采集语料
python extract_information/01_tcm_kg_extract_info.py   # LLM 知识抽取
python create_information/import_tcm_data.py          # 导入 Neo4j
python create_information/faiss_embedding.py   # 构建向量索引
```

FAISS 索引默认读取 `create_information/` 下的文件，
也可通过环境变量 `FAISS_INDEX_PATH` / `FAISS_ID2TEXT_PATH` 指定其他位置。

> Windows 提示：FAISS 在包含非 ASCII 字符的路径下可能崩溃。若遇到该问题，请把索引文件放到纯英文路径，并用上述环境变量指向它。

### 5. 启动服务

```bash
# 后端（端口 8000）
python api/main.py

# 前端 - 流式版（端口 8501）
streamlit run webui/app_stream.py
```

打开 http://localhost:8501 即可使用。也可直接运行 `webui/start_app.bat` 一键启动前后端。

### 6. 接口说明

| 接口 | 方法 | 说明 |
|---|---|---|
| `/` | GET | 健康检查 |
| `/process` | POST | 同步问答，返回 `{"input": ..., "output": ...}` |
| `/process_stream` | POST | 流式问答，SSE 返回进度与最终答案 |

请求示例：

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"input": "拉肚子该吃什么中药？", "session_id": "user-001"}'
```

---

## 核心设计说明

**为什么用图数据库而不是纯向量检索？**
中医知识强关联、需要多跳推理。例如"感冒咳嗽发热该用什么方剂"，需要同时命中疾病、症状、方剂、成分、功效多个节点。向量检索只能召回相似文本片段，无法完成结构化关联推理；而图查询天然支持多跳遍历，且结果可精确溯源。

**为什么大模型生成的查询还要预检？**
把大模型接入数据库存在风险：模型可能生成语法错误甚至危险语句。因此所有生成的 Cypher 先经 Neo4j `EXPLAIN` 预检——不执行、不落库即可验证合法性，非法语句回退重生成，超过 3 次则降级为直连大模型作答，保证系统永不因查询失败而卡死。

**FAISS 在这里的作用是什么？**
它不是用来召回文本片段的，而是做**实体链接**：把用户的口语表达映射到图谱里的标准节点名（"拉肚子" → "泄泻"），是图谱检索之前的关键一步，直接决定召回率。

---

## 已知限制

- 知识图谱为 **Schema 驱动**，需要预先定义本体；扩展到新领域需替换本体定义与抽取提示词。
- 目前仅对**图谱中已有的节点名**建立向量索引，本体外的长尾问题会回退到直连大模型作答。
- 未实现社区摘要与全局检索，暂不支持"整体综述型"问题。

---

## 免责声明

本项目为技术学习与研究用途。系统输出仅为中医药知识参考，**不构成任何诊疗建议**，实际用药请遵医嘱。
