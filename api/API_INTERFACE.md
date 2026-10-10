# 中医知识图谱问答系统 - API接口文档

## 📖 项目简介

基于FastAPI和LangGraph的中医知识图谱智能问答系统，提供RESTful API接口服务。

**技术栈：**
- FastAPI - 高性能Web框架
- LangGraph - 工作流编排
- Neo4j - 图数据库
- FAISS - 向量相似度搜索
- LLM - 大语言模型

---

## 🚀 快速开始

### 1. 启动服务

```bash
cd api
python main.py
```

或使用启动脚本：
```bash
# Windows
start_server.bat
```

### 2. 访问地址

- **API基础地址**: `http://localhost:8000`
- **交互式文档**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc文档**: `http://localhost:8000/redoc`

---

## 📡 API接口列表

### 1. 健康检查接口

**接口地址**: `GET /`

**功能描述**: 检查服务是否正常运行

**请求参数**: 无

**响应示例**:
```json
{
  "status": "ok",
  "message": "中医知识图谱问答系统服务运行正常"
}
```

**状态码**:
- `200` - 服务正常

---

### 2. 中医问答接口（核心接口）

**接口地址**: `POST /process`

**功能描述**: 接收用户问题，返回中医知识图谱的智能回答

**Content-Type**: `application/json`

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| input | string | 是 | 用户输入的问题 |

#### 请求示例

```json
{
  "input": "人参有什么功效？"
}
```

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| input | string | 用户原始输入 |
| output | string | 系统生成的回答 |

#### 响应示例

**成功响应**:
```json
{
  "input": "人参有什么功效？",
  "output": "人参具有大补元气、复脉固脱、补脾益肺、生津养血、安神益智等功效。适用于体虚欲脱、肢冷脉微、脾虚食少、肺虚喘咳等症状。"
}
```

**错误响应**:
```json
{
  "input": "",
  "output": "系统出错了，请重试！"
}
```

#### 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 500 | 服务器内部错误 |

#### cURL示例

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"input": "感冒了吃什么药？"}'
```

#### Python示例

```python
import requests

url = "http://localhost:8000/process"
data = {"input": "人参有什么功效？"}

response = requests.post(url, json=data)
result = response.json()

print(f"问题: {result['input']}")
print(f"回答: {result['output']}")
```

#### JavaScript示例

```javascript
fetch('http://localhost:8000/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    input: '人参有什么功效？'
  })
})
.then(response => response.json())
.then(data => {
  console.log('问题:', data.input);
  console.log('回答:', data.output);
})
.catch(error => {
  console.error('Error:', error);
});
```

---

### 3. 静态资源访问

**接口地址**: `GET /picture/{filename}`

**功能描述**: 访问静态图片资源

**路径参数**:
- `filename`: 图片文件名

**示例**:
```
http://localhost:8000/picture/graph.jpg
```

**配置说明**:
静态文件目录通过 `app.mount("/picture", StaticFiles(directory=...))` 挂载

---

## 🔄 工作流程

当用户通过 `/process` 接口提交问题时，系统会执行以下流程：

```
用户输入
  ↓
意图识别（判断是否中医相关）
  ↓
├─ 非中医问题 → 直接LLM回答
└─ 中医问题
     ↓
  实体抽取（症状、疾病、方剂、药材等）
     ↓
  FAISS向量匹配（标准化实体名称）
     ↓
  生成Cypher查询语句
     ↓
  验证Cypher语法
     ↓
  执行Neo4j图数据库查询
     ↓
  生成自然语言回答
     ↓
  返回结果
