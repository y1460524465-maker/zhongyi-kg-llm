# 中医知识图谱问答系统 - Streamlit前端

## 📋 项目说明

这是基于Streamlit构建的中医知识图谱问答系统前端页面，调用FastAPI后端服务来提供智能问答功能。

## 🚀 快速开始

### 步骤1：启动FastAPI后端服务

```bash
cd ../api
python main.py
```

或双击运行 `start_server.bat`

### 步骤2：启动Streamlit前端

```bash
cd webui
streamlit run app.py
```

或双击运行 `start_app.bat`

### 步骤3：访问页面

打开浏览器访问：http://localhost:8501

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `app.py` | Streamlit主程序 |
| `start_app.bat` | Windows启动脚本 |
| `requirements.txt` | 依赖包列表 |

## 🛠️ 安装依赖

如果需要安装依赖：

```bash
pip install -r requirements.txt
```

或单独安装：

```bash
pip install streamlit requests
```

## 💡 使用说明

1. 在输入框中输入您的问题
2. 点击"🔍 提问"按钮
3. 等待系统生成回答
4. 查看回答结果

### 示例问题

- 人参有什么功效？
- 桂枝汤的组成是什么？
- 感冒了吃什么药？
- 如何治疗失眠？

## 🔌 接口说明

**API地址**: http://localhost:8000/process

**请求方式**: POST

**请求格式**:
```json
{
  "input": "您的问题"
}
```

**响应格式**:
```json
{
  "input": "您的问题",
  "output": "系统回答"
}
```

## ⚙️ 配置

如需修改API地址，编辑 `app.py` 中的 `API_URL` 变量：

```python
API_URL = "http://localhost:8000/process"
```

## 📝 注意事项

1. 确保先启动FastAPI后端服务
2. 确保端口8000和8501未被占用
3. 如需修改端口，请同时修改后端和前端配置

## 🔗 相关项目

- **FastAPI后端**: ../api/
- **LangGraph工作流**: ../langgraph_more_nodes/