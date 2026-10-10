from langgraph.graph.state import CompiledStateGraph

from langgraph_more_nodes.full_workflow import build_graph


def output_pic_graph(app: CompiledStateGraph, filename: str = "graph.jpg"):
    try:
        mermaid_code = app.get_graph().draw_mermaid_png()
        with open(filename, 'wb') as f:
            f.write(mermaid_code)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    output_pic_graph(build_graph().compile())