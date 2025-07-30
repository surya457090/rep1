from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy admin credentials (can be improved)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Create the database and tables if not exist
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        register_no TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        register_no TEXT UNIQUE NOT NULL,
        candidate TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        register_no = request.form['register_no']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO voters (name, email, register_no, password) VALUES (?, ?, ?, ?)",
                      (name, email, register_no, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Register number already exists!"
        finally:
            conn.close()

        return redirect('/login')

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        register_no = request.form['register_no']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM voters WHERE register_no=? AND password=?", (register_no, password))
        voter = c.fetchone()
        conn.close()

        if voter:
            session['register_no'] = register_no
            session['name'] = voter[1]
            return redirect('/vote')
        else:
            return "Invalid credentials"

    return render_template('login.html')

# Vote route
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'register_no' not in session:
        return redirect('/login')

    register_no = session['register_no']

    if request.method == 'POST':
        candidate = request.form['candidate']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM votes WHERE register_no=?", (register_no,))
        if c.fetchone():
            conn.close()
            return "You have already voted!"

        c.execute("INSERT INTO votes (register_no, candidate) VALUES (?, ?)", (register_no, candidate))
        conn.commit()
        conn.close()

        return "Thanks for voting!"

    return render_template('vote.html', name=session.get('name'))

# Admin login
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/admin/results')
        else:
            return "Invalid admin credentials"

    return render_template('admin_login.html')

# Admin results page
@app.route('/admin/results')
def admin_results():
    if not session.get('admin'):
        return redirect('/admin')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT candidate, COUNT(*) FROM votes GROUP BY candidate")
    results = c.fetchall()
    conn.close()

    return render_template('admin_results.html', results=results)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

