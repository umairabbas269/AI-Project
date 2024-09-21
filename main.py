import streamlit as st
import json
from question_generator import QuestionGenerator
from question_translator import QuestionTranslator
from question_prerequisite import QuestionPrerequisite
from similar_question_generator import SimilarQuestionGenerator
from llm_model import OpenAIModel
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, filename='mcqapp.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

# Function to save questions to a JSON file
def save_to_json_in_english(filename, questions):
    with open(filename, 'w') as f:
        json.dump(questions, f)

# Main Streamlit Application
def main():
    st.sidebar.title("MCQ Generator")

    # Model selection
    model_name = st.sidebar.selectbox("Select Model", ["gpt-4o-mini", "gpt-4o", "gpt-4"])
    model = OpenAIModel(model_name)

    language = st.sidebar.selectbox("Select Language", ["English", "Hindi"])
    
    # User inputs
    specialization = st.sidebar.text_input("Enter the specialization:")
    difficulty = st.sidebar.selectbox("Select difficulty level:", ["Easy", "Medium", "Hard"])
    num_questions = st.sidebar.number_input("Number of questions:", min_value=1, max_value=100, value=5)
    max_tokens_question = st.sidebar.number_input("Max Tokens for Question Generation", min_value=100, max_value=4000, value=3000)
    max_tokens_explanation = st.sidebar.number_input("Max Tokens for Explanation", min_value=100, max_value=4000, value=1500)

    # Initialize session state
    if "original_questions" not in st.session_state:
        st.session_state.original_questions = {}
    if "last_index" not in st.session_state:
        st.session_state.last_index = {}

    # Generate Questions
    if st.sidebar.button("Generate Questions"):
        if not specialization or not difficulty or not language:
            st.sidebar.error("Please fill out all fields.")
        else:
            # Initialize or increment the index for the specialization
            if specialization not in st.session_state.last_index:
                st.session_state.last_index[specialization] = 0
            else:
                st.session_state.last_index[specialization] += 1

            # Clear previous questions for the specialization if generating new ones
            if specialization not in st.session_state.original_questions:
                st.session_state.original_questions[specialization] = {}

            with st.spinner("Generating questions..."):
                question_generator = QuestionGenerator(model)
                questions = question_generator.generate_questions(specialization, difficulty, num_questions, max_tokens_question)

                for index, raw_q in enumerate(questions, start=1):
                    question_text, options, correct_answer = question_generator.parse_question(raw_q)
                    if question_text and options:
                        question_id = f"{specialization}_{st.session_state.last_index[specialization] + index}"
                        # Store the original English questions
                        st.session_state.original_questions[specialization][question_id] = {
                            "question": question_text,
                            "options": options,
                            "correct_answer": correct_answer,
                            "translations": {}
                        }

                # Immediately translate to the selected language
                if language != "English":
                    question_translator = QuestionTranslator(model)
                    for q_id, q in st.session_state.original_questions[specialization].items():
                        translated_question = question_translator.translate_text(q['question'], language)
                        translated_options = [question_translator.translate_text(opt, language) for opt in q['options']]
                        q['translations'][language] = {
                            "question": translated_question,
                            "options": translated_options
                        }
                logging.info(f"{num_questions} questions generated.")

    # Save to JSON (always in English)
    if st.sidebar.button("Save Questions to JSON"):
        if st.session_state.get("original_questions"):
            filename = "questions.json"  # Updated to remove timestamp
            # Prepare the data structure for saving
            questions_to_save = {}
            for spec, questions in st.session_state.original_questions.items():
                questions_to_save[spec] = {
                    "questions": [
                        {
                            "id": q_id,
                            "question": q["question"],
                            "options": q["options"],
                            "correct_answer": q["correct_answer"],
                            "translations": q["translations"]
                        } for q_id, q in questions.items()
                    ]
                }
            save_to_json_in_english(filename, questions_to_save)
            st.sidebar.success(f"Questions saved as {filename}.")
        else:
            st.sidebar.error("No questions to save.")

    # Display Questions and Check Answer
    if st.session_state.get("original_questions"):
        for specialization, questions in st.session_state.original_questions.items():
            for i, (q_id, q) in enumerate(questions.items(), start=1):
                st.subheader(f"Question {i} (ID: {q_id})")
                st.write(q["question"])  # Display the original question

                # Display options using radio buttons
                user_answer = st.radio("Options", q["options"], key=f"q{i}")

                # Check Answer
                if st.button(f"Check Answer for Question {i}"):
                    if user_answer == q["options"][ord(q["correct_answer"]) - ord("A")]:
                        st.success("Correct!")
                    else:
                        st.error(f"Incorrect. The correct answer is {q['correct_answer']}: {q['options'][ord(q['correct_answer']) - ord('A')]}")

                # Explain Answer
                if st.button(f"Explain Answer for Question {i}"):
                    with st.spinner(f"Explaining answer for Question {i}..."):
                        prompt_builder = PromptBuilder()
                        prompt_builder.build_explain_answer_prompt(q["question"], q["correct_answer"], q["options"])
                        prompt = prompt_builder.get_prompt("explain_answer")

                        response = model.get_response(
                            messages=[
                                {"role": "system", "content": "You are an expert assistant providing detailed explanations for multiple-choice questions."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=max_tokens_explanation,
                            temperature=0.7,
                        )
                        explanation = response['choices'][0]['message']['content'].strip()

                        # Display explanation
                        st.write(explanation)

                # Prerequisite Background Material
                if st.button(f"Prerequisite for Question {i}"):
                    with st.spinner(f"Fetching prerequisite material for Question {i}..."):
                        question_prerequisite = QuestionPrerequisite(model)
                        prerequisite_material = question_prerequisite.fetch_prerequisite(q["question"], q["options"])
                        st.write(prerequisite_material)

                # Generate Similar Question
                if st.button(f"Generate Similar Question for Question {i}"):
                    with st.spinner(f"Generating similar question for Question {i}..."):
                        similar_question_generator = SimilarQuestionGenerator(model)
                        similar_question = similar_question_generator.generate_similar_question(q["question"])
                        st.write(similar_question)

if __name__ == "__main__":
    main()
