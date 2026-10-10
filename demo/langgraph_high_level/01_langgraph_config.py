from langgraph.graph import StateGraph, START, END
from langgraph.types import RunnableConfig
#创建一个langgraph 状态图的步骤
#1.创建状态
#2.创建 节点
#3.把节点串起来

# 定义一个简单的状态
class State(dict):
    input: str
    step1: str
    step2: str
    result: str


# 定义节点函数
#要使用config配置，就需要将RunnableConfig 传入到节点函数中
#从配置中拿到前缀，拼接到文本中
def step1(state: State, config: RunnableConfig):
    prefix = config.get("configurable", {}).get("prefix", "")
    uname = config.get("configurable", {}).get("uname", "")
    renshe = config.get("configurable", {}).get("renshe", "")
    text = f"{prefix}{state['input']}-{uname}-{renshe}"
    state["step1"] = text
    print(f"[Step1] 使用 prefix = {prefix}")
    return state


def step2(state: State, config: RunnableConfig):
    suffix = config.get("configurable", {}).get("suffix", "")
    result = f"{state['step1']}{suffix}"
    print(f"[Step2] 使用 suffix = {suffix}")
    state["step2"] = result
    state["result"] = result
    return state


# 构建有向图
def build_graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("step1", step1)
    graph_builder.add_node("step2", step2)
    graph_builder.add_edge(START, "step1")
    graph_builder.add_edge("step1", "step2")
    graph_builder.add_edge("step2", END)

    # 编译图
    graph = graph_builder.compile()
    return graph


# 构建图
graph = build_graph()

# 运行时传入config
config = RunnableConfig(
    configurable={
        "prefix": "[前缀] ",
        "suffix": " [后缀]",
        "uname":"wangliangwu",
        "renshe":"好人卡"
    }
)

result = graph.invoke({"input": "你好，LangGraph！"}, config=config)

print("最终输出：", result)