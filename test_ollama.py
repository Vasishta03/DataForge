# test_ollama.py
import ollama

def test_ollama_connection():
    try:
        response = ollama.generate(model='mistral', prompt='Test connection')
        print("Connection successful! Response:", response['response'])
    except Exception as e:
        print("Connection failed:", str(e))

if __name__ == "__main__":
    test_ollama_connection()


# for testing ollama whether it is working or not 
