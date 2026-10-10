import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from common.config import Config

conf = Config()

# ============ 配置llm区域 ============
# vLLM 服务地址与模型名从环境变量读取（VLLM_BASE_URL / VLLM_MODEL_NAME），
# 本地部署默认 http://localhost:8000/v1，请勿硬编码云端实例地址。
my_llm = ChatOpenAI(
    api_key=os.getenv("VLLM_API_KEY", "EMPTY"),
    base_url=conf.VLLM_BASE_URL,
    model=conf.VLLM_MODEL_NAME or "export/qwen2.5-merged-0605"
)

if __name__ == '__main__':
    # 构造对话消息
    messages = [
        SystemMessage(content="请从以下中医文本中抽取知识图谱结构，包括实体与关系。"),
        HumanMessage(
            content="【方剂名称】斩梦丹\n- 中医百科\n- 斩梦丹\n斩梦丹的药方\n出处\n《普济方》卷三十三\n组成\n知母30克黄柏30克（去皮）滑石90克\n【制法】\n上药为末，白水和丸。\n斩梦丹的功效\n主治\n治梦泄遗精。\n用法\n空腹时温酒送下。")
    ]
    # 调用模型
    result = ""
    for chunk in my_llm.stream(messages):
        result += chunk.content
        print(chunk.content, end="", flush=True)
    print("\n")
    print("*" * 100)
    print(result)
