from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from functools import wraps
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from config import SECRET_KEY, JWT_SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_TOKEN_LOCATION'] = ['headers']
jwt = JWTManager(app)

# Initialize SQLAlchemy and LoginManager
db = SQLAlchemy(app)
login = LoginManager(app)

# Configure CORS
CORS(app, supports_credentials=True)


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
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(
            identity={'username': user.username, 'user_id': user.id})
        return jsonify(access_token=access_token, user_id=user.id), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/tracks', methods=['GET'])
@jwt_required()
def get_tracks():
    current_user = get_jwt_identity()
    user_id = current_user['user_id']
    tracks = Track.query.all()
    filtered_tracks = [track for track in tracks if track.user_id == user_id]
    return jsonify([track.to_dict() for track in filtered_tracks])


@app.route('/api/tracks', methods=['POST'])
@jwt_required()
def add_track():
    data = request.get_json()
    current_user = get_jwt_identity()
    user_id = current_user['user_id']
    new_track = Track(name=data['name'], user_id=user_id)
    db.session.add(new_track)
    db.session.commit()
    return jsonify(new_track.to_dict()), 201


@app.route('/api/tracks/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_track(id):
    # This will return None if no track with that ID exists
    track = Track.query.get(id)
    if track is None:
        return jsonify({'message': 'Invalid track ID.'}), 404
    try:
        db.session.delete(track)
        db.session.commit()
        return jsonify({'message': 'Track deleted successfully'}), 200
    except:
        return jsonify({'message': 'Failed to delete track'}), 400


@app.route('/api/tracks/<int:id>', methods=['PUT'])
@jwt_required()
def update_track(id):
    track = Track.query.get(id)
    if track is None:
        return jsonify({'message': 'Invalid track ID.'}), 404
    data = request.get_json()
    track.name = data.get('name', track.name)
    try:
        db.session.commit()
        return jsonify({'message': 'Track updated successfully'}), 200
    except:
        return jsonify({'message': 'Failed to update track'}), 400


@app.route('/api/tracks/search', methods=['GET'])
@jwt_required()
def search():
    query = request.args.get('query')
    if query:
        tracks = Track.query.filter(Track.name.ilike(f'%{query}%')).all()
    else:
        tracks = Track.query.all()
    return jsonify([track.to_dict() for track in tracks]), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
