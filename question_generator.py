import re
from prompt_builder import PromptBuilder
from llm_model import LLMModel, OpenAIModel 
import logging

# Configure logging to write to a file
logging.basicConfig(filename='question_generator.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# This is a single-line comment

class QuestionGenerator:
    def __init__(self, model: LLMModel):
        self.model = model
        self.prompt_builder = PromptBuilder()

    def parse_question(self, response_text: str) -> dict:
        # Improved regex to handle optional whitespace and variations
        match = re.search(r'Question:\s*(.+?)\s*A\.\s*(.+?)\s*B\.\s*(.+?)\s*C\.\s*(.+?)\s*D\.\s*(.+?)\s*Correct Answer:\s*([A-D])', response_text)
        if match:
            return {
                "question": match.group(1),
                "options": {
                    "A": match.group(2),
                    "B": match.group(3),
                    "C": match.group(4),
                    "D": match.group(5),
                },
                "correct_answer": match.group(6)
            }
        return {}

    def generate_questions(self, specialization: str, difficulty: str, num_questions: int, max_tokens: int) -> list:
        prompt = self.prompt_builder.get_mcq_generation_prompt(specialization, difficulty, num_questions)
        logging.info("Generating questions with prompt: %s", prompt)

        try:
            response = self.model.get_response([{"role": "user", "content": prompt}], max_tokens=max_tokens)
            if not isinstance(response, list):
                raise ValueError("Response is not a list")
        except Exception as e:
            logging.error("Error generating questions: %s", e)
            return []  # Return an empty list on error
        
        questions = [self.parse_question(choice) for choice in response if self.parse_question(choice)]
        logging.info("Generated %d questions", len(questions))
        return questions  # Return the list of questions

if __name__ == "__main__":
    # Example usage
    model = OpenAIModel() 
    generator = QuestionGenerator(model)
    questions = generator.generate_questions("History", "Easy", 4, 1000)
    print(questions)
