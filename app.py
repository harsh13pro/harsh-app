from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # सेशन के लिए सिक्योरिटी की जरूरत है

# Users और User Credentials को स्टोर करने के लिए फाइल्स
USER_FILE = "users.txt"
USER_CREDENTIALS_FILE = "user_credentials.txt"

# Function to read users from file
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

# Function to save a new user
def save_user(username, password):
    with open(USER_FILE, "a") as file:
        file.write(f"{username}:{password}\n")
    with open(USER_CREDENTIALS_FILE, "a") as file:
        file.write(f"Email: {username}, Password: {password}\n")  # ✅ ईमेल और पासवर्ड सेव

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()
        if username in users:
            return "Username already exists. Try another one."

        save_user(username, password)  # ✅ Signup पर ईमेल और पासवर्ड सेव

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()

        if username in users and users[username] == password:
            session['user'] = username  # Store user session
            save_user(username, password)  # ✅ Login पर भी ईमेल और पासवर्ड सेव
            return redirect(url_for('upload'))
        else:
            return "Invalid username or password. Try again."

    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:  # Prevent access without login
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_info = request.form.get('user_info')

        # Save submitted info to a file
        with open("submitted_data.txt", "a") as file:
            file.write(f"User: {session['user']}, Info: {user_info}\n")

        return "Information uploaded successfully!"

    return render_template('upload.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)  # Flask app run होगा
