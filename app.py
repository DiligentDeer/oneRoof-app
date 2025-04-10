import streamlit as st
import pandas as pd
import plotly.express as px
import json
import time
from datetime import datetime
import os
import ast
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')  # Default password if not set
QUIZ_TIME_LIMIT = 30  # minutes

# File paths - use absolute paths for deployment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ATTEMPTS_FILE = os.path.join(DATA_DIR, 'Quiz Attempts.csv')
QUESTIONS_FILE = os.path.join(DATA_DIR, 'Questions.csv')
ANSWERS_FILE = os.path.join(DATA_DIR, 'Answers.csv')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Load quiz data from CSV
def load_quiz_data():
    try:
        # Check if Questions.csv exists, if not create it with sample data
        if not os.path.exists(QUESTIONS_FILE):
            sample_questions = pd.DataFrame([
                {
                    'id': 1,
                    'question': 'What is the capital of France?',
                    'options': "['London', 'Berlin', 'Paris', 'Madrid']",
                    'correct_answer': 'Paris'
                },
                {
                    'id': 2,
                    'question': 'Which planet is known as the Red Planet?',
                    'options': "['Venus', 'Mars', 'Jupiter', 'Saturn']",
                    'correct_answer': 'Mars'
                },
                {
                    'id': 3,
                    'question': 'What is the largest mammal in the world?',
                    'options': "['African Elephant', 'Blue Whale', 'Giraffe', 'Hippopotamus']",
                    'correct_answer': 'Blue Whale'
                },
                {
                    'id': 4,
                    'question': 'Who painted the Mona Lisa?',
                    'options': "['Vincent van Gogh', 'Pablo Picasso', 'Leonardo da Vinci', 'Michelangelo']",
                    'correct_answer': 'Leonardo da Vinci'
                },
                {
                    'id': 5,
                    'question': 'What is the chemical symbol for gold?',
                    'options': "['Ag', 'Fe', 'Au', 'Cu']",
                    'correct_answer': 'Au'
                }
            ])
            sample_questions.to_csv(QUESTIONS_FILE, index=False)
        
        # Load questions from CSV
        questions_df = pd.read_csv(QUESTIONS_FILE)
        questions = []
        for _, row in questions_df.iterrows():
            questions.append({
                'id': int(row['id']),
                'question': row['question'],
                'options': ast.literal_eval(row['options']),
                'correct_answer': row['correct_answer']
            })
        return {'questions': questions}
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        return {'questions': []}

# Save quiz attempt to CSV
def save_quiz_attempt(name, score, total_questions, time_taken):
    try:
        # Get current timestamp
        current_time = datetime.now()
        timestamp = current_time.isoformat()
        
        new_attempt = pd.DataFrame([{
            'timestamp': timestamp,
            'name': name,
            'score': score,
            'total_questions': total_questions,
            'time_taken': time_taken,
            'completed': True
        }])
        
        # Append to CSV file
        new_attempt.to_csv(ATTEMPTS_FILE, mode='a', header=not os.path.exists(ATTEMPTS_FILE), index=False)
        
        # Return the timestamp for use in answer records
        return timestamp
    except Exception as e:
        st.error(f"Error saving quiz attempt: {e}")
        return None

# Save answer to CSV
def save_answer(attempt_id, question_id, answer, correct, timestamp=None):
    try:
        # Use provided timestamp or get current time
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        new_answer = pd.DataFrame([{
            'attempt_id': attempt_id,
            'question_id': question_id,
            'answer': answer,
            'correct': correct,
            'timestamp': timestamp
        }])
        
        # Append to CSV file
        new_answer.to_csv(ANSWERS_FILE, mode='a', header=not os.path.exists(ANSWERS_FILE), index=False)
    except Exception as e:
        st.error(f"Error saving answer: {e}")

# Get quiz data for admin dashboard
def get_quiz_data():
    try:
        if os.path.exists(ATTEMPTS_FILE):
            return pd.read_csv(ATTEMPTS_FILE)
        return None
    except Exception as e:
        st.error(f"Error loading quiz data: {e}")
        return None

# Initialize session state
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'results_saved' not in st.session_state:
    st.session_state.results_saved = False

# Load quiz data
QUIZ_DATA = load_quiz_data()

