from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import RunnableConfig


# 定义状态结构
class State(dict):
    total: int  # 当前累加总和
    new_value: int  # 新输入的数字


# 定义节点：执行累加逻辑
def add_node(state: State, config: RunnableConfig):
    # 取出旧的总和（如果没有则为0）
    old_total = state.get("total", 0)
    print(old_total)
    # 获取新输入的数字
    new_value = state["new_value"]
    # 计算新的总和
    new_total = old_total + new_value
    state["total"] = new_total
    return state


# 构建图
def build_graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("add", add_node)
    graph_builder.add_edge(START, "add")
    graph_builder.add_edge("add", END)

    # 编译成可运行的应用
    memory = InMemorySaver()
    graph = graph_builder.compile(memory)
    return graph


graph = build_graph()

# === 第一次调用 ===
config1 = RunnableConfig(configurable={
    "thread_id": "12345"
})
result1 = graph.invoke({"new_value": 5}, config=config1)
print("结果1:", result1)

# # === 第二次调用（同一个线程，累加）===
result2 = graph.invoke({"new_value": 7}, config=config1)
print("结果2:", result2)
#
# === 第三次调用（不同线程，全新开始）===
config2 = RunnableConfig(configurable={
    "thread_id": "12345"
})
result3 = graph.invoke({"new_value": 10}, config=config2)
print("结果3:", result3)