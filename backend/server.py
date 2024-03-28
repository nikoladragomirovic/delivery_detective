from flask import Flask, jsonify, request, abort
from pymongo import MongoClient
import bcrypt
import secrets
import string

app = Flask(__name__)

def generate_session_token():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(32))

def check_session_token(username, session_token):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['dostava_detektiv']
    accounts_collection = db['accounts']

    user = accounts_collection.find_one({'username': username, 'session_tokens': session_token})
    return user is not None

@app.route('/restaurants', methods=['GET'])
def restaurants():
    username = request.form.get('username')
    session_token = request.form.get('session_token')

    if not username or not session_token:
        return jsonify({'error': 'Username or session token missing'}), 400

    if not check_session_token(username, session_token):
        return jsonify({'error': 'Invalid session token'}), 401

    client = MongoClient('mongodb://localhost:27017/')
    db = client['dostava_detektiv']
    restaurants_collection = db['restaurants']
    data = list(restaurants_collection.find())

    for item in data:
        item['_id'] = str(item['_id'])

    return jsonify(data)

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({'error': 'Username or password missing'}), 400

    client = MongoClient('mongodb://localhost:27017/')
    db = client['dostava_detektiv']
    accounts_collection = db['accounts']

    existing_user = accounts_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user = {
        'username': username,
        'password': hashed_password.decode('utf-8')
    }
    accounts_collection.insert_one(new_user)

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({'error': 'Username or password missing'}), 400

    client = MongoClient('mongodb://localhost:27017/')
    db = client['dostava_detektiv']
    accounts_collection = db['accounts']

    existing_user = accounts_collection.find_one({'username': username})
    if not existing_user:
        return jsonify({'error': 'Username does not exist'}), 404

    hashed_password = existing_user['password'].encode('utf-8')

    if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        session_token = generate_session_token()
        accounts_collection.update_one({'username': username}, {'$push': {'session_tokens': session_token}})

        return jsonify({'message': 'Login successful', 'session_token': session_token}), 200
    else:
        return jsonify({'error': 'Incorrect password'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    username = request.form.get('username')
    session_token = request.form.get('session_token')

    if not username or not session_token:
        return jsonify({'error': 'Username or session token missing'}), 400

    client = MongoClient('mongodb://localhost:27017/')
    db = client['dostava_detektiv']
    accounts_collection = db['accounts']

    accounts_collection.update_one({'username': username}, {'$pull': {'session_tokens': session_token}})

    return jsonify({'message': 'Logout successful'}), 200

if __name__ == '__main__':
    app.run(debug=True)