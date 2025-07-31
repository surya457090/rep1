import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')  # for session

DATABASE = 'voting.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        candidate TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    ''')
    db.commit()

@app.before_request
def before_request():
    init_db()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']

        # Admin login check
        if uname == os.environ.get('ADMIN_USERNAME') and pwd == os.environ.get('ADMIN_PASSWORD'):
            session['admin'] = True
            return redirect(url_for('admin'))

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (uname,)).fetchone()
        if user and check_password_hash(user['password'], pwd):
            session['user_id'] = user['id']
            return redirect(url_for('vote'))
        return "Invalid login"
    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    existing_vote = db.execute('SELECT * FROM votes WHERE user_id = ?', (session['user_id'],)).fetchone()
    if existing_vote:
        return "You already voted."

    if request.method == 'POST':
        candidate = request.form['candidate']
        db.execute('INSERT INTO votes (user_id, candidate) VALUES (?, ?)', (session['user_id'], candidate))
        db.commit()
        return "Vote submitted!"
    return render_template('vote.html')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    db = get_db()
    result = db.execute('SELECT candidate, COUNT(*) as count FROM votes GROUP BY candidate').fetchall()
    return render_template('admin.html', results=result)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)


