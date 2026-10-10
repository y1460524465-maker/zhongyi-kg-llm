import requests
import json
import uuid

BASE_URL = "http://localhost:8000"


def test_stream(question: str, session_id: str = None):
    """测试流式接口，逐块打印收到的消息"""
    if session_id is None:
        session_id = str(uuid.uuid4())

    print(f"\n{'=' * 60}")
    print(f"问题: {question}")
    print(f"session_id: {session_id}")
    print("=" * 60)

    payload = {"input": question, "session_id": session_id}

    with requests.post(
        f"{BASE_URL}/process_stream",
        json=payload,
        stream=True,
        timeout=120
    ) as resp:
        if resp.status_code != 200:
            print(f"❌ 请求失败，状态码: {resp.status_code}")
            print(resp.text)
            return None

        final_reply = None
        for chunk in resp.iter_content(chunk_size=None):
            if not chunk:
                continue
            try:
                msg = json.loads(chunk.decode("utf-8"))
            except json.JSONDecodeError:
                print(f"[raw] {chunk.decode('utf-8')}")
                continue

            msg_type = msg.get("type")
            content = msg.get("msg", "")

            if msg_type == "msg":
                print(f"  [进度] {content}")
            elif msg_type == "reply":
                print(f"\n  [回答]\n{content}")
                final_reply = content
            elif msg_type == "done":
                print("\n  [完成]")
                break

        return final_reply


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 流式接口测试")
    print("=" * 60)

    # 用同一个 session_id 模拟多轮对话
    session = str(uuid.uuid4())

    test_stream("世界第一高峰是什么？", session_id=session)
    test_stream("那第二呢？", session_id=session)          # 测试记忆：能否理解上下文
    test_stream("拉肚子该吃什么中药？", session_id=session) # 测试中医路径

    # 换一个 session，验证记忆隔离
    print(f"\n{'=' * 60}")
    print("换新 session，验证记忆隔离")
    test_stream("那第二呢？")  # 新 session 无历史，应返回无法理解的结果
