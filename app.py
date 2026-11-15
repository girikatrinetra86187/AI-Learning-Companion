
import streamlit as st
from groq import Groq
from pypdf import PdfReader
import io

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide"
)

# -------------------------------
# CUSTOM DESIGN
# -------------------------------

st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}
.title {
    text-align: center;
    color: #244b87;
    font-size: 38px;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 17px;
}
.stButton button {
    background-color: #2457a7;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# API CONNECTION
# -------------------------------

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error(
        "Groq API key not found. "
        "Please check .streamlit/secrets.toml"
    )
    st.stop()

MODEL = "openai/gpt-oss-20b"

def ask_ai(prompt, system_prompt="You are a helpful AI study assistant."):
    """Send a prompt to Groq and return the response."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5,
        max_tokens=2000
    )

    return response.choices[0].message.content

# -------------------------------
# READ PDF OR TEXT FILE
# -------------------------------

def read_uploaded_file(uploaded_file):

    if uploaded_file is None:
        return ""

    if uploaded_file.name.lower().endswith(".txt"):
        return uploaded_file.getvalue().decode(
            "utf-8", errors="replace"
        )

    if uploaded_file.name.lower().endswith(".pdf"):
        reader = PdfReader(
            io.BytesIO(uploaded_file.getvalue())
        )

        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages)

    return ""

# -------------------------------
# HEADER
# -------------------------------

st.markdown(
    '<div class="title">🎓 AI Study Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your personal AI-powered learning companion'
    '</div>',
    unsafe_allow_html=True
)

st.divider()

st.success(
    "Welcome! Ask questions, summarize notes, "
    "understand topics and generate quizzes."
)

# -------------------------------
# SIDEBAR
# -------------------------------

st.sidebar.title("🎓 Study Menu")

st.sidebar.write(
    "Choose a learning tool from the tabs."
)

if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.divider()

st.sidebar.info(
    "Developed using Python, Streamlit and Groq AI."
)

# -------------------------------
# SESSION STORAGE
# -------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# APPLICATION TABS
# -------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "💬 AI Chat",
    "📝 Summarizer",
    "📚 Topic Explainer",
    "❓ Quiz Generator"
])

# -------------------------------
# TAB 1: AI CHATBOT
# -------------------------------

with tab1:

    st.subheader("Ask Your AI Study Assistant")

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask any study-related question..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:
                    answer = ask_ai(
                        question,
                        "You are an educational AI assistant. "
                        "Explain concepts in simple English "
                        "with examples and clear steps."
                    )

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:
                    st.error(f"AI Error: {e}")

# -------------------------------
# TAB 2: NOTES SUMMARIZER
# -------------------------------

with tab2:

    st.subheader("Summarize Your Study Notes")

    uploaded_file = st.file_uploader(
        "Upload PDF or TXT notes",
        type=["pdf", "txt"],
        key="summary_file"
    )

    if st.button("Generate Summary"):

        if uploaded_file is None:
            st.warning("Please upload a file first.")

        else:

            with st.spinner("Reading and summarizing..."):

                try:
                    notes = read_uploaded_file(
                        uploaded_file
                    )

                    if not notes.strip():
                        st.warning(
                            "No readable text found in this file."
                        )
                    else:
                        summary = ask_ai(
                            "Summarize these study notes "
                            "using headings and important points:\n\n"
                            + notes[:20000],
                            "You are an expert study notes summarizer."
                        )

                        st.markdown("### Your Summary")
                        st.markdown(summary)

                        st.download_button(
                            "Download Summary",
                            summary,
                            file_name="study_summary.txt"
                        )

                except Exception as e:
                    st.error(f"Error: {e}")

# -------------------------------
# TAB 3: TOPIC EXPLAINER
# -------------------------------

with tab3:

    st.subheader("Understand Difficult Topics")

    topic = st.text_input(
        "Enter a topic you want to understand"
    )

    level = st.selectbox(
        "Choose explanation level",
        [
            "Beginner",
            "Intermediate",
            "Advanced",
            "Exam Preparation"
        ]
    )

    if st.button("Explain Topic"):

        if not topic.strip():
            st.warning("Please enter a topic.")

        else:

            with st.spinner("Preparing explanation..."):

                try:
                    explanation = ask_ai(
                        f"Explain {topic} at {level} level. "
                        "Use simple English, examples, "
                        "headings and important points.",
                        "You are a patient computer science tutor."
                    )

                    st.markdown("### Topic Explanation")
                    st.markdown(explanation)

                except Exception as e:
                    st.error(f"Error: {e}")

# -------------------------------
# TAB 4: QUIZ GENERATOR
# -------------------------------

with tab4:

    st.subheader("Generate Practice Questions")

    quiz_topic = st.text_input(
        "Enter quiz topic"
    )

    number = st.selectbox(
        "Number of questions",
        [5, 10, 15, 20]
    )

    difficulty = st.selectbox(
        "Select difficulty",
        ["Easy", "Medium", "Hard"]
    )

    if st.button("Generate Quiz"):

        if not quiz_topic.strip():
            st.warning("Please enter a quiz topic.")

        else:

            with st.spinner("Creating your quiz..."):

                try:
                    quiz = ask_ai(
                        f"Create {number} multiple-choice questions "
                        f"on {quiz_topic}. Difficulty: {difficulty}. "
                        "Give four options (A, B, C, D) for each "
                        "question. At the end, provide the correct "
                        "answers with short explanations.",
                        "You are an educational quiz generator."
                    )

                    st.markdown("### Your Practice Quiz")
                    st.markdown(quiz)

                    st.download_button(
                        "Download Quiz",
                        quiz,
                        file_name="practice_quiz.txt"
                    )

                except Exception as e:
                    st.error(f"Error: {e}")

# -------------------------------
# FOOTER
# -------------------------------

st.divider()

st.markdown(
    "<center>Made with ❤️ using Python, Streamlit "
    "and Groq AI</center>",
    unsafe_allow_html=True
)