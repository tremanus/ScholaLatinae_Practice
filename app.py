from flask import Flask, render_template, request, redirect, url_for, session
import json
import random
from datetime import datetime
import psycopg2
import os
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Use environment variable or default

# Initialize CORS
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins; adjust as needed

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5431')
DB_NAME = os.getenv('DB_NAME', 'quiz_app')
DB_USER = os.getenv('DB_USER', 'quiz_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# Load questions from a JSON file
def load_questions():
    try:
        with open('questions.json') as f:
            data = json.load(f)
            if isinstance(data.get('questions'), list):
                return data['questions']
            else:
                raise ValueError("Invalid JSON format: 'questions' must be a list")
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Error loading questions: {e}")
        return []

questions = load_questions()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        session['questions'] = random.sample(questions, min(10, len(questions)))  # Get 10 random questions or less if not enough
        session['question_index'] = 0
        session['score'] = 0
        session['answers'] = []  # Initialize the answers list
        return redirect(url_for('quiz'))
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        answer = request.form.get('answer')
        current_question_index = session.get('question_index', 0)
        current_question = session['questions'][current_question_index]
        
        is_correct = answer == current_question['correct_answer']
        if is_correct:
            session['score'] += 1

        session['answers'].append((current_question['question'], answer, is_correct, current_question['correct_answer']))

        session['question_index'] += 1
        if session['question_index'] >= len(session['questions']):
            return redirect(url_for('result'))

    current_question_index = session.get('question_index', 0)
    if current_question_index < len(session['questions']):
        current_question = session['questions'][current_question_index]

        # Shuffle the options
        options = current_question['options']
        random.shuffle(options)
        current_question['options'] = options

        return render_template('quiz.html', question=current_question, question_number=current_question_index + 1)
    return redirect(url_for('result'))

@app.route('/result')
def result():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    score = session.get('score', 0)
    username = session.get('username')
    
    # Save result to database
    save_result(username, score)
    
    return render_template('result.html', score=score, username=username)

@app.route('/leaderboard')
def leaderboard():
    results = get_leaderboard()
    return render_template('leaderboard.html', results=results)

def save_result(username, score):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute('''
        SELECT score FROM results WHERE username = %s
    ''', (username,))
    existing_score = cursor.fetchone()

    if existing_score:
        # Update existing user's score
        cursor.execute('''
            UPDATE results
            SET score = score + %s, timestamp = %s
            WHERE username = %s
        ''', (score, datetime.now(), username))
    else:
        # Insert new user
        cursor.execute('''
            INSERT INTO results (username, score, timestamp)
            VALUES (%s, %s, %s)
        ''', (username, score, datetime.now()))

    conn.commit()
    cursor.close()
    conn.close()

def get_leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, score
        FROM results
        ORDER BY score DESC
        LIMIT 10
    ''')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port if needed
