# RAG-QA-System

基于本地知识库的RAG智能问答系统，利用Ollama本地大模型、LangChain框架和Streamlit开发工具构建。

## 项目简介

本项目实现了一个能够"学习"指定本地文档并回答相关问题的智能问答系统，有效缓解大模型"幻觉"问题。

## 环境要求与安装步骤

### 1. Python版本
- Python 3.10+

### 2. 依赖库安装
```bash
pip install -r requirements.txt
```

### 3. Ollama安装
1. 下载Ollama: https://ollama.com/download
2. 安装完成后，在命令行运行:
```bash
ollama pull deepseek-r1:7b
ollama pull nomic-embed-text
```

## 使用说明

### 运行Web应用
```bash
streamlit run app.py
```

### 使用步骤
1. 在左侧侧边栏上传PDF或DOCX格式的文档
2. 点击"构建/更新知识库"按钮构建向量数据库
3. 在问答输入框中输入问题，点击"提问"获取答案
4. 系统会显示回答及参考来源

### 命令行版本
```bash
python rag_cli.py
```

### 测试Ollama API
```bash
python test_ollama.py
```

## 关键技术点说明

### RAG流程
1. **文档加载**: 支持PDF和DOCX格式文档
2. **文本分块**: 使用RecursiveCharacterTextSplitter，chunk_size=1000, chunk_overlap=200
3. **向量化**: 使用Ollama内置的nomic-embed-text嵌入模型
4. **向量存储**: 使用Chroma向量数据库
5. **检索增强**: 使用ConversationalRetrievalChain连接检索器和大模型

### 所用模型
- **嵌入模型**: nomic-embed-text
- **大语言模型**: deepseek-r1:7b

## 项目结构
```
RAG-QA-System/
├── app.py              # Streamlit Web应用
├── knowledge_base.py    # 知识库管理模块
├── rag_chain.py        # RAG问答链模块
├── rag_cli.py          # 命令行版本
├── test_ollama.py      # Ollama API测试
├── requirements.txt    # 依赖清单
└── .gitignore          # Git忽略配置
```

## 功能特点
- 支持PDF和DOCX文档上传
- 批量文档处理
- 对话历史记忆
- 参考来源追踪
- 本地部署，数据隐私安全

## 已知问题与改进方向
- 大模型响应时间较长，可考虑使用更小的模型
- 可增加文档预览功能
- 可增加多轮对话优化
- 可增加文档分类功能