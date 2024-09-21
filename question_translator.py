from prompt_builder import PromptBuilder

class QuestionTranslator:
    def __init__(self, model):
        self.model = model
        self.prompt_builder = PromptBuilder()

    def translate_text(self, text, language):
        prompt = self.prompt_builder.build_translate_text_prompt(text, language)
        response = self.model.get_response([{"role": "user", "content": prompt}])
        return response['choices'][0]['message']['content']
