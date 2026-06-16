from langchain_ollama import ChatOllama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from knowledge_base import KnowledgeBase

class RAGChatbot:
    def __init__(self, model_name="deepseek-r1:7b", kb_persist_dir="./chroma_db"):
        self.knowledge_base = KnowledgeBase(persist_directory=kb_persist_dir)
        self.model = ChatOllama(model=model_name)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        self.chain = None
        self._init_chain()

    def _init_chain(self):
        retriever = self.knowledge_base.vector_store.as_retriever(
            search_kwargs={"k": 3}
        ) if self.knowledge_base.load_vector_store() else None
        
        if not retriever:
            print("Warning: No vector store found. RAG functionality will be limited.")
            return
        
        template = """基于提供的参考文档回答问题。如果文档中没有相关信息，请明确说明"文档中未找到相关答案"。

参考文档：
{context}

对话历史：
{chat_history}

问题：
{question}

请根据参考文档和对话历史，用中文回答问题："""
        
        prompt = PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template=template
        )
        
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.model,
            retriever=retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True,
            verbose=False
        )

    def answer(self, question):
        if not self.chain:
            return {
                "answer": "知识库尚未构建，请先上传文档并构建知识库。",
                "sources": []
            }
        
        try:
            result = self.chain({"question": question})
            answer = result.get("answer", "无法获取答案")
            
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    source_info = {
                        "source": doc.metadata.get("source", "unknown"),
                        "page": doc.metadata.get("page", "N/A")
                    }
                    if source_info not in sources:
                        sources.append(source_info)
            
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            return {
                "answer": f"回答过程中出现错误：{str(e)}",
                "sources": []
            }

    def clear_history(self):
        self.memory.clear()

    def get_history(self):
        return self.memory.load_memory_variables({}).get("chat_history", [])

def main():
    print("Initializing RAG Chatbot...")
    chatbot = RAGChatbot()
    
    print("\nRAG Chatbot ready!")
    print("Type 'exit' to quit, 'clear' to clear history")
    
    while True:
        question = input("\n请输入问题：")
        
        if question.lower() == "exit":
            break
        if question.lower() == "clear":
            chatbot.clear_history()
            print("对话历史已清空")
            continue
        
        result = chatbot.answer(question)
        print(f"\n回答：{result['answer']}")
        
        if result["sources"]:
            print("\n参考来源：")
            for i, source in enumerate(result["sources"], 1):
                print(f"{i}. {source['source']} (第{source['page']}页)")

if __name__ == "__main__":
    main()