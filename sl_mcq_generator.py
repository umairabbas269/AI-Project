import streamlit as st
import re
import os
import time
from PyPDF2 import PdfReader
from groq import Groq
from dotenv import load_dotenv
import logging

# Initialize environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='question_generator.log'
)

# Initialize Groq client
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    st.error(f"Failed to initialize Groq client: {str(e)}")
    st.stop()

# Session state initialization
if "app_state" not in st.session_state:
    st.session_state.app_state = {
        "questions": [],
        "student_answers": {},
        "pdf_text": "",
        "current_difficulty": "Medium",
        "question_type": "MCQ",
        "pdf_uploaded": False,
        "generation_count": 0  # Track generation attempts
    }

def extract_text_from_pdf(uploaded_file):
    """Faster PDF text extraction with better formatting"""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            # Improved text cleaning
            page_text = ' '.join(page_text.split())  # Remove extra whitespace
            page_text = re.sub(r'(?<=\w)-\s+(?=\w)', '', page_text)  # Fix hyphenated words
            text += page_text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"PDF read error: {str(e)}")
        logging.error(f"PDF extraction failed: {str(e)}")
        return ""

def parse_questions(raw_text, question_type):
    """More reliable parsing with multiple fallback patterns"""
    questions = []
    try:
        if question_type == "MCQ":
            # Enhanced MCQ parsing
            pattern = r'(?:Question|Q)[:\s]*(.*?)\n(A[\.:].*?)\n(B[\.:].*?)\n(C[\.:].*?)\n(D[\.:].*?)\n(?:Correct Answer|Answer)[:\s]*([A-D])'
            matches = re.finditer(pattern, raw_text, re.IGNORECASE|re.DOTALL)
            for match in matches:
                questions.append({
                    "type": "MCQ",
                    "question": match.group(1).strip(),
                    "options": [
                        match.group(2).strip()[3:],  # Remove "A. " prefix
                        match.group(3).strip()[3:],
                        match.group(4).strip()[3:],
                        match.group(5).strip()[3:]
                    ],
                    "answer": match.group(6).upper(),
                    "difficulty": st.session_state.app_state["current_difficulty"]
                })

        elif question_type == "True/False":
            # More robust True/False parsing
            pattern = r'(?:Statement|S)[:\s]*(.*?)\n(?:Correct Answer|Answer)[:\s]*(True|False)'
            matches = re.finditer(pattern, raw_text, re.IGNORECASE|re.DOTALL)
            for match in matches:
                questions.append({
                    "type": "True/False",
                    "question": match.group(1).strip(),
                    "answer": match.group(2).capitalize(),
                    "difficulty": st.session_state.app_state["current_difficulty"]
                })

        elif question_type == "Essay":
            # Improved Essay parsing
            pattern = r'(?:Question|Q)[:\s]*(.*?)(?:\n(?:Expected Length|Length)[:\s]*(.*?))?(?=\n\n|$)'
            matches = re.finditer(pattern, raw_text, re.IGNORECASE|re.DOTALL)
            for match in matches:
                questions.append({
                    "type": "Essay",
                    "question": match.group(1).strip(),
                    "expected_length": match.group(2).strip() if match.group(2) else "2-3 paragraphs",
                    "difficulty": st.session_state.app_state["current_difficulty"]
                })

    except Exception as e:
        logging.error(f"Parsing failed: {str(e)}")
    
    return questions

def generate_questions(text_chunk, question_type, count=3):
    """Faster generation with optimized prompts"""
    try:
        # Optimized prompts for each type
        prompts = {
            "MCQ": f"""Generate exactly {count} multiple-choice questions from the text.
            Format each EXACTLY like this:
            Question: [question]
            A. [option A]
            B. [option B]
            C. [option C]
            D. [option D]
            Correct Answer: [A-D]
            Difficulty: {st.session_state.app_state["current_difficulty"]}""",
            
            "True/False": f"""Generate exactly {count} true/false statements from the text.
            Format each EXACTLY like this:
            Statement: [statement]
            Correct Answer: True/False
            Difficulty: {st.session_state.app_state["current_difficulty"]}""",
            
            "Essay": f"""Generate exactly {count} essay questions from the text.
            Format each EXACTLY like this:
            Question: [question]
            Expected Length: [length]
            Difficulty: {st.session_state.app_state["current_difficulty"]}"""
        }

        start_time = time.time()
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # More reliable model
            messages=[{
                "role": "system", 
                "content": f"You are an expert at creating {question_type} questions. Follow the format strictly."
            }, {
                "role": "user", 
                "content": f"Text:\n{text_chunk[:3000]}\n\n{prompts[question_type]}"
            }],
            temperature=0.7,
            max_tokens=4000  # Increased token limit
        )
        
        logging.info(f"Generation took {time.time()-start_time:.2f} seconds")
        return parse_questions(response.choices[0].message.content, question_type)
    
    except Exception as e:
        logging.error(f"Generation failed: {str(e)}")
        st.error(f"Question generation error: {str(e)}")
        return []

