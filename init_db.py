import psycopg2
import os

# Define PostgreSQL connection parameters
DB_HOST = 'localhost'
DB_PORT = '5431'  # Port number you set
DB_NAME = 'quiz_app'
DB_USER = 'quiz_user'
DB_PASSWORD = 'your_password'

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
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
