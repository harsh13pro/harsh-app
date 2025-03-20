import os
from flask import Flask, request, render_template, redirect, url_for, session

# ✅ Flask App Initialize करें
app = Flask(__name__, template_folder=os.path.abspath('templates'))
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Secure Session Key

# ✅ Users और Credentials को स्टोर करने के लिए फाइल्स
USER_FILE = "users.txt"
USER_CREDENTIALS_FILE = "user_credentials.txt"

# ✅ Function to read users from file
def load_users():
    users = {}
    try:
        with open(USER_FILE, "r") as file:
            for line in file:
                line = line.strip()
                if ":" in line:  # Validate format
                    username, password = line.split(":", 1)
                    users[username] = password
    except FileNotFoundError:
        pass
    return users

# ✅ Function to save a new user
def save_user(username, password):
    with open(USER_FILE, "a") as file:
        file.write(f"{username}:{password}\n")
    with open(USER_CREDENTIALS_FILE, "a") as file:
        file.write(f"Email: {username}, Password: {password}\n")  # ✅ ईमेल और पासवर्ड सेव

# ✅ Home Route
@app.route('/', methods=['GET', 'HEAD'])
def home():
    if request.method == 'HEAD':
        return '', 200  # ✅ HEAD रिक्वेस्ट को हैंडल करें
    return redirect(url_for('login'))  # ✅ `/login` पर रीडायरेक्ट

# ✅ Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                return "Username and password are required."

            users = load_users()
            if username in users:
                return "Username already exists. Try another one."

            save_user(username, password)  # ✅ Signup पर ईमेल और पासवर्ड सेव
            return redirect(url_for('login'))

        return render_template('signup.html')  # ✅ `/templates/signup.html` होना चाहिए
    except Exception as e:
        return f"Error loading signup page: {e}"  # ✅ अगर Error आए तो दिखाए

# ✅ Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            users = load_users()

            if username in users and users[username] == password:
                session['user'] = username  # Store user session
                return redirect(url_for('upload'))
            else:
                return "Invalid username or password. Try again."

        return render_template('login.html')  # ✅ `/templates/login.html` होना चाहिए
    except Exception as e:
        return f"Error loading login page: {e}"

# ✅ Upload Route (User को Authenticated होना चाहिए)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        if request.method == 'POST':
            user_info = request.form.get('user_info')

            # ✅ Save submitted info to a file
            with open("submitted_data.txt", "a") as file:
                file.write(f"User: {session['user']}, Info: {user_info}\n")

            return "Information uploaded successfully!"

        return render_template('upload.html')  # ✅ `/templates/upload.html` होना चाहिए
    except Exception as e:
        return f"Error loading upload page: {e}"

# ✅ Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user session
    return redirect(url_for('login'))

# ✅ Flask App Run करें (Render के लिए सही Config)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=True)
