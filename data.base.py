import sqlite3

def get_db():
    return sqlite3.connect('messenger.db')

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                user_id INTEGER,
                friend_id INTEGER,
                status TEXT DEFAULT 'pending'
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user INTEGER,
                to_user INTEGER,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

def create_user(username, password):
    with get_db() as conn:
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                        (username, password))
            return True
        except:
            return False

def get_user(username, password):
    with get_db() as conn:
        cur = conn.execute('SELECT * FROM users WHERE username=? AND password=?',
                          (username, password))
        return cur.fetchone()

def get_user_by_name(username):
    with get_db() as conn:
        cur = conn.execute('SELECT * FROM users WHERE username=?', (username,))
        return cur.fetchone()

def add_friend_request(user_id, friend_name):
    friend = get_user_by_name(friend_name)
    if not friend:
        return False
    
    with get_db() as conn:
        try:
            conn.execute('''
                INSERT INTO friends (user_id, friend_id, status)
                VALUES (?, ?, 'accepted')
            ''', (user_id, friend[0]))
            conn.execute('''
                INSERT INTO friends (user_id, friend_id, status)
                VALUES (?, ?, 'accepted')
            ''', (friend[0], user_id))
            return True
        except:
            return False

def get_friends(user_id):
    with get_db() as conn:
        cur = conn.execute('''
            SELECT u.username FROM friends f
            JOIN users u ON f.friend_id = u.id
            WHERE f.user_id = ? AND f.status = 'accepted'
        ''', (user_id,))
        return [row[0] for row in cur.fetchall()]

def save_message(from_user, to_username, message):
    to_user = get_user_by_name(to_username)
    if not to_user:
        return False
    
    with get_db() as conn:
        conn.execute('''
            INSERT INTO messages (from_user, to_user, message)
            VALUES (?, ?, ?)
        ''', (from_user, to_user[0], message))
        return True

def get_messages_between(user_id, other_username):
    other = get_user_by_name(other_username)
    if not other:
        return []
    
    with get_db() as conn:
        cur = conn.execute('''
            SELECT u.username, m.message, m.timestamp
            FROM messages m
            JOIN users u ON m.from_user = u.id
            WHERE (m.from_user = ? AND m.to_user = ?)
               OR (m.from_user = ? AND m.to_user = ?)
            ORDER BY m.timestamp
        ''', (user_id, other[0], other[0], user_id))
        
        return [{'from': row[0], 'message': row[1], 'time': row[2]}
                for row in cur.fetchall()]