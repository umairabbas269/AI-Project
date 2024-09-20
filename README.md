
# MCQ Generator

MCQ Generator is a **Streamlit-based web application** that utilizes OpenAI's GPT models to generate multiple-choice questions (MCQs) on a wide range of topics. The tool is designed to assist educators, students, and quiz enthusiasts in creating custom quizzes with detailed explanations.

## Features

- **Generate MCQs** based on user-specified topics and difficulty levels.
- Support for multiple GPT models (GPT-4, GPT-4o, GPT-4o-mini).
- **Customizable** number of questions and token limits for each generation.
- **Interactive answering** with immediate feedback on responses.
- Detailed **explanations** provided for each question.
- Option to **save generated questions** as JSON files for future use.

## Prerequisites

Before you start using MCQ Generator, ensure that your environment meets the following requirements:

- **Python 3.7+**
- An **OpenAI API key**

## Installation

To set up MCQ Generator on your local machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/csv610/mcq_generator.git
   cd mcq-generator
   ```

2. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key as an environment variable:**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

To launch the MCQ Generator app, run the following command:

```bash
streamlit run app.py
```

Once the application is running, open your browser and navigate to [http://localhost:8501](http://localhost:8501).

### How to Use

1. **Select the GPT model** from the dropdown menu.
2. **Enter the topic** or specialization for the MCQs.
3. **Choose the difficulty level** (Easy, Medium, Hard).
4. **Specify the number of questions** you want to generate.
5. Adjust the **max tokens** for both question generation and explanation if required.
6. Click on **"Generate Questions"** to create your MCQs.
7. **Answer the questions** and check your responses.
8. Use the **"Explain Answer"** button for detailed explanations.
9. Click **"Save Questions to JSON"** to export the generated quiz for future use.

## Contributing

Contributions are welcome! If you'd like to contribute to the development of MCQ Generator, please submit a Pull Request. We appreciate your efforts to make this project better.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

- This project uses the **OpenAI API** to generate questions and explanations.
- Built using **Streamlit** for the web interface.

---

Feel free to reach out with any issues or feature requests!
