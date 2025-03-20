import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Secure Session Key

# ✅ SQLite Database का नाम सेट करें
DB_NAME = "database.db"

# ✅ SQLite में Tables बनाएं (अगर पहले से नहीं हैं)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')

    # Uploads Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            info TEXT
        )
    ''')

    conn.commit()
    conn.close()

# ✅ Function to save user in SQLite
def save_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# ✅ Function to check user in SQLite
def check_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# ✅ Home Route
@app.route('/')
def home():
    return redirect(url_for('login'))

# ✅ Signup Route (SQLite में यूज़र को सेव करें)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            return "Username already exists. Try another one."

        save_user(username, password)  # ✅ SQLite में यूज़र सेव करें
        return redirect(url_for('login'))

    return render_template('signup.html')

# ✅ Login Route (SQLite से यूज़र चेक करें)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if check_user(username, password):
            session['user'] = username  # ✅ User Session Store करें
            return redirect(url_for('upload'))
        else:
            return "Invalid username or password. Try again."

    return render_template('login.html')

# ✅ Upload Route (User को Authenticated होना चाहिए)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_info = request.form.get('user_info')

        # ✅ SQLite में अपलोड किया गया डेटा सेव करें
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO uploads (username, info) VALUES (?, ?)", (session['user'], user_info))
        conn.commit()
        conn.close()

        return "Information uploaded successfully!"

    return render_template('upload.html')

# ✅ View Uploads Route (सभी अपलोड डेटा देखें - सिर्फ़ लॉगिन यूज़र)
@app.route('/uploads')
def view_uploads():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT info FROM uploads WHERE username=?", (session['user'],))
    uploads = cursor.fetchall()
    conn.close()

    return render_template('uploads.html', uploads=uploads)

# ✅ Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)  # ✅ User Session Remove करें
    return redirect(url_for('login'))

# ✅ Flask App Run करें (Render के लिए सही Config)
if __name__ == '__main__':
    init_db()  # ✅ जब Flask ऐप स्टार्ट होगी, तो Database भी Initialize होगा
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=True)
