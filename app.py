import streamlit as st
import os
import tempfile
from knowledge_base import KnowledgeBase
from rag_chain import RAGChatbot

st.set_page_config(page_title="RAG智能问答系统", page_icon="📚", layout="wide")

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'kb' not in st.session_state:
    st.session_state.kb = KnowledgeBase()

def init_chatbot():
    st.session_state.chatbot = RAGChatbot()

def build_knowledge_base(documents):
    kb = st.session_state.kb
    kb.build_vector_store(documents)
    init_chatbot()

st.title("📚 基于本地知识库的RAG智能问答系统")

with st.sidebar:
    st.header("知识库管理")
    
    uploaded_files = st.file_uploader(
        "上传文档",
        type=["pdf", "docx", "doc"],
        accept_multiple_files=True
    )
    
    if st.button("构建/更新知识库"):
        if uploaded_files:
            with st.spinner("正在处理文档..."):
                documents = []
                for uploaded_file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
                        temp_file.write(uploaded_file.getvalue())
                        temp_file_path = temp_file.name
                    
                    try:
                        if uploaded_file.name.endswith(".pdf"):
                            from langchain_community.document_loaders import PyPDFLoader
                            loader = PyPDFLoader(temp_file_path)
                            docs = loader.load()
                        elif uploaded_file.name.endswith((".docx", ".doc")):
                            from langchain_community.document_loaders import Docx2txtLoader
                            loader = Docx2txtLoader(temp_file_path)
                            docs = loader.load()
                        
                        for doc in docs:
                            doc.metadata["source"] = uploaded_file.name
                        documents.extend(docs)
                    finally:
                        os.unlink(temp_file_path)
                
                build_knowledge_base(documents)
                st.success(f"知识库构建成功！共处理 {len(documents)} 个文档")
        else:
            st.warning("请先上传文档")
    
    stats = st.session_state.kb.get_stats()
    st.info(f"当前知识库状态：\n- 文本块数量：{stats['chunks']}")
    
    if st.button("清空对话历史"):
        st.session_state.messages = []
        if st.session_state.chatbot:
            st.session_state.chatbot.clear_history()
        st.success("对话历史已清空")

st.header("问答交互")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("参考来源"):
                for source in message["sources"]:
                    st.write(f"- {source['source']} (第{source['page']}页)")

if prompt := st.chat_input("请输入您的问题"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("正在思考..."):
            if not st.session_state.chatbot:
                init_chatbot()
            
            result = st.session_state.chatbot.answer(prompt)
            st.markdown(result["answer"])
            
            if result.get("sources"):
                with st.expander("参考来源"):
                    for source in result["sources"]:
                        st.write(f"- {source['source']} (第{source['page']}页)")
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result.get("sources", [])
    })