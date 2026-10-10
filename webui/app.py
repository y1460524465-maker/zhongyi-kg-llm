import streamlit as st
import requests
import json
import uuid

# 页面配置
st.set_page_config(
    page_title="中医知识图谱问答系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 页面标题
st.title("🏥 中医知识图谱问答系统")
st.markdown("---")

# API配置
API_URL = "http://localhost:8000/process"

# 每个浏览器标签页生成唯一 session_id，页面刷新后保持不变
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 侧边栏（可选）
with st.sidebar:
    st.header("⚙️ 设置")
    st.info("API地址: http://localhost:8000")
    st.markdown("---")
    st.markdown("### 📚 使用示例")
    st.markdown("1. 人参有什么功效？")
    st.markdown("2. 桂枝汤的组成是什么？")
    st.markdown("3. 感冒了吃什么药？")

# 主页面
st.subheader("💬 请输入您的问题")

# 输入框
user_input = st.text_area(
    label="问题",
    placeholder="例如：人参有什么功效？",
    height=100
)

# 提交按钮
col1, col2 = st.columns([1, 4])
with col1:
    submit_button = st.button("🔍 提问", type="primary", use_container_width=True)

# 回答区域
st.markdown("---")
st.subheader("📝 回答")
answer_container = st.container()

# 处理请求
if submit_button and user_input:
    with st.spinner("正在思考中..."):
        try:
            # 调用API
            response = requests.post(
                API_URL,
                json={"input": user_input, "session_id": st.session_state.session_id},
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("output", "")
                
                # 展示回答
                with answer_container:
                    st.success("回答已生成！")
                    st.markdown(f"**问题:** {user_input}")
                    st.markdown(f"**回答:**\n\n{answer}")
                    
                    # 可选：显示完整的API响应
                    with st.expander("查看完整响应"):
                        st.json(result)
            else:
                st.error(f"请求失败，状态码: {response.status_code}")
                st.text(response.text)
                
        except requests.exceptions.ConnectionError:
            st.error("无法连接到服务器，请确保FastAPI服务已启动！")
            st.info("启动命令: cd api && python main.py")
        except requests.exceptions.Timeout:
            st.error("请求超时，请稍后重试")
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
elif submit_button and not user_input:
    st.warning("请输入问题！")

# 页脚
st.markdown("---")
st.caption("中医知识图谱问答系统 | 基于LangGraph和FastAPI")