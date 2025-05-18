import os
import logging
import requests
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='llm_model.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==============================
# Abstract Class for LLM Models
# ==============================
class LLMModel(ABC):
    @abstractmethod
    def get_response(self, messages: list[dict], max_tokens: int, temperature: float) -> list[str]:
        pass


# ===================
# Groq Model Class
# ===================
class GroqModel(LLMModel):
    def __init__(self, model_name: str = 'llama3-8b-8192'):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("🔴 GROQ_API_KEY not found in environment variables")
        self.model_name = model_name
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"  # Groq's OpenAI-compatible chat API endpoint

    def get_response(self, messages: list[dict], max_tokens: int = 1000, temperature: float = 0.1) -> list[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                logging.info("✅ Groq response received successfully")
                # Extract the text from each choice
                return [choice["message"]["content"].strip() for choice in data.get("choices", [])]
            else:
                logging.error(f"❌ Error from Groq: Status code {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logging.error(f"❌ Groq Exception: {e}")
            return []


# ==============================
# Factory Method for LLM Models
# ==============================
def get_llm_model(provider: str = "groq") -> LLMModel:
    provider = provider.lower()
    if provider == "openai":
        # You can implement OpenAIModel class similar to before if you want
        raise NotImplementedError("OpenAIModel not implemented in this snippet")
    elif provider == "groq":
        return GroqModel()
    else:
        raise ValueError(f"⚠️ Unsupported provider: {provider}")


# ==============================
# Example Usage
# ==============================
if __name__ == "__main__":
    model = get_llm_model("groq")  # Using Groq llama3-8b-8192 by default
    
    test_prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Generate 3 multiple-choice questions about Python programming."}
    ]
    
    response = model.get_response(messages=test_prompt)
    
    print("Generated Questions:")
    if response:
        for i, question in enumerate(response, 1):
            print(f"{i}. {question}")
    else:
        print("No questions generated or empty response received.")
