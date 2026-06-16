import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

class KnowledgeBase:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.vector_store = None

    def load_documents(self, folder_path):
        documents = []
        supported_extensions = [".pdf", ".docx", ".doc"]
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in supported_extensions:
                continue
            
            try:
                if file_ext == ".pdf":
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                elif file_ext in [".docx", ".doc"]:
                    loader = Docx2txtLoader(file_path)
                    docs = loader.load()
                
                for doc in docs:
                    doc.metadata["source"] = filename
                documents.extend(docs)
                print(f"Loaded: {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        
        return documents

    def split_documents(self, documents, chunk_size=1000, chunk_overlap=200):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks

    def build_vector_store(self, documents):
        chunks = self.split_documents(documents)
        
        if os.path.exists(self.persist_directory):
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            self.vector_store.add_documents(chunks)
        else:
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
        
        self.vector_store.persist()
        print(f"Vector store built and persisted to {self.persist_directory}")

    def load_vector_store(self):
        if os.path.exists(self.persist_directory):
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print(f"Vector store loaded from {self.persist_directory}")
            return True
        return False

    def search(self, query, k=3):
        if not self.vector_store:
            self.load_vector_store()
        
        if not self.vector_store:
            return []
        
        results = self.vector_store.similarity_search(query, k=k)
        return results

    def get_stats(self):
        if not self.vector_store:
            self.load_vector_store()
        
        if not self.vector_store:
            return {"documents": 0, "chunks": 0}
        
        collection = self.vector_store._collection
        count = collection.count()
        return {"documents": count, "chunks": count}

def main():
    kb = KnowledgeBase()
    
    docs_folder = "./documents"
    if not os.path.exists(docs_folder):
        os.makedirs(docs_folder)
        print(f"Created documents folder: {docs_folder}")
    
    documents = kb.load_documents(docs_folder)
    
    if documents:
        kb.build_vector_store(documents)
    else:
        print("No documents found in the documents folder")
        print("Please add PDF or DOCX files to the documents folder and run again")
    
    stats = kb.get_stats()
    print(f"Knowledge base stats: {stats}")

if __name__ == "__main__":
    main()