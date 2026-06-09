import os
import streamlit as st
from knowledge_base import KnowledgeBase
from rag_chain import RAGChain
import tempfile

st.set_page_config(page_title="RAG智能问答系统", layout="wide")

if "kb" not in st.session_state:
    st.session_state.kb = KnowledgeBase()
    st.session_state.kb.load_vector_db()

if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "document_count" not in st.session_state:
    st.session_state.document_count = st.session_state.kb.get_document_count()

def init_rag_chain():
    if st.session_state.kb.vectorstore is not None:
        st.session_state.rag_chain = RAGChain(st.session_state.kb.vectorstore)

if st.session_state.kb.vectorstore is not None and st.session_state.rag_chain is None:
    init_rag_chain()

st.title("🔍 RAG智能问答系统")

with st.sidebar:
    st.subheader("知识库管理")
    
    uploaded_files = st.file_uploader("上传PDF或DOCX文件", type=["pdf", "docx"], accept_multiple_files=True)
    
    if st.button("构建/更新知识库"):
        if uploaded_files:
            with tempfile.TemporaryDirectory() as temp_dir:
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                
                documents = st.session_state.kb.load_documents(temp_dir)
                if documents:
                    st.session_state.kb.clear_db()
                    chunk_count = st.session_state.kb.build_vector_db(documents)
                    st.session_state.document_count = chunk_count
                    init_rag_chain()
                    st.success(f"知识库更新成功！共 {chunk_count} 个文本块")
                else:
                    st.error("未找到有效文档")
        else:
            st.warning("请先上传文档")
    
    if st.button("清空知识库"):
        st.session_state.kb.clear_db()
        st.session_state.rag_chain = None
        st.session_state.document_count = 0
        st.session_state.chat_history = []
        st.success("知识库已清空")
    
    st.subheader("知识库状态")
    st.write(f"文本块数量: {st.session_state.document_count}")

st.subheader("问答交互")
user_input = st.text_input("请输入您的问题:", key="input")

if st.button("提问"):
    if user_input.strip():
        if st.session_state.rag_chain is None:
            st.warning("请先上传文档并构建知识库")
        else:
            with st.spinner("正在思考..."):
                answer, sources = st.session_state.rag_chain.ask(user_input)
                
                st.session_state.chat_history.append({
                    "question": user_input,
                    "answer": answer,
                    "sources": sources
                })
                
                st.success("回答完成！")

if st.session_state.chat_history:
    st.subheader("对话历史")
    for i, chat in enumerate(reversed(st.session_state.chat_history), 1):
        with st.expander(f"问题 {len(st.session_state.chat_history) - i + 1}: {chat['question']}"):
            st.write(f"**回答:** {chat['answer']}")
            if chat['sources']:
                st.write("**参考来源:**")
                for j, source in enumerate(chat['sources'], 1):
                    src = source.metadata.get("source", "未知来源")
                    st.write(f"  {j}. {os.path.basename(src)}")

if st.button("清空对话历史"):
    st.session_state.chat_history = []
    if st.session_state.rag_chain:
        st.session_state.rag_chain.clear_memory()
    st.success("对话历史已清空")