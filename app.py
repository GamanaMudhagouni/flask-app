from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db():
    return sqlite3.connect(DB_PATH)

# create table
conn = get_db()
conn.execute('''CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT,
firstname TEXT,
lastname TEXT,
email TEXT,
address TEXT
)''')
conn.commit()
conn.close()

@app.route('/')
def register_page():
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register():

    data = (
        request.form['username'],
        request.form['password'],
        request.form['firstname'],
        request.form['lastname'],
        request.form['email'],
        request.form['address']
    )

    conn = get_db()
    conn.execute(
        "INSERT INTO users(username,password,firstname,lastname,email,address) VALUES(?,?,?,?,?,?)",
        data
    )
    conn.commit()
    conn.close()

    return redirect(url_for('profile', username=data[0]))

@app.route('/profile/<username>')
def profile(username):

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()

    wordcount = None
    filepath = os.path.join(UPLOAD_FOLDER, "Limerick.txt")

    if os.path.exists(filepath):
        with open(filepath) as f:
            wordcount = len(f.read().split())

    return render_template("profile.html", user=user, wordcount=wordcount)

@app.route('/login')
def login_page():
    return render_template("login.html")

@app.route('/relogin', methods=['POST'])
def relogin():

    username = request.form['username']
    password = request.form['password']

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()
    conn.close()

    if user:
        return redirect(url_for('profile', username=username))

    return "Invalid Login"

@app.route('/upload', methods=['POST'])
def upload():

    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, "Limerick.txt")
    file.save(filepath)

    return redirect(request.referrer)

@app.route('/download')
def download():

    filepath = os.path.join(UPLOAD_FOLDER, "Limerick.txt")
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run()