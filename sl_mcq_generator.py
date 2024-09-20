import streamlit as st
import logging
import os
import json
import re
from datetime import datetime
import ollama  # Importing the Ollama library
import rocksdb  # Importing RocksDB

# Initialize logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI client (API key fetched from environment variable)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

# Initialize RocksDB
db = rocksdb.DB("cache.db", rocksdb.Options(create_if_missing=True))

# Function to load from cache
def load_from_cache(key):
    value = db.get(key.encode('utf-8'))
    return value.decode('utf-8') if value else None

# Function to save to cache
def save_to_cache(key, value):
    db.put(key.encode('utf-8'), value.encode('utf-8'))

# Define a class to manage prompts
class PromptManager:
    @staticmethod
    def generate_mcq(num_questions, specialization, difficulty):
        return f"""Generate {num_questions} unambiguous, unbiased, and verifiable multiple-choice questions about {specialization} at a {difficulty} difficulty level in English. 
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

    @staticmethod
    def explain_answer(question, correct_answer, options):
        options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
        return f"""Explain the following multiple-choice question and why the correct answer is {correct_answer} in English:
        {question}

        {options_text}
        
        Please provide a detailed explanation, including any background information or context relevant to the question."""

    @staticmethod
    def fetch_prerequisite(question, options):
        options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
        return f"""Provide a detailed background material that would help a student understand the following question and its options. 
        The material should cover fundamental concepts, definitions, and any necessary background knowledge related to the question and its options.

        Question: {question}

        {options_text}
        
        The explanation should be detailed, yet clear and beginner-friendly, aimed at a student who is not familiar with the topic."""

    @staticmethod
    def translate_text(text, language):
        return f"Translate the following text to {language}:\n\n{text}"

# Define an interface for the model
class ModelInterface:
    def call_api(self, model, messages, max_tokens):
        raise NotImplementedError

    def generate_mcq(self, model, specialization, difficulty, num_questions, max_tokens):
        raise NotImplementedError

    def explain_answer(self, model, question, correct_answer, options, max_tokens):
        raise NotImplementedError

    def fetch_prerequisite(self, model, question, options, max_tokens):
        raise NotImplementedError

    def translate_text(self, model, text, language, max_tokens):
        raise NotImplementedError

# Implement the OpenAI model
class OpenAIModel(ModelInterface):
    def __init__(self, client):
        self.client = client

    def call_api(self, model, messages, max_tokens):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                n=1,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip().split("\n\n")
        except Exception as e:
            logging.error(f"OpenAI API call error: {str(e)}")
            return None

    def generate_mcq(self, model, specialization, difficulty, num_questions, max_tokens):
        prompt = PromptManager.generate_mcq(num_questions, specialization, difficulty)
        messages = [{"role": "user", "content": prompt}]
        return self.call_api(model, messages, max_tokens)

    def explain_answer(self, model, question, correct_answer, options, max_tokens):
        prompt = PromptManager.explain_answer(question, correct_answer, options)
        messages = [{"role": "user", "content": prompt}]
        return self.call_api(model, messages, max_tokens)

    def fetch_prerequisite(self, model, question, options, max_tokens):
        prompt = PromptManager.fetch_prerequisite(question, options)
        messages = [{"role": "user", "content": prompt}]
        return self.call_api(model, messages, max_tokens)

    def translate_text(self, model, text, language, max_tokens):
        prompt = PromptManager.translate_text(text, language)
        messages = [{"role": "user", "content": prompt}]
        return self.call_api(model, messages, max_tokens)

# Implement the Ollama model
class OllamaModel(ModelInterface):
    def call_api(self, model, prompt, max_tokens):
        try:
            response = ollama.chat(model=model, prompt=prompt, max_tokens=max_tokens)
            return response.strip().split("\n\n")
        except Exception as e:
            logging.error(f"Ollama API call error: {str(e)}")
            return None

    def generate_mcq(self, model, specialization, difficulty, num_questions, max_tokens):
        prompt = PromptManager.generate_mcq(num_questions, specialization, difficulty)
        return self.call_api(model, prompt, max_tokens)

    def explain_answer(self, model, question, correct_answer, options, max_tokens):
        prompt = PromptManager.explain_answer(question, correct_answer, options)
        return self.call_api(model, prompt, max_tokens)

    def fetch_prerequisite(self, model, question, options, max_tokens):
        prompt = PromptManager.fetch_prerequisite(question, options)
        return self.call_api(model, prompt, max_tokens)

    def translate_text(self, model, text, language, max_tokens):
        prompt = PromptManager.translate_text(text, language)
        return self.call_api(model, prompt, max_tokens)

# Initialize a global dictionary to keep track of question ID counters for each specialization
question_id_counters = {}

# Modify the parse_question function to include a unique ID based on specialization
def parse_question(response_text, specialization):
    # Initialize the counter for the specialization if it doesn't exist
    if specialization not in question_id_counters:
        question_id_counters[specialization] = 1
    else:
        question_id_counters[specialization] += 1  # Increment the counter for the specialization

    question_match = re.search(r'Question: (.*?)\n', response_text, re.DOTALL)
    question_text = question_match.group(1) if question_match else None
    options = re.findall(r'[A-D]\. (.*?)\n', response_text)
    correct_answer_match = re.search(r'Correct Answer: ([A-D])', response_text)
    correct_answer = correct_answer_match.group(1) if correct_answer_match else None
    
    # Create a unique ID based on specialization and the current counter
    unique_id = f"{specialization}_{question_id_counters[specialization]}"
    
    return unique_id, question_text, options, correct_answer

# Main Streamlit Application
def main():
    st.sidebar.title("MCQ Generator")
    model_choice = st.sidebar.selectbox("Select Model", ["OpenAI", "Ollama"])
    
    if model_choice == "OpenAI":
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        model_interface = OpenAIModel(openai_client)
    else:
        model_interface = OllamaModel()

    specialization = st.sidebar.text_input("Enter the specialization:")
    difficulty = st.sidebar.selectbox("Select difficulty level:", ["Easy", "Medium", "Hard"])
    num_questions = st.sidebar.number_input("Number of questions:", min_value=1, max_value=100, value=5)
    max_tokens = st.sidebar.number_input("Max Tokens", min_value=100, max_value=4000, value=3000)

    if st.sidebar.button("Generate Questions"):
        if not specialization or not difficulty:
            st.sidebar.error("Please fill out all fields.")
        else:
            raw_questions = model_interface.generate_mcq(model_choice, specialization, difficulty, num_questions, max_tokens)
            if raw_questions:
                st.session_state.original_questions = [parse_question(q, specialization) for q in raw_questions]
                logging.info(f"{num_questions} questions generated.")
            else:
                st.error("Failed to generate questions.")

    if st.session_state.get("original_questions"):
        for i, (unique_id, question, options, correct_answer) in enumerate(st.session_state.original_questions, start=1):
            st.subheader(f"Question {i} (ID: {unique_id})")
            st.write(question)
            user_answer = st.radio("Options", options, key=f"q{i}")

            if st.button(f"Check Answer for Question {i}"):
                if user_answer == options[ord(correct_answer) - ord("A")]:
                    st.success("Correct!")
                else:
                    st.error(f"Incorrect. The correct answer is {correct_answer}: {options[ord(correct_answer) - ord('A')]}")
            
            if st.button(f"Explain Answer for Question {i}"):
                # Create a unique key for the cache based on question ID and correct answer
                cache_key = f"explanation_{unique_id}_{correct_answer}"
                explanation = load_from_cache(cache_key)
                if explanation is None:
                    explanation = model_interface.explain_answer(model_choice, question, correct_answer, options, max_tokens)
                    save_to_cache(cache_key, explanation)  # Cache the fetched explanation
                
                st.write(explanation)

            if st.button(f"Prerequisite for Question {i}"):
                # Create a unique key for the cache based on question ID and options
                cache_key = f"prerequisite_{unique_id}_{'_'.join(options)}"
                prerequisite_material = load_from_cache(cache_key)
                if prerequisite_material is None:
                    prerequisite_material = model_interface.fetch_prerequisite(model_choice, question, options, max_tokens)
                    save_to_cache(cache_key, prerequisite_material)  # Cache the fetched material
                
                st.write(prerequisite_material)

            if st.button(f"Translate Question for Question {i}"):
                language = st.selectbox("Select Language", ["English", "Hindi"])
                # Create a unique key for the cache based on question ID and language
                cache_key = f"translation_{unique_id}_{language}"
                translation = load_from_cache(cache_key)
                if translation is None:
                    translation = model_interface.translate_text(model_choice, question, language, max_tokens)
                    save_to_cache(cache_key, translation)  # Cache the fetched translation
                
                st.write(translation)

if __name__ == "__main__":
    main()
