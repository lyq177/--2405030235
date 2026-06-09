from langchain.chat_models import ChatOllama

def test_ollama():
    try:
        llm = ChatOllama(model="deepseek-r1:7b", temperature=0)
        response = llm.predict("Hello! What is natural language processing?")
        print("Ollama API测试成功！")
        print("响应:", response[:200] + "..." if len(response) > 200 else response)
        return True
    except Exception as e:
        print(f"Ollama API测试失败: {e}")
        return False

if __name__ == "__main__":
    test_ollama()