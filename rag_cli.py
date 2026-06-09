from knowledge_base import KnowledgeBase
from rag_chain import RAGChain

def main():
    kb = KnowledgeBase()
    docs_path = "./documents"
    
    if kb.load_vector_db():
        print("知识库已加载")
    else:
        print("正在构建知识库...")
        documents = kb.load_documents(docs_path)
        if not documents:
            print(f"在 {docs_path} 目录中未找到文档")
            return
        chunk_count = kb.build_vector_db(documents)
        print(f"知识库构建完成，共 {chunk_count} 个文本块")
    
    rag_chain = RAGChain(kb.vectorstore)
    
    print("\nRAG问答系统已就绪！")
    print("输入 'quit' 或 'exit' 退出\n")
    
    while True:
        question = input("请输入问题: ")
        if question.lower() in ["quit", "exit"]:
            print("再见！")
            break
        
        answer, sources = rag_chain.ask(question)
        print(f"\n回答: {answer}")
        if sources:
            print("\n参考来源:")
            for i, doc in enumerate(sources, 1):
                source = doc.metadata.get("source", "未知来源")
                print(f"  {i}. {source}")
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()