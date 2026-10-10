import streamlit as st
import requests
import json
import uuid

st.set_page_config(
    page_title="中医知识图谱问答系统（流式）",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

STREAM_API_URL = "http://localhost:8000/process_stream"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.header("⚙️ 设置")
    st.info("API地址: http://localhost:8000")
    st.caption(f"会话ID: {st.session_state.session_id[:8]}...")
    st.markdown("---")
    st.markdown("### 📚 使用示例")
    st.markdown("1. 人参有什么功效？")
    st.markdown("2. 桂枝汤的组成是什么？")
    st.markdown("3. 感冒了吃什么药？")
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

st.title("🏥 中医知识图谱问答系统")
st.caption("流式输出版 · 实时显示推理进度")
st.markdown("---")

# 渲染历史对话
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入框
user_input = st.chat_input("请输入您的问题，例如：拉肚子该吃什么中药？")

if user_input:
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 流式输出
    with st.chat_message("assistant"):
        progress_placeholder = st.empty()
        answer_placeholder = st.empty()

        try:
            with requests.post(
                STREAM_API_URL,
                json={"input": user_input, "session_id": st.session_state.session_id},
                stream=True,
                timeout=120,
            ) as resp:
                if resp.status_code != 200:
                    st.error(f"请求失败，状态码: {resp.status_code}")
                else:
                    progress_lines = []
                    final_answer = ""

                    for chunk in resp.iter_content(chunk_size=None):
                        if not chunk:
                            continue
                        try:
                            msg = json.loads(chunk.decode("utf-8"))
                        except json.JSONDecodeError:
                            continue

                        msg_type = msg.get("type")
                        content = msg.get("msg", "")

                        if msg_type == "msg":
                            progress_lines.append(content)
                            progress_placeholder.info("  \n".join(progress_lines))

                        elif msg_type == "reply":
                            final_answer = content
                            answer_placeholder.markdown(final_answer)

                        elif msg_type == "done":
                            # 思考过程收起，保留可展开
                            progress_placeholder.empty()
                            with answer_placeholder.container():
                                with st.expander("查看推理过程", expanded=False):
                                    for line in progress_lines:
                                        st.caption(line)
                                st.markdown(final_answer)
                            break

                    if final_answer:
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": final_answer}
                        )

        except requests.exceptions.ConnectionError:
            st.error("无法连接到服务器，请确保FastAPI服务已启动！")
        except requests.exceptions.Timeout:
            st.error("请求超时，请稍后重试")
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
