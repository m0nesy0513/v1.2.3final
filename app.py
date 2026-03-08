import os
import streamlit as st

from utils.docx_parser import parse_docx
from utils.rag_loader import load_knowledge_base
from utils.vector_store import build_or_load_vector_store
from utils.qa_agent import rag_answer, analyze_genealogy
from utils.genealogy_graph import draw_genealogy_graph
from utils.migration_map import draw_migration_map
from utils.report_generator import generate_pdf

APP_TITLE = "族谱勘查 v1.2.3 Final"
CSS_PATH = os.path.join("assets", "style.css")


def load_css():
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(page_title=APP_TITLE, layout="wide")
load_css()

st.title(APP_TITLE)

@st.cache_resource(show_spinner="正在加载知识库与向量索引，请稍候...")
def load_rag_resources():
    import json

    with open("genealogy_expert_kb.json", "r", encoding="utf-8") as f:
        docs = json.load(f)
    index, texts = build_or_load_vector_store(docs, cache_dir="data")
    return docs, index, texts

docs, index, texts = load_rag_resources()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "current_genealogy_text" not in st.session_state:
    st.session_state.current_genealogy_text = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

page = st.sidebar.radio("导航", ["首页", "族谱分析", "AI问答", "族谱图谱", "迁徙地图"])

if page == "首页":
    st.write("面向族谱整理、校勘、问答与可视化的 AI 系统。")
    st.write(f"当前知识库文档数：{len(docs)}")
    st.write(f"当前知识库段落数：{len(texts)}")
    st.info("首次启动会加载向量模型并构建缓存，可能稍慢；后续会快很多。")

elif page == "族谱分析":
    file = st.file_uploader("上传族谱 DOCX", type=["docx"], key="analysis_file")

    if file:
        st.session_state.analysis_result = ""
        text = parse_docx(file)
        st.session_state.current_genealogy_text = text

        st.text_area("族谱内容", text, height=400)

        if st.button("开始分析", use_container_width=True):
            with st.spinner("AI 正在分析，请稍候..."):
                result = analyze_genealogy(text, index, texts)
            st.session_state.analysis_result = result

        if st.session_state.analysis_result:
            st.markdown(st.session_state.analysis_result)

            pdf_data = generate_pdf(st.session_state.analysis_result)
            st.download_button(
                "下载 PDF 报告",
                data=pdf_data,
                file_name="genealogy_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

elif page == "AI问答":
    col1, col2 = st.columns([6, 1])

    with col2:
        if st.button("清空对话", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("请输入问题")

    if question:
        st.session_state.chat_messages.append({"role": "user", "content": question})

        with st.spinner("AI 思考中..."):
            answer = rag_answer(
                question=question,
                index=index,
                texts=texts,
                current_genealogy_text=st.session_state.current_genealogy_text,
            )

        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
        st.rerun()

elif page == "族谱图谱":
    st.info("图谱节点较多时，建议优先使用电脑端查看。")
    file = st.file_uploader("上传族谱 DOCX", type=["docx"], key="graph_file")
    if file:
        text = parse_docx(file)
        draw_genealogy_graph(text)

elif page == "迁徙地图":
    file = st.file_uploader("上传族谱 DOCX", type=["docx"], key="map_file")
    if file:
        text = parse_docx(file)
        draw_migration_map(text)
