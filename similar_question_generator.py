from prompt_builder import PromptBuilder
from llm_model import LLMModel, OpenAIModel

class SimilarQuestionGenerator:
    def __init__(self, model):
        self.model = model
        self.prompt_builder = PromptBuilder()

    def generate_similar_question(self, question, options=None):
        if options is None:
           self.prompt_builder.build_generate_similar_question_prompt(question)
        else:
           self.prompt_builder.build_generate_similar_question_prompt_with_options(question, options)

     
        response = self.model.get_response([{"role": "user", "content": prompt}])
        return response['choices'][0]['message']['content']

if __name__ == "__main__":
    # Example usage with options
    model = YourModelClass()  # Replace with your actual model class
    generator = SimilarQuestionGenerator(model)
    question = "What are the benefits of exercise?"
    options = ["A) Weight loss", "B) Improved mood", "C) Increased energy", "D) All of the above"]
    similar_question = generator.generate_similar_question(question, options)
    print(similar_question)