# Main app
def main():
    st.set_page_config(
        page_title="Quiz App",
        page_icon="❓",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main {
        background-color: #f5f6fa;
    }
    .stButton>button {
        background-color: #4a90e2;
        color: white;
        border-radius: 25px;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #357abd;
        transform: scale(1.05);
    }
    .quiz-container {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    .timer {
        font-size: 1.2em;
        color: #e74c3c;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar for admin login
    with st.sidebar:
        st.title("Admin Access")
        admin_password = st.text_input("Password", type="password")
        if st.button("Login"):
            if admin_password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.success("Admin logged in successfully!")
            else:
                st.error("Invalid password!")
    
    # Main content
    if st.session_state.admin_logged_in:
        admin_dashboard()
    elif st.session_state.quiz_completed:
        show_results()
    elif st.session_state.quiz_started:
        show_quiz()
    else:
        show_landing_page()

def show_landing_page():
    st.title("Welcome to the Quiz!")
    st.markdown("### Test your knowledge with our interactive quiz.")
    
    st.markdown("""
    #### Instructions:
    - Time limit: 30 minutes
    - Multiple choice questions
    - Results will be shown immediately after completion
    - Your progress will be saved automatically
    """)
    
    st.session_state.name = st.text_input("Enter your name")
    
    if st.button("Start Quiz"):
        if st.session_state.name:
            st.session_state.quiz_started = True
            st.session_state.start_time = time.time()
            st.experimental_rerun()
        else:
            st.error("Please enter your name to start the quiz.")

def show_quiz():
    # Timer
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, QUIZ_TIME_LIMIT * 60 - elapsed_time)  # 30 minutes in seconds
    
    if remaining_time <= 0:
        st.session_state.quiz_completed = True
        st.experimental_rerun()
    
    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)
    
    # Progress bar
    progress = (st.session_state.current_question + 1) / len(QUIZ_DATA['questions'])
    st.progress(progress)
    
    # Timer and question counter
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Question {st.session_state.current_question + 1} of {len(QUIZ_DATA['questions'])}")
    with col2:
        st.markdown(f"<div class='timer'>⏱️ {minutes:02d}:{seconds:02d}</div>", unsafe_allow_html=True)
    
    # Question
    current_q = QUIZ_DATA['questions'][st.session_state.current_question]
    st.markdown(f"### {current_q['question']}")
    
    # Options
    answer = st.radio("Select your answer:", current_q['options'], key=f"q{st.session_state.current_question}")
    
    # Create a unique key for the button to prevent conflicts
    button_key = f"next_question_{st.session_state.current_question}"
    
    if st.button("Next Question", key=button_key):
        # Check answer
        if answer == current_q['correct_answer']:
            st.session_state.score += 1
        
        # Get current timestamp for consistency
        current_time = datetime.now().isoformat()
        
        # Save answer to CSV
        save_answer(
            f"{st.session_state.name}_{int(time.time())}",
            current_q['id'],
            answer,
            answer == current_q['correct_answer'],
            current_time
        )
        
        # Move to next question or end quiz
        st.session_state.current_question += 1
        
        # Check if we've reached the end of the quiz
        if st.session_state.current_question >= len(QUIZ_DATA['questions']):
            st.session_state.quiz_completed = True
            st.session_state.results_saved = False  # Reset results saved flag
        
        st.experimental_rerun()

def show_results():
    # Calculate score and time taken (always do this, regardless of whether results are saved)
    total_questions = len(QUIZ_DATA['questions'])
    score = st.session_state.score
    percentage = (score / total_questions) * 100
    
    # Calculate time taken
    time_taken = int(time.time() - st.session_state.start_time)
    minutes_taken = time_taken // 60
    seconds_taken = time_taken % 60
    
    # Only save results once
    if not st.session_state.results_saved:
        # Get current timestamp for consistency
        current_time = datetime.now().isoformat()
        
        # Save results to CSV
        timestamp = save_quiz_attempt(
            st.session_state.name,
            score,
            total_questions,
            f"{minutes_taken}m {seconds_taken}s"
        )
        
        # Mark results as saved
        st.session_state.results_saved = True
    
    # Display results
    st.title("Quiz Results")
    
    # Score circle
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <div style="width: 200px; height: 200px; border-radius: 50%; background: conic-gradient(#4a90e2 {percentage}%, #eee 0); display: flex; align-items: center; justify-content: center; margin: 0 auto;">
            <div style="width: 180px; height: 180px; background: white; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <h2 style="margin: 0;">{score}/{total_questions}</h2>
                <p style="margin: 0;">{percentage:.1f}%</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Performance feedback
    if percentage >= 80:
        st.success("### ⭐ Excellent!")
        st.markdown("You've demonstrated outstanding knowledge!")
    elif percentage >= 60:
        st.info("### 👍 Good Job!")
        st.markdown("You've shown good understanding of the material.")
    else:
        st.warning("### 🔄 Keep Practicing!")
        st.markdown("You might want to review the material and try again.")
    
    # Time taken
    st.markdown(f"**Time taken:** {minutes_taken}m {seconds_taken}s")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Home"):
            # Reset all session state variables
            st.session_state.quiz_started = False
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.quiz_completed = False
            st.session_state.results_saved = False
            st.experimental_rerun()
    
    with col2:
        if st.button("Print Results"):
            st.markdown("""
            <script>
                window.print();
            </script>
            """, unsafe_allow_html=True)

def admin_dashboard():
    st.title("Admin Dashboard")
    st.markdown("### View quiz performance analytics and statistics")
    
    # Get data from CSV
    data = get_quiz_data()
    
    if data is None or len(data) == 0:
        st.warning("No quiz data available yet.")
        return
    
    # Convert timestamp to datetime
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    
    # Score distribution
    st.subheader("Score Distribution")
    fig_score = px.histogram(data, x='score', title='Score Distribution')
    st.plotly_chart(fig_score, use_container_width=True)
    
    # Performance over time
    st.subheader("Performance Over Time")
    fig_time = px.line(data, x='timestamp', y='score', title='Score Trends Over Time')
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Recent attempts
    st.subheader("Recent Quiz Attempts")
    st.dataframe(
        data[['timestamp', 'name', 'score', 'total_questions', 'time_taken']].sort_values('timestamp', ascending=False).head(10),
        use_container_width=True
    )
    
    # Logout button
    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.experimental_rerun()

if __name__ == "__main__":
    main() 