from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

# Initialize Flask app
app = Flask(__name__)

# This secret key is used to encode/decode JWT tokens
SECRET_KEY = 'your_secret_key_here'  # Replace with a secure random key!

# A sample "database" for demo purposes (use real DB in production)
USERS = {
    "admin": "password",
    "sahithi": "secure123"
}

# --- JWT Token Required Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['user']
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# --- Login Route ---
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    # Validate user
    if username in USERS and USERS[username] == password:
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({'token': token})

    return jsonify({'message': 'Invalid username or password'}), 401

# --- Protected Route Example ---
@app.route('/auth/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({"message": f"Welcome, {current_user}! This is a protected route."})

# --- Run Server ---
if __name__ == "__main__":
    app.run(debug=True)
