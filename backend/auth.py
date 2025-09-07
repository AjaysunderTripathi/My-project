from flask import session, jsonify
from functools import wraps

# Example user store (replace with DB in production)
USERS = {
    'admin': {'password': 'adminpass', 'type': 'admin'},
    'volunteer': {'password': 'volpass', 'type': 'volunteer'},
    'student': {'password': 'studpass', 'type': 'student'}
}

def login_user(data):
    username = data.get('username')
    password = data.get('password')
    user = USERS.get(username)
    if user and user['password'] == password:
        session['user_id'] = username
        session['user_type'] = user['type']
        return jsonify({'message': 'Login successful', 'user_type': user['type']})
    return jsonify({'error': 'Invalid credentials'}), 401

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

def get_user_type(user_id):
    user = USERS.get(user_id)
    return user['type'] if user else 'student'

def logout_user():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return jsonify({'message': 'Logout successful'})
