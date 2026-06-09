from langchain.chat_models import ChatOllama
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

class RAGChain:
    def __init__(self, vectorstore, model_name="deepseek-r1:7b"):
        self.llm = ChatOllama(model=model_name, temperature=0)
        self.vectorstore = vectorstore
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        self.chain = self._build_chain()

    def _build_chain(self):
        prompt_template = """基于提供的参考文档回答问题。如果文档中没有相关信息，则明确说"文档中未找到相关答案"。

参考文档:
{context}

问题: {question}

回答:"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        return chain

    def ask(self, question):
        result = self.chain({"question": question})
        answer = result.get("answer", "")
        sources = result.get("source_documents", [])
        return answer, sources

    def clear_memory(self):
        self.memory.clear()