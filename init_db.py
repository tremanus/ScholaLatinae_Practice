import psycopg2
import os

POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgres://default:uUi5dkVcTjH8@ep-sweet-mode-a42cjtbt.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require')

def get_db_connection():
    conn = psycopg2.connect(POSTGRES_URL)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the results table with quiz_type if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            score INTEGER NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            quiztype VARCHAR(20) NOT NULL
        );
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized.")

if __name__ == '__main__':
    init_db()