```

---

## 💡 使用示例

### 示例1: 中药查询

**请求**:
```json
{
  "input": "人参的性味归经是什么？"
}
```

**响应**:
```json
{
  "input": "人参的性味归经是什么？",
  "output": "人参性温，味甘、微苦，归脾、肺、心经。"
}
```

### 示例2: 方剂查询

**请求**:
```json
{
  "input": "桂枝汤的组成和功效是什么？"
}
```

**响应**:
```json
{
  "input": "桂枝汤的组成和功效是什么？",
  "output": "桂枝汤由桂枝、芍药、甘草、生姜、大枣组成。具有解肌发表、调和营卫的功效，主治外感风寒表虚证。"
}
```

### 示例3: 症状咨询

**请求**:
```json
{
  "input": "我感冒了，有点咳嗽和发热，应该吃什么药？"
}
```

**响应**:
```json
{
  "input": "我感冒了，有点咳嗽和发热，应该吃什么药？",
  "output": "根据您的症状（感冒、咳嗽、发热），建议可以考虑以下方剂：银翘散、桑菊饮等。但请注意，具体用药需要结合您的体质和病情，建议咨询专业中医师。"
}
```

### 示例4: 非中医问题

**请求**:
```json
{
  "input": "今天天气怎么样？"
}
```

**响应**:
```json
{
  "input": "今天天气怎么样？",
  "output": "抱歉，我无法提供天气信息。我是一个中医知识图谱问答系统，主要回答中医药相关的问题，如中药、方剂、症状、疾病等。如果您有中医方面的问题，欢迎提问！"
}
```

---

## ⚙️ 配置说明

### 环境变量配置

在 `common/.env` 文件中配置以下参数：

```env
# 大模型配置
MODEL_API_KEY=your_api_key
MODEL_BASE_URL=https://api.example.com
MODEL_NAME=gpt-3.5-turbo

# Neo4j数据库配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Embedding模型配置
EMBEDDING_MODEL_PATH=./bge-large-zh-v1.5
```

### FAISS索引路径

FAISS索引文件路径配置在以下文件中：

- `langgraph_more_nodes/nodes/match_entity_node.py`
- `create_information/faiss_embedding.py`

**注意**: 由于FAISS库在Windows中文路径下的兼容性问题，建议使用英文路径存储FAISS索引文件。

```python
from common.config import Config

conf = Config()
index_path = conf.FAISS_INDEX_PATH      # 默认 create_information/nero4j_embedding_faiss.index
id2text_path = conf.FAISS_ID2TEXT_PATH  # 默认 create_information/nero4j_embedding_faiss_id2text.pkl
```

---

## 🔧 开发指南

### 项目结构

```
api/
├── main.py                 # FastAPI主程序
├── start_server.bat        # Windows启动脚本
├── test_api.py            # API测试脚本
├── quick_test.py          # 快速诊断脚本
├── README.md              # 使用说明
└── API_INTERFACE.md       # API接口文档（本文件）

langgraph_more_nodes/
├── full_workflow.py       # LangGraph工作流
├── agent_state.py         # Agent状态定义
└── nodes/                 # 各个处理节点
    ├── zhongyi_intent_node.py      # 意图识别
    ├── extract_entity_node.py      # 实体抽取
    ├── match_entity_node.py        # 实体匹配
    ├── generate_cypher_node.py     # Cypher生成
    ├── check_cypher_node.py        # Cypher验证
    ├── run_cypher_node.py          # Cypher执行
    └── generate_answer_node.py     # 答案生成
```

### 添加新接口

在 `main.py` 中添加新的路由：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    input: str
    max_retries: int = 3

@app.post("/api/custom")
async def custom_endpoint(request: QueryRequest):
    # 你的业务逻辑
    result = process_query(request.input)
    return {"result": result}
```

### 错误处理

系统会自动捕获异常并返回友好的错误信息：

```python
try:
    data = await request.json()
    input_text = data.get("input", "")
    output = await zhongyi_response(input_text)
    result = {
        "input": input_text,
        "output": output
    }
except Exception as e:
    import traceback
    traceback.print_exc()
    result = {
        "input": "",
        "output": "系统出错了，请重试！"
    }
```

---

## 📊 性能优化

### 1. 超时设置

对于长时间运行的查询，建议在客户端设置合理的超时时间：

```python
# Python requests示例
response = requests.post(url, json=data, timeout=120)  # 120秒超时
```

### 2. 并发处理

FastAPI天然支持异步处理，可以同时处理多个请求。

### 3. 缓存策略

对于频繁查询的问题，可以实现缓存机制：

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_zhongyi_response(input_text: str):
    return zhongyi_response(input_text)
```

---

## ❓ 常见问题

### Q1: 服务启动失败怎么办？

**A**: 检查以下几点：
1. 确认端口8000未被占用
2. 检查 `common/.env` 配置文件是否正确
3. 确认所有依赖已安装：`pip install -r requirements.txt`
4. 查看控制台错误信息

### Q2: 响应时间过长怎么办？

**A**: 可能的原因：
1. LLM模型响应慢 - 考虑使用更快的模型
2. FAISS索引较大 - 优化索引结构
3. Neo4j查询复杂 - 优化Cypher语句
4. 首次加载需要初始化 - 后续请求会更快

### Q3: 如何修改端口号？

**A**: 修改 `main.py` 最后一行：

```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # 改为8001端口
```

### Q4: 如何部署到生产环境？

**A**: 推荐使用以下方式之一：

**方式1: 使用Gunicorn + Uvicorn**
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**方式2: 使用Docker**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**方式3: 使用Nginx反向代理**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Q5: 如何监控API使用情况？

**A**: 可以添加日志记录：

```python
import logging
from datetime import datetime

logging.basicConfig(filename='api.log', level=logging.INFO)

@app.post("/process")
async def process(request: Request):
    start_time = datetime.now()
    data = await request.json()
    
    # 记录请求
    logging.info(f"Request: {data.get('input')} at {start_time}")
    
    # ... 业务逻辑
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # 记录响应时间和结果
    logging.info(f"Response time: {duration}s")
    
    return JSONResponse(content=result)
```

---

## 🔐 安全建议

### 1. 添加API认证

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials

@app.post("/process")
async def process(request: Request, credentials: dict = Depends(verify_token)):
    # 你的业务逻辑
    pass
```

### 2. 限制请求频率

```python
from slowapi import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

app.state.limiter = Limiter(default_rate_limit="10/minute")
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/process")
@limiter.limit("5/minute")
async def process(request: Request):
    # 每分钟最多5次请求
    pass
```

### 3. 输入验证

```python
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    input: str = Field(..., min_length=1, max_length=500, description="用户问题")
```

---

## 📝 更新日志

### v1.0.0 (2024-01-01)
- ✅ 初始版本发布
- ✅ 实现基本的中医问答接口
- ✅ 集成LangGraph工作流
- ✅ 支持Neo4j图数据库查询
- ✅ 支持FAISS向量相似度搜索
- ✅ 提供Swagger交互式文档

---

## 📞 技术支持

如有问题或建议，请联系：
- 📧 Email: [your-email@example.com]
- 💬 Issues: [GitHub Issues链接]
- 📖 文档: [项目Wiki链接]

---

## 📄 License

本项目仅供学习和研究使用。

---

## 🌟 附录

### A. 完整的请求-响应流程图

```
Client                          Server                         Backend
  |                               |                               |
  |-- POST /process ------------->|                               |
  |   {input: "人参功效"}          |                               |
  |                               |-- 意图识别 ------------------>| 
  |                               |                               |
  |                               |-- 实体抽取 ------------------>|
  |                               |                               |
  |                               |-- FAISS匹配 ---------------->|
  |                               |                               |
  |                               |-- 生成Cypher --------------->|
  |                               |                               |
  |                               |-- 执行Neo4j查询 ------------>|
  |                               |                               |
  |                               |-- LLM生成回答 -------------->|
  |                               |                               |
  |<-- 200 OK --------------------|                               |
  |   {input, output}             |                               |
  |                               |                               |
```

### B. 支持的实体类型

| 实体类型 | 英文标识 | 示例 |
|---------|---------|------|
| 症状 | Symptom | 咳嗽、发热、失眠 |
| 疾病 | Disease | 风寒感冒、脾虚泄泻 |
| 方剂 | Formula | 桂枝汤、麻黄汤 |
| 药材 | Herb | 人参、黄芪、当归 |
| 功效 | Effect | 清热、补气、祛湿 |
| 出处 | Source | 《伤寒论》《本草纲目》 |

### C. 常用测试问题

```
1. 人参有什么功效？
2. 桂枝汤的组成是什么？
3. 感冒了吃什么药？
4. 如何治疗失眠？
5. 黄芪和人参有什么区别？
6. 《伤寒论》中有哪些经典方剂？
7. 咳嗽有哪些中药可以治疗？
8. 补气的中药有哪些？
```

---

**最后更新时间**: 2024-01-01

**文档版本**: v1.0.0
