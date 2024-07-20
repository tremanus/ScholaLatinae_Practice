import sqlite3

conn = sqlite3.connect('results.db')
cursor = conn.cursor()

# Create the results table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        score INTEGER NOT NULL,
        timestamp TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
