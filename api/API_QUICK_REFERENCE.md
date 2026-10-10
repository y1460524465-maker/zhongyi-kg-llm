# API 快速参考手册

## 🚀 快速开始

### 启动服务
```bash
cd api
python main.py
```

### 访问地址
- **API**: http://localhost:8000
- **文档**: http://localhost:8000/docs

---

## 📡 核心接口

### POST /process - 中医问答接口

**请求**:
```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"input": "人参有什么功效？"}'
```

**响应**:
```json
{
  "input": "人参有什么功效？",
  "output": "人参具有大补元气、复脉固脱、补脾益肺等功效..."
}
```

---

## 💻 代码示例

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/process",
    json={"input": "人参有什么功效？"}
)
print(response.json()["output"])
```

### JavaScript
```javascript
fetch('http://localhost:8000/process', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({input: '人参有什么功效？'})
})
.then(r => r.json())
.then(data => console.log(data.output));
```

### Java
```java
OkHttpClient client = new OkHttpClient();
RequestBody body = RequestBody.create(
    "{\"input\":\"人参有什么功效？\"}",
    MediaType.parse("application/json")
);
Request request = new Request.Builder()
    .url("http://localhost:8000/process")
    .post(body)
    .build();
Response response = client.newCall(request).execute();
```

---

## 📋 常用测试问题

```json
{"input": "人参的性味归经是什么？"}
{"input": "桂枝汤的组成和功效？"}
{"input": "感冒咳嗽吃什么药？"}
{"input": "如何治疗失眠？"}
{"input": "补气的中药有哪些？"}
```

---

## ⚠️ 注意事项

1. **超时设置**: 建议设置120秒超时
   ```python
   requests.post(url, json=data, timeout=120)
   ```

2. **错误处理**: 始终检查响应状态码
   ```python
   if response.status_code == 200:
       result = response.json()
   else:
       print(f"Error: {response.status_code}")
   ```

3. **FAISS路径**: 索引文件默认在 `create_information/` 下，可用环境变量覆盖（建议用英文路径）
   ```
   FAISS_INDEX_PATH=<英文路径>/nero4j_embedding_faiss.index
   FAISS_ID2TEXT_PATH=<英文路径>/nero4j_embedding_faiss_id2text.pkl
   ```

---

## 🔧 配置修改

### 修改端口
编辑 `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # 改为8001
```

### 修改FAISS路径
编辑 `langgraph_more_nodes/nodes/match_entity_node.py`:
```python
index_path = r"你的路径\nero4j_embedding_faiss.index"
```

---

## ❓ 常见问题

| 问题 | 解决方案 |
|------|---------|
| 连接被拒绝 | 确认服务已启动 |
| 响应超时 | 增加timeout时间 |
| FAISS加载失败 | 检查文件路径是否为英文 |
| 端口被占用 | 修改端口号或关闭占用程序 |

---

## 📊 性能指标

- **平均响应时间**: 5-30秒（取决于问题复杂度）
- **并发支持**: 支持多请求并发处理
- **推荐超时**: 120秒

---

## 📞 获取帮助

- 完整文档: [API_INTERFACE.md](API_INTERFACE.md)
- Swagger文档: http://localhost:8000/docs
- 快速诊断: `python quick_test.py`

---

**提示**: 更多详细信息请查看 [API_INTERFACE.md](API_INTERFACE.md)