def main():
    st.set_page_config(page_title="Question Generator Pro", layout="wide")
    st.title("📝 AI Question Generator Pro")
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # PDF Upload with progress
        pdf_file = st.file_uploader("Upload PDF Textbook", type=["pdf"])
        if pdf_file:
            with st.spinner("Processing PDF..."):
                st.session_state.app_state["pdf_text"] = extract_text_from_pdf(pdf_file)
                if st.session_state.app_state["pdf_text"]:
                    st.session_state.app_state["pdf_uploaded"] = True
                    st.success("PDF processed successfully!")
                else:
                    st.session_state.app_state["pdf_uploaded"] = False

        # Question type selection
        question_type = st.radio(
            "Question Type",
            ["MCQ", "True/False", "Essay"],
            index=["MCQ", "True/False", "Essay"].index(st.session_state.app_state["question_type"])
        )
        st.session_state.app_state["question_type"] = question_type
        
        # Generation parameters
        col1, col2 = st.columns(2)
        with col1:
            difficulty = st.select_slider(
                "Difficulty", 
                options=["Easy", "Medium", "Hard"],
                value=st.session_state.app_state["current_difficulty"]
            )
            st.session_state.app_state["current_difficulty"] = difficulty
            
        with col2:
            num_questions = st.slider("Number of Questions", 1, 10, 5)
        
        # Enhanced generate button with attempt tracking
        if st.button("✨ Generate Questions", type="primary", use_container_width=True):
            if not st.session_state.app_state["pdf_uploaded"]:
                st.error("Please upload a valid PDF first")
            else:
                with st.spinner(f"Generating {num_questions} {question_type} questions..."):
                    st.session_state.app_state["generation_count"] += 1
                    questions = generate_questions(
                        text_chunk=st.session_state.app_state["pdf_text"],
                        question_type=question_type,
                        count=num_questions
                    )
                    
                    if len(questions) < num_questions:
                        st.warning(f"Only generated {len(questions)}/{num_questions} questions. Try generating again.")
                    
                    st.session_state.app_state["questions"] = questions
                    st.session_state.app_state["last_generated"] = time.time()

    # Main display area
    tab1, tab2 = st.tabs(["📚 Questions", "📊 Analytics"])
    
    with tab1:
        if st.session_state.app_state["questions"]:
            st.subheader(f"Generated {st.session_state.app_state['question_type']} Questions")
            
            for i, q in enumerate(st.session_state.app_state["questions"]):
                with st.expander(f"Q{i+1}: {q['question']}", expanded=True):
                    if q["type"] == "MCQ":
                        user_ans = st.radio(
                            "Select your answer:",
                            q["options"],
                            key=f"mcq_{i}",
                            index=None
                        )
                        if st.button("Check", key=f"check_mcq_{i}"):
                            correct_idx = ord(q['answer']) - ord('A')
                            is_correct = (user_ans == q["options"][correct_idx])
                            st.session_state.app_state["student_answers"][f"q{i}"] = {
                                "correct": is_correct,
                                "question": q["question"],
                                "type": q["type"]
                            }
                            st.success("✅ Correct!" if is_correct else f"❌ Incorrect (Answer: {q['answer']})")
                    
                    elif q["type"] == "True/False":
                        user_ans = st.radio(
                            "True or False?",
                            ["True", "False"],
                            key=f"tf_{i}",
                            index=None
                        )
                        if st.button("Check", key=f"check_tf_{i}"):
                            is_correct = (user_ans == q["answer"])
                            st.session_state.app_state["student_answers"][f"q{i}"] = {
                                "correct": is_correct,
                                "question": q["question"],
                                "type": q["type"]
                            }
                            st.success("✅ Correct!" if is_correct else f"❌ Incorrect (Answer: {q['answer']})")
                    
                    elif q["type"] == "Essay":
                        st.write(f"**Expected Length:** {q.get('expected_length', '2-3 paragraphs')}")
                        user_response = st.text_area("Your answer", key=f"essay_{i}", height=200)
                        if st.button("Submit", key=f"submit_essay_{i}"):
                            st.session_state.app_state["student_answers"][f"q{i}"] = {
                                "correct": True,
                                "question": q["question"],
                                "type": q["type"],
                                "response": user_response
                            }
                            st.success("📝 Essay submitted!")
        
        elif st.session_state.app_state["pdf_uploaded"]:
            st.info("Click 'Generate Questions' to create questions")
        else:
            st.info("Please upload a PDF textbook to begin")
    
    with tab2:
        if st.session_state.app_state["student_answers"]:
            correct = sum(1 for ans in st.session_state.app_state["student_answers"].values() if ans["correct"])
            total = len(st.session_state.app_state["student_answers"])
            st.metric("Overall Accuracy", f"{correct/total*100:.1f}%")
            
            st.write("### Question Types Generated")
            st.write(f"- MCQs: {sum(1 for q in st.session_state.app_state['questions'] if q['type']=='MCQ')}")
            st.write(f"- True/False: {sum(1 for q in st.session_state.app_state['questions'] if q['type']=='True/False')}")
            st.write(f"- Essays: {sum(1 for q in st.session_state.app_state['questions'] if q['type']=='Essay')}")
        else:
            st.warning("No answers recorded yet")

if __name__ == "__main__":
    main()