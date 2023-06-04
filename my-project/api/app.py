from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from functools import wraps

# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this!

# Initialize SQLAlchemy and LoginManager
db = SQLAlchemy(app)
login = LoginManager(app)

# Configure CORS
CORS(app, origins="http://localhost:8080", supports_credentials=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
        }

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
        }

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists.'}), 400
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'message': 'Invalid username or password'}), 400

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/track', methods=['GET'])
@login_required
def get_tracks():
    tracks = Track.query.filter_by(user_id=current_user.id).all()
    return jsonify([track.to_dict() for track in tracks])

@app.route('/api/track', methods=['POST'])
@login_required
def add_track():
    data = request.get_json()
    track = Track(name=data['name'], user_id=current_user.id)
    db.session.add(track)
    db.session.commit()
    return jsonify(track.to_dict())

@app.route('/api/track/<int:id>', methods=['DELETE'])
def delete_track(id):
    track = Track.query.filter_by(id=id).first()
    try:
        db.session.delete(track)
        db.session.commit()
        return jsonify({'message': 'Logged in successfully'}), 200
    except:
        return jsonify({'message': 'Failed to delete track'}), 400

@app.route('/api/track/<int:id>', methods=['PUT'])
def update_track(id):
    track = Track.query.filter_by(id=id).first()
    try:
        data = request.get_json()
        if not track:
            return jsonify({'message': 'No track found!'})
        track.name = data['name']
        db.session.commit()
        return jsonify({'message': 'Track has been updated!'})
    except:
        return jsonify({'message': 'Failed to delete track'}), 400    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()