from langgraph.graph import StateGraph, START, END
from typing import TypedDict


# ---------- 子图 ----------
class SubState(TypedDict):
    msg: str


def say_hello(state: SubState):
    print("👋 子图：你好，我是子流程！")
    print(state)
    return state


def say_bye(state: SubState):
    print("👋 子图：再见！")
    return state


def build_subgraph():
    graph_builder = StateGraph(SubState)
    graph_builder.add_node("hello", say_hello)
    graph_builder.add_node("bye", say_bye)
    graph_builder.add_edge(START, "hello")
    graph_builder.add_edge("hello", "bye")
    graph_builder.add_edge("bye", END)
    return graph_builder.compile()


# ---------- 主图 ----------
class MainState(TypedDict):
    done: bool


def start_main(state: MainState):
    print("🚀 主图开始运行！")
    return state


def finish_main(state: MainState):
    print("✅ 主图：全部完成！")
    state["done"] = True
    return state


def build_main_graph():
    #主图要用子图，就必须把子图创建出来，
    subgraph = build_subgraph()  # ✅ 子图

    g = StateGraph(MainState)
    g.add_node("start", start_main)
    g.add_node("sub", subgraph)  # 👈 把子图当作一个节点
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