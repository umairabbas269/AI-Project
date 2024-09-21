import os
from openai import OpenAI
from abc import ABC, abstractmethod
import logging

# Configure logging
logging.basicConfig(filename='llm_model.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Abstract class for LLMModel
class LLMModel(ABC):
    @abstractmethod
    def get_response(self, messages: list[dict], max_tokens: int, temperature: float) -> list[str]:
        pass

# Concrete class for OpenAI
class OpenAIModel(LLMModel):
    def __init__(self, model_name: str = 'gpt-4'):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key is not set in environment variables.")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def get_response(self, messages: list[dict], max_tokens: int = 1000, temperature: float = 0.1) -> list[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name, 
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            logging.info("Response received successfully.")
            return response.choices[0].message.content.strip().split("\n\n")
        except Exception as e:
            logging.error(f"Error while getting response: {e}")
            return []

if __name__ == "__main__":
    # Example usage
    model = OpenAIModel()
    question = "What is the capital of India?"
    response = model.get_response(messages=[{"role": "user", "content": f"{question}"}])
    print(response)
