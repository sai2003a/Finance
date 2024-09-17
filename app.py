from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3  

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' 


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  
    return conn


def create_user_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
  
    if 'user_id' in session:
        return redirect(url_for('dashboard'))  
    else:
        return redirect(url_for('register'))  
    
@app.route('/logout')
def logout():
    session.pop('user_id', None) 
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

       
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('register'))

    
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? OR username = ?', (email, username)).fetchone()

        if user:
            flash('Username or Email is already taken.', 'error')
            conn.close()
            return redirect(url_for('register'))

       
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        conn.commit()
        conn.close()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']  
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard')) 

        flash('Invalid email or password. Please try again.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
   
    create_user_table()
    app.run(debug=True)
