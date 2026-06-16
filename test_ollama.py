import ollama

def test_ollama_api():
    try:
        print("Testing Ollama API connection...")
        response = ollama.chat(model='deepseek-r1:7b', messages=[
            {'role': 'user', 'content': 'Hello, how are you?'},
        ])
        print(f"Model response: {response['message']['content']}")
        print("Ollama API test PASSED!")
        return True
    except Exception as e:
        print(f"Ollama API test FAILED: {e}")
        return False

def test_embedding():
    try:
        print("\nTesting Ollama embedding...")
        response = ollama.embeddings(model='nomic-embed-text', prompt='Hello, world!')
        print(f"Embedding length: {len(response['embedding'])}")
        print("Embedding test PASSED!")
        return True
    except Exception as e:
        print(f"Embedding test FAILED: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("Ollama API Test Suite")
    print("=" * 50)
    test_ollama_api()
    test_embedding()
    print("\n" + "=" * 50)