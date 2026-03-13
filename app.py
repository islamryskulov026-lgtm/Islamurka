from flask import Flask, render_template, request, redirect, session
from database import *
import sqlite3

app = Flask(__name__)
app.secret_key = 'islam_secret_key'

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/chat')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user(username, password)
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/chat')
        else:
            return render_template('login.html', error='Неверный логин или пароль')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if create_user(username, password):
            return redirect('/login')
        else:
            return render_template('register.html', error='Имя занято')
    
    return render_template('register.html')

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect('/login')
    
    friends = get_friends(session['user_id'])
    return render_template('chat.html', username=session['username'], friends=friends)

@app.route('/add_friend', methods=['POST'])
def add_friend():
    if 'user_id' not in session:
        return {'error': 'Not logged in'}, 401
    
    friend_name = request.form['friend_name']
    success = add_friend_request(session['user_id'], friend_name)
    return {'success': success}

@app.route('/get_friends')
def get_friends_list():
    if 'user_id' not in session:
        return {'error': 'Not logged in'}, 401
    
    friends = get_friends(session['user_id'])
    return {'friends': friends}

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return {'error': 'Not logged in'}, 401
    
    to_user = request.form['to_user']
    message = request.form['message']
    
    success = save_message(session['user_id'], to_user, message)
    return {'success': success}

@app.route('/get_messages')
def get_messages():
    if 'user_id' not in session:
        return {'error': 'Not logged in'}, 401
    
    with_user = request.args.get('with')
    messages = get_messages_between(session['user_id'], with_user)
    return {'messages': messages}

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)