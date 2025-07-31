import os
import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'database.db'

# ----------- Admin credentials -----------
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# ----------- Initialize the database -----------
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            register_no TEXT UNIQUE,
            password TEXT,
            has_voted INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_no TEXT,
            candidate TEXT
        )''')
        conn.commit()

# Run DB initialization every time app starts
@app.before_first_request
def initialize():
    init_db()

# ----------- Routes -----------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        register_no = request.form['register_no']
        password = request.form['password']

        try:
            with sqlite3.connect(DATABASE) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO voters (name, email, register_no, password) VALUES (?, ?, ?, ?)",
                          (name, email, register_no, password))
                conn.commit()
        except sqlite3.IntegrityError:
            return "Register number already exists!"
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        register_no = request.form['register_no']
        password = request.form['password']

        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM voters WHERE register_no=? AND password=?", (register_no, password))
            voter = c.fetchone()

        if voter:
            session['register_no'] = register_no
            session['name'] = voter[1]
            return redirect('/vote')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'register_no' not in session:
        return redirect('/login')

    if request.method == 'POST':
        candidate = request.form['candidate']
        register_no = session['register_no']

        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM votes WHERE register_no=?", (register_no,))
            if c.fetchone():
                return "You have already voted!"
            c.execute("INSERT INTO votes (register_no, candidate) VALUES (?, ?)", (register_no, candidate))
            conn.commit()

        return "Thanks for voting!"

    return render_template('vote.html', name=session['name'])

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

@app.route('/admin/results')
def admin_results():
    if not session.get('admin'):
        return redirect('/admin')

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT candidate, COUNT(*) FROM votes GROUP BY candidate")
        results = c.fetchall()
    return render_template('admin_results.html', results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

