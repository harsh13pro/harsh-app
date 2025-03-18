import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Render के लिए Secret Key

# ✅ फाइलें अगर मौजूद नहीं हैं, तो क्रिएट करें
USER_FILE = "users.txt"
USER_CREDENTIALS_FILE = "user_credentials.txt"
for file in [USER_FILE, USER_CREDENTIALS_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            pass  # खाली फाइल बनाएँ

# ✅ फ़ाइल से Users पढ़ने का Function
def load_users():
    users = {}
    try:
        with open(USER_FILE, "r") as file:
            for line in file:
                line = line.strip()
                if ":" in line:
                    username, password = line.split(":", 1)
                    users[username] = password
    except Exception as e:
        print(f"Error reading {USER_FILE}: {e}")
    return users

# ✅ Users को Save करने का Function
def save_user(username, password):
    try:
        with open(USER_FILE, "a") as file:
            file.write(f"{username}:{password}\n")
        with open(USER_CREDENTIALS_FILE, "a") as file:
            file.write(f"Email: {username}, Password: {password}\n")
    except Exception as e:
        print(f"Error saving user: {e}")

# ✅ `/` Route (HEAD और GET दोनों सपोर्ट)
@app.route('/', methods=['GET', 'HEAD'])
def home():
    if request.method == 'HEAD':
        return '', 200  # ✅ HEAD रिक्वेस्ट को हैंडल करें
    return redirect(url_for('signup'))  # ✅ `/signup` पर रीडायरेक्ट

# ✅ Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return "Username and password are required."

        users = load_users()
        if username in users:
            return "Username already exists. Try another one."

        save_user(username, password)
        return redirect(url_for('login'))

    return render_template('signup.html')

# ✅ Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()
        if username in users and users[username] == password:
            session['user'] = username
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

        try:
            with open("submitted_data.txt", "a") as file:
                file.write(f"User: {session['user']}, Info: {user_info}\n")
            return "Information uploaded successfully!"
        except Exception as e:
            return f"Error saving data: {e}"

    return render_template('upload.html')

# ✅ Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ✅ Flask App Run करें
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=True)
