class PromptBuilder:

    def get_mcq_generation_prompt(self, specialization, difficulty, num_questions):
        new_prompt  = f"""Generate {num_questions} unambiguous, unbiased, and verifiable multiple-choice questions about {specialization} at a {difficulty} difficulty level in English. 
        Cover a wide range of subtopics within the specialization, including both theoretical concepts and practical real-world applications.
        The questions should reflect the variety of topics that may appear in competitive examinations and educational assessments.
        
        Ensure that each question is based on factual information that can be verified using reliable sources such as textbooks, academic papers, or well-known websites (e.g., government or university websites). Avoid speculative or opinion-based content.
        
        All questions must be unambiguous, with clear language that leaves no room for misinterpretation.
        
        Ensure the questions and options are unbiased, free from any cultural, racial, or gender bias, and are appropriate for diverse audiences.

        Each question MUST be unique, and have exactly 4 options (A, B, C, D), with only one correct answer. Format each question as follows:

        Question: [Question text]
        A. [Option A]
        B. [Option B]
        C. [Option C]
        D. [Option D]
        Correct Answer: [A/B/C/D]

        Ensure that the options are plausible, and avoid trivial or obviously incorrect answers. Include real-world context where relevant, and ensure that all questions are diverse, covering different aspects of {specialization}."""

        return new_prompt
    
    def get_text_translation_prompt(self, text, language):
        new_prompt = f"Translate the following text to {language}:\n\n{text}"
        return new_prompt

    def get_explain_answer_prompt(self, question, options, correct_answer):

        if options:
            new_prompt = f"""Explain the following multiple-choice question and why the correct answer is {correct_answer} in English:
        
            {question}

            {options}
        
            Please provide a detailed explanation, including any background information or context relevant to the question."""
        else:
            new_prompt = f"""Explain the following question and why the correct answer is {correct_answer} in English:
        
            {question}
        
            Please provide a detailed explanation, including any background information or context relevant to the question."""
    
        return new_prompt
    
    def get_prerequisites_prompt(self, question, options):

        if options:
            new_prompt = f"""Provide detailed background material that would help a student understand the following question and its options. 
            The material should cover fundamental concepts, definitions, and any necessary background knowledge related to the question and its options.

            Question: {question}

            {options}
        
            The explanation should be detailed, yet clear and beginner-friendly, aimed at a student who is not familiar with the topic."""

        else:
            new_prompt = f"""Provide detailed background material that would help a student understand the following question. 
            The material should cover fundamental concepts, definitions, and any necessary background knowledge related to the question.

            Question: {question}

            The explanation should be detailed, yet clear and beginner-friendly, aimed at a student who is not familiar with the topic."""

        return new_prompt
    
    def get_similar_question_generation_prompt(self, question, num_questions=1, with_options=True):  # Added default value for with_options
        if with_options:
            new_prompt = f"""Generate {num_questions} unique, unambiguous, and unbiased multiple-choice questions based on the following question. 
            The new question should cover a similar topic or idea but must not be a duplicate or semantically similar to the original question.
            It should enhance the user's understanding of the topic.

            Original Question: {question}
        
            Each question MUST have exactly 4 options (A, B, C, D), with only one correct answer. 
            Format the output strictly as follows:

            Question: [Question text]
            A. [Option A]
            B. [Option B]
            C. [Option C]
            D. [Option D]
            Correct Answer: [A/B/C/D]

            Ensure the correct answer is only a letter (A, B, C, D) and no explanation is included."""
        else:
            new_prompt = f"""Generate {num_questions} unique, unambiguous, and unbiased questions based on the following question. 
            The new question should cover a similar topic or idea but must not be a duplicate or semantically similar to the original question.
            It should enhance the user's understanding of the topic.

            Original Question: {question} """

        return new_prompt  # Fixed indentation and added return statement
    
    def get_true_false_question_generation_prompt(self, statement, num_questions=1):  # New method for True/False questions
        new_prompt = f"""Generate {num_questions} unique, unambiguous, and unbiased True/False questions based on the following statement. 
        Each question should clearly indicate whether the statement is true or false, and provide a brief explanation for the answer.

        Statement: {statement}

        Format the output strictly as follows:

        Question: [Is the statement true or false?]
        Answer: [True/False]
        Explanation: [Brief explanation of the answer]"""

        return new_prompt  # Return the generated prompt
    
    def get_yes_no_question_generation_prompt(self, statement, num_questions=1):  # New method for Yes/No questions
        new_prompt = f"""Generate {num_questions} unique, unambiguous, and unbiased Yes/No questions based on the following statement. 
        Each question should clearly indicate whether the answer is yes or no, and provide a brief explanation for the answer.

        Statement: {statement}

        Format the output strictly as follows:

        Question: [Is the statement true or false?]
        Answer: [Yes/No]
        Explanation: [Brief explanation of the answer]"""

        return new_prompt  # Return the generated prompt
    
if __name__ == "__main__":
    prompt_builder = PromptBuilder()
    
    # Build a multiple-choice question prompt
    prompt = prompt_builder.get_mcq_generation_prompt("Physics", "Medium", 5)
    print("MCQ Prompt:\n", prompt_builder)
    
    # Build a translation prompt
    prompt = prompt_builder.get_text_translation_prompt("Hello, how are you?", "Hindi")
    print("\nTranslation Prompt:\n", prompt_builder)
    
    # Build an explanation prompt
    prompt = prompt_builder.get_explain_answer_prompt("What is the force of gravity?", ["9.8 m/s²", "9.81 m/s²", "10 m/s²", "8.5 m/s²"], "B")
    print("\nExplanation Prompt:\n", prompt)
    
    # Build a prerequisite prompt
    prompt = prompt_builder.get_prerequisites_prompt("What is Newton's second law?", ["F=ma", "E=mc²", "F=mv", "F=mg"])
    print("\nPrerequisite Prompt:\n", prompt)
    
    # Build a similar question prompt
    prompt = prompt_builder.get_similar_question_generation_prompt("What is the speed of light?")
    print("\nSimilar Question Prompt:\n", prompt)
