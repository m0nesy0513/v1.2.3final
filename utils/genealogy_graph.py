import networkx as nx
from pyvis.network import Network
import streamlit as st

MAX_GRAPH_NODES = 120


def _clean_node(text: str) -> str:
    return text.strip().replace("：", "").replace(":", "")[:20]


def draw_genealogy_graph(text: str):
    relations = []

    for line in text.split("\n"):
        if "之子" not in line:
            continue

        parts = line.split("之子")
        if len(parts) != 2:
            continue

        father = _clean_node(parts[0])
        child = _clean_node(parts[1])

        if father and child and father != child:
            relations.append((father, child))

    relations = relations[:MAX_GRAPH_NODES]

    if not relations:
        st.warning("未识别到可生成图谱的父子关系。")
        return

    if len(relations) >= MAX_GRAPH_NODES:
        st.info("图谱节点较多，已自动截取前 120 条关系，手机端建议优先查看简化图。")

    graph = nx.DiGraph()

    for father, child in relations:
        graph.add_edge(father, child)

    net = Network(height="600px", width="100%", directed=True)
    net.from_nx(graph)

    html = net.generate_html()
    st.components.v1.html(html, height=620, scrolling=True)
