import sqlite3

# Connect to the SQLite database (will create it if not exists)
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create voters table
c.execute('''
    CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        register_no TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Create votes table
c.execute('''
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        register_no TEXT NOT NULL UNIQUE,
        candidate TEXT NOT NULL
    )
''')

conn.commit()
print("✅ Tables created successfully.\n")

# View existing votes
c.execute("SELECT * FROM votes")
rows = c.fetchall()

print("📊 Votes in the database:")
if rows:
    for row in rows:
        print(f"🗳️  Register No: {row[1]}, Candidate: {row[2]}")
else:
    print("No votes recorded yet.")

conn.close()
