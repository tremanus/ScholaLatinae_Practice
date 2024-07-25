from flask import Flask, render_template, request, redirect, url_for, session
import json
import random
from datetime import datetime, timedelta
import psycopg2
import os
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Use environment variable or default

# Initialize CORS
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins; adjust as needed

# Database configuration
POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgres://default:uUi5dkVcTjH8@ep-sweet-mode-a42cjtbt-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require')

def get_db_connection():
    conn = psycopg2.connect(POSTGRES_URL)
    return conn

# Load questions from a JSON file
def load_questions(filename):
    try:
        with open(filename) as f:
            data = json.load(f)
            if isinstance(data.get('questions'), list):
                return data['questions']
            else:
                raise ValueError("Invalid JSON format: 'questions' must be a list")
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Error loading questions: {e}")
        return []

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/beginner', methods=['GET', 'POST'])
def beginner_index():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        session['questions'] = random.sample(load_questions('beginner_questions.json'), min(10, len(load_questions('beginner_questions.json'))))  # Load beginner questions
        session['question_index'] = 0
        session['score'] = 0
        session['answers'] = []  # Initialize the answers list
        return redirect(url_for('beginner_quiz', _external=True))
    return render_template('beginner-index.html')

@app.route('/beginner-quiz', methods=['GET', 'POST'])
def beginner_quiz():
    if 'username' not in session:
        return redirect(url_for('beginner_index', _external=True))

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
            return redirect(url_for('beginner_result', _external=True))

    current_question_index = session.get('question_index', 0)
    if current_question_index < len(session['questions']):
        current_question = session['questions'][current_question_index]

        # Shuffle the options
        options = current_question['options']
        random.shuffle(options)
        current_question['options'] = options

        return render_template('beginner-quiz.html', question=current_question, question_number=current_question_index + 1)
    return redirect(url_for('beginner_result', _external=True))

@app.route('/beginner-result')
def beginner_result():
    if 'username' not in session:
        return redirect(url_for('beginner_index', _external=True))
    
    score = session.get('score', 0)
    username = session.get('username')
    last_submission_time = session.get('last_submission_time')

    # Check if the last submission was within the last 20 seconds
    if last_submission_time:
        last_submission_time = datetime.strptime(last_submission_time, '%Y-%m-%d %H:%M:%S.%f')
        time_since_last_submission = datetime.now() - last_submission_time
        if time_since_last_submission < timedelta(seconds=20):
            error_message = "You must wait 20 seconds between submissions."
            return render_template('beginner-result.html', score=score, username=username, error_message=error_message)

    # Save result to database
    save_result(username, score, 'beginner')

    # Update the last submission time
    session['last_submission_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    
    return render_template('beginner-result.html', score=score, username=username)

@app.route('/intermediate', methods=['GET', 'POST'])
def intermediate_index():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        session['questions'] = random.sample(load_questions('intermediate_questions.json'), min(10, len(load_questions('intermediate_questions.json'))))  # Load intermediate questions
        session['question_index'] = 0
        session['score'] = 0
        session['answers'] = []  # Initialize the answers list
        return redirect(url_for('intermediate_quiz', _external=True))
    return render_template('intermediate-index.html')

@app.route('/intermediate-quiz', methods=['GET', 'POST'])
def intermediate_quiz():
    if 'username' not in session:
        return redirect(url_for('intermediate_index', _external=True))

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
            return redirect(url_for('intermediate_result', _external=True))

    current_question_index = session.get('question_index', 0)
    if current_question_index < len(session['questions']):
        current_question = session['questions'][current_question_index]

        # Shuffle the options
        options = current_question['options']
        random.shuffle(options)
        current_question['options'] = options

        return render_template('intermediate-quiz.html', question=current_question, question_number=current_question_index + 1)
    return redirect(url_for('intermediate_result', _external=True))

@app.route('/intermediate-result')
def intermediate_result():
    if 'username' not in session:
        return redirect(url_for('intermediate_index', _external=True))
    
    score = session.get('score', 0)
    username = session.get('username')
    
    # Save result to database
    save_result(username, score, 'intermediate')
    
    return render_template('intermediate-result.html', score=score, username=username)

@app.route('/advanced', methods=['GET', 'POST'])
def advanced_index():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        session['questions'] = random.sample(load_questions('advanced_questions.json'), min(10, len(load_questions('advanced_questions.json'))))  # Load advanced questions
        session['question_index'] = 0
        session['score'] = 0
        session['answers'] = []  # Initialize the answers list
        return redirect(url_for('advanced_quiz', _external=True))
    return render_template('advanced-index.html')

@app.route('/advanced-quiz', methods=['GET', 'POST'])
def advanced_quiz():
    if 'username' not in session:
        return redirect(url_for('advanced_index', _external=True))

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
            return redirect(url_for('advanced_result', _external=True))

    current_question_index = session.get('question_index', 0)
    if current_question_index < len(session['questions']):
        current_question = session['questions'][current_question_index]

        # Shuffle the options
        options = current_question['options']
        random.shuffle(options)
        current_question['options'] = options

        return render_template('advanced-quiz.html', question=current_question, question_number=current_question_index + 1)
    return redirect(url_for('advanced_result', _external=True))

@app.route('/advanced-result')
def advanced_result():
    if 'username' not in session:
        return redirect(url_for('advanced_index', _external=True))
    
    score = session.get('score', 0)
    username = session.get('username')
    
    # Save result to db
    save_result(username, score, 'advanced')
    
    return render_template('advanced-result.html', score=score, username=username)

@app.route('/leaderboard')
def leaderboard():
    beginner_results = get_leaderboard('beginner')
    intermediate_results = get_leaderboard('intermediate')
    advanced_results = get_leaderboard('advanced')
    return render_template('leaderboard.html', beginner_results=beginner_results, intermediate_results=intermediate_results, advanced_results=advanced_results)

def save_result(username, score, quiztype):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute('''
        SELECT score FROM results WHERE username = %s AND quiztype = %s
    ''', (username, quiztype))
    existing_score = cursor.fetchone()

    if existing_score:
        # Update existing user's score
        cursor.execute('''
            UPDATE results
            SET score = score + %s, timestamp = %s
            WHERE username = %s AND quiztype = %s
        ''', (score, datetime.now(), username, quiztype))
    else:
        # Insert new user
        cursor.execute('''
            INSERT INTO results (username, score, timestamp, quiztype)
            VALUES (%s, %s, %s, %s)
        ''', (username, score, datetime.now(), quiztype))

    conn.commit()
    cursor.close()
    conn.close()

def get_leaderboard(quiztype):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, score
        FROM results
        WHERE quiztype = %s
        ORDER BY score DESC
        LIMIT 10
    ''', (quiztype,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port if needed