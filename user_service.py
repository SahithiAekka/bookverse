from flask import Flask, request, jsonify
import jwt, datetime
from functools import wraps

SECRET_KEY = "your_secret_key_here"      # same key everywhere
app = Flask(__name__)

# fake “database”
USERS = [
    {"id": 1, "username": "admin", "email": "admin@mail.com"},
    {"id": 2, "username": "sahithi", "email": "sahithi@mail.com"}
]

# ------------- token decorator -------------
def token_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
        if not token:
            return jsonify({"msg": "Missing token"}), 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"msg": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"msg": "Invalid token"}), 401
        return f(*args, **kwargs)
    return wrapped
# -------------------------------------------

# 1. get profile (public)
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = next((u for u in USERS if u["id"] == user_id), None)
    return jsonify(user) if user else ({"msg": "User not found"}, 404)

# 2. register new user (open)
@app.route("/users", methods=["POST"])
def register():
    data = request.get_json()
    if not data or "username" not in data or "email" not in data:
        return {"msg": "Need username & email"}, 400
    new_id = max(u["id"] for u in USERS) + 1 if USERS else 1
    new_user = {"id": new_id, "username": data["username"], "email": data["email"]}
    USERS.append(new_user)
    return jsonify(new_user), 201

# 3. update profile (protected)
@app.route("/users/<int:user_id>", methods=["PUT"])
@token_required
def update_user(user_id):
    data = request.get_json()
    user = next((u for u in USERS if u["id"] == user_id), None)
    if not user:
        return {"msg": "User not found"}, 404
    user["username"] = data.get("username", user["username"])
    user["email"]    = data.get("email", user["email"])
    return jsonify(user)

if __name__ == "__main__":
    app.run(port=5002, debug=True)
