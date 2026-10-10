import time
from typing import TypedDict, List

from langgraph.graph import StateGraph, START, END
import operator
from typing import Annotated
def my_merge(a, b):
    # 这里定义合并逻辑
    return b

# 定义状态结构
class MyState(TypedDict):
    menu: Annotated[list,my_merge ]
    all_ready: bool


# --- 节点定义 ---
def start_cooking(state: MyState):
    print("👨‍🍳 厨房准备开始！")
    # 初始化共享菜单列表
    state["menu"] = []
    return state


def chef_a(state: MyState):
    print("👩‍🍳 A 厨师在做：番茄炒蛋...")
    time.sleep(2)
    # 向共享 list 添加菜品
    state["menu"].append("番茄炒蛋")
    return state


def chef_b(state: MyState):
    print("👨‍🍳 B 厨师在做：宫保鸡丁...")
    time.sleep(3)
    state["menu"].append("宫保鸡丁")
    return state


def chef_c(state: MyState):
    print("👩‍🍳 C 厨师在做：鱼香肉丝...")
    time.sleep(1)
    state["menu"].append("鱼香肉丝")
    return state


def serve_dish(state: MyState):
    print("\n🍽️ 所有菜都准备好了！菜单如下：")
    for dish in state["menu"]:
        print(" -", dish)
    state["all_ready"] = True
    return state


# --- 构建 LangGraph ---
def build_graph():
    graph_builder = StateGraph(MyState)
    graph_builder.add_node("start", start_cooking)
    graph_builder.add_node("chef_a", chef_a)
    graph_builder.add_node("chef_b", chef_b)
    graph_builder.add_node("chef_c", chef_c)
    graph_builder.add_node("serve", serve_dish)

    # 启动 → 并行三个厨师
    graph_builder.add_edge(START, "start")
    graph_builder.add_edge("start", "chef_a")
    graph_builder.add_edge("start", "chef_b")
    graph_builder.add_edge("start", "chef_c")

    # 三个厨师汇总到 serve
    graph_builder.add_edge(["chef_a", "chef_b", "chef_c"], "serve")

    graph_builder.add_edge("serve", END)

    return graph_builder.compile()


# --- 运行 ---
if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke({})
    print("\n最终结果:", result)