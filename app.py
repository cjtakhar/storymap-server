from flask import Flask, request, jsonify, g
from flask_cors import CORS
from models import db, User, Card
from config import Config
import jwt

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=app.config['CORS_ORIGINS'])
db.init_app(app)
app.config['SECRET_KEY'] = 'secret'

@app.route('/')
def index():
    return "Welcome to the Story Map server."

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        token = jwt.encode({'username': username}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'success': True, 'token': token}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'error': 'Username already exists'}), 400
    else:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True}), 200

@app.route('/api/cards', methods=['GET', 'POST'])
def save_cards():
    if request.method == 'GET':
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Missing token'}), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            username = payload['username']
        except jwt.DecodeError:
            return jsonify({'error': 'Invalid token'}), 401

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        cards = Card.query.filter_by(user_id=user.id).all()
        cards_data = [{'id': card.id, 'information': card.information} for card in cards]

        return jsonify({'cards': cards_data}), 200

    elif request.method == 'POST':
        data = request.get_json()
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Missing token'}), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            username = payload['username']
        except jwt.DecodeError:
            return jsonify({'error': 'Invalid token'}), 401

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Clear existing cards for the user
        Card.query.filter_by(user_id=user.id).delete()

        for card in data['cards']:
            card_id = card['id']
            card_info = card['information']

            new_card = Card(id=card_id, information=card_info, user=user)
            db.session.add(new_card)

        db.session.commit()
        return jsonify({'success': True}), 200


if __name__ == '__main__':
    # Use gunicorn as the server
    import os
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)
