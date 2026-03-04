import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"


async def get_response(query: str, context: str):
    try:
        prompt = f"""
        You are a legal rental agreement assistant.
        Use the following document context to answer the question.

        Context:
        {context}

        Question:
        {query}

        Answer clearly and professionally.
        """

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
        )

        result = response.json()
        return result.get("response", "No response from model.")

    except Exception as e:
        return f"Ollama Error: {str(e)}"