import os
from flask import Flask, render_template, request, redirect, url_for, session

# ✅ Flask App Initialize करें और Templates Folder को सेट करें
app = Flask(__name__, template_folder=os.path.abspath('templates'))
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# ✅ `/` Route (GET और HEAD दोनों सपोर्ट)
@app.route('/', methods=['GET', 'HEAD'])
def home():
    if request.method == 'HEAD':
        return '', 200  # ✅ HEAD रिक्वेस्ट को हैंडल करें
    return redirect(url_for('login.html'))  # ✅ `/signup` पर रीडायरेक्ट

# ✅ Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                return "Username and password are required."

            return redirect(url_for('login'))

        return render_template('signup.html')  # ✅ `/templates/signup.html` होना चाहिए
    except Exception as e:
        return f"Error loading signup page: {e}"  # ✅ अगर Error आए तो दिखाए

# ✅ Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        return render_template('login.html')  # ✅ `/templates/login.html` होना चाहिए
    except Exception as e:
        return f"Error loading login page: {e}"

# ✅ Upload Route (User को Authenticated होना चाहिए)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        return render_template('upload.html')  # ✅ `/templates/upload.html` होना चाहिए
    except Exception as e:
        return f"Error loading upload page: {e}"

# ✅ Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ✅ Flask App Run करें (Render के लिए सही Config)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=True)
