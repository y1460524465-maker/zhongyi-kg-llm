import time
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# 定义状态结构
class MyState(TypedDict):
    make_vegetables: bool
    rice_heated: bool
    dish_ready: bool


# --- 节点定义 ---
def start_cooking(state: MyState):
    print("👨‍🍳 开始做饭！")
    return state


def make_vegetables(state: MyState):
    print("🔪 正在炒菜...")
    time.sleep(10)
    print("🔪 炒完菜了...")
    # 模拟完成切菜
    state["make_vegetables"] = True
    return state


def heat_rice(state: MyState):
    print("🍚 微波炉正在加热米饭...")
    time.sleep(2)
    print("🍚 米饭已经加热完成！")

    # 模拟加热完成
    state["rice_heated"] = True
    return state


def serve_dish(state: MyState):
    print("🍽️ 菜和饭都准备好了，上菜！")
    state["dish_ready"] = True
    return state


# --- 构建 LangGraph ---
def build_graph():
    graph_builder = StateGraph(MyState)
    graph_builder.add_node(start_cooking.__name__, start_cooking)
    graph_builder.add_node(make_vegetables.__name__, make_vegetables)
    graph_builder.add_node(heat_rice.__name__, heat_rice)
    graph_builder.add_node(serve_dish.__name__, serve_dish)

    # 顺序 & 并行逻辑
    graph_builder.add_edge(START, start_cooking.__name__)
    graph_builder.add_edge(start_cooking.__name__, make_vegetables.__name__)
    graph_builder.add_edge(start_cooking.__name__, heat_rice.__name__)

    # 并行结果都汇总到 serve  #这里是重点，
    graph_builder.add_edge([make_vegetables.__name__, heat_rice.__name__], serve_dish.__name__)

    graph_builder.add_edge(serve_dish.__name__, END)

    graph = graph_builder.compile()
    return graph


# --- 运行 ---
if __name__ == "__main__":
    # 打印节点名称
    # print(start_cooking.__name__)
    graph = build_graph()
    result = graph.invoke({})
    print("\n最终结果:", result)