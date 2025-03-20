import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session, g

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Secure Session Key

# ✅ Render के लिए `/data/` फोल्डर में डेटाबेस सेव करें
DB_NAME = "/data/database.db" if os.getenv("RENDER") else "database.db"

# ✅ SQLite Connection Function
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db

# ✅ Database और Tables Create करें
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            info TEXT
        )
    ''')
    conn.commit()
    print("✅ Database और Tables क्रिएट हो गए!")

@app.before_request
def before_request():
    get_db()

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# ✅ HEAD Request Fix
@app.route('/', methods=['GET', 'HEAD'])
def home():
    if request.method == 'HEAD':
        return '', 200  # ✅ HEAD रिक्वेस्ट को हैंडल करें
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "Username already exists. Try another one."

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = username
            return redirect(url_for('upload'))
        else:
            return "Invalid username or password. Try again."

    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_info = request.form.get('user_info')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO uploads (username, info) VALUES (?, ?)", (session['user'], user_info))
        conn.commit()

        return "Information uploaded successfully!"

    return render_template('upload.html')

@app.route('/uploads')
def view_uploads():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT info FROM uploads WHERE username=?", (session['user'],))
    uploads = cursor.fetchall()

    return render_template('uploads.html', uploads=uploads)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=True)
