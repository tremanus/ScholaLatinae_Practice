import psycopg2
import os

# Retrieve the database URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://biyabrook:your_password@localhost:5431/quiz_app')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the results table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            score INTEGER NOT NULL,
            timestamp TIMESTAMP NOT NULL
        );
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized.")

if __name__ == '__main__':
    init_db()
