from langgraph.graph import StateGraph, START, END
from typing import TypedDict


# ---------- 子图 ----------
class SubState(TypedDict):
    name: str
    age: int


def say_hello(state: SubState):
    name = state["name"]
    state["age"] =18
    print("子图开始")
    print(f"👋 子图：你好，{name},我是子流程！")
    return state


def say_bye(state: SubState):
    name = state["name"]
    print("子图结束")
    print(f"👋 子图：{name},再见！")
    return state


def build_subgraph():
    g = StateGraph(SubState)
    g.add_node("hello", say_hello)
    g.add_node("bye", say_bye)
    g.add_edge(START, "hello")
    g.add_edge("hello", "bye")
    g.add_edge("bye", END)
    return g.compile()


# ---------- 主图 ----------
class MainState(TypedDict):
    done: bool
    sub_output: dict  # 用于保存子图返回结果


def start_main(state: MainState):
    print("🚀 主图开始运行！")
    return state


# ✅ 子图包装节点（负责调用子图并传递/接收数据）
def run_subgraph(state: MainState):
    subgraph = build_subgraph()

    # 从主图状态中构造子图输入
    sub_state = {"name": "小帅"}

    # 调用子图
    result = subgraph.invoke(sub_state)

    # 打印和合并结果回主图
    print("✅ 主图：子图输出 =", result)
    state["sub_output"] = result
    return state


def finish_main(state: MainState):
    print("✅ 主图：全部完成！")
    state["done"] = True
    return state


def build_main_graph():
    g = StateGraph(MainState)
    g.add_node("start", start_main)
    g.add_node("sub", run_subgraph)
    g.add_node("finish", finish_main)

    g.add_edge(START, "start")
    g.add_edge("start", "sub")
    g.add_edge("sub", "finish")
    g.add_edge("finish", END)
    return g.compile()


# ---------- 运行 ----------
if __name__ == "__main__":
    graph = build_main_graph()
    result = graph.invoke({})
    print("结果：", result)