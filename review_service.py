from flask import Flask, request, jsonify
import jwt, datetime
from functools import wraps

SECRET_KEY = "your_secret_key_here"
app = Flask(__name__)

# fake review storage
REVIEWS = [
    {"id": 1, "book_id": 1, "user": "sahithi", "text": "Great book!", "stars": 5}
]

def token_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
        if not token:
            return {"msg": "Missing token"}, 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {"msg": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"msg": "Invalid token"}, 401
        return f(*args, **kwargs)
    return wrapped

# 1. list reviews for a book (public)
@app.route("/books/<int:book_id>/reviews", methods=["GET"])
def list_reviews(book_id):
    reviews = [r for r in REVIEWS if r["book_id"] == book_id]
    return jsonify(reviews)

# 2. add a review (protected)
@app.route("/books/<int:book_id>/reviews", methods=["POST"])
@token_required
def add_review(book_id):
    data = request.get_json()
    if not data or "text" not in data or "stars" not in data:
        return {"msg": "Need text and stars"}, 400
    new_id = max(r["id"] for r in REVIEWS) + 1 if REVIEWS else 1
    # you might parse username from JWT; keeping simple:
    new_review = {
        "id": new_id,
        "book_id": book_id,
        "user": data.get("user", "anon"),
        "text": data["text"],
        "stars": data["stars"]
    }
    REVIEWS.append(new_review)
    return jsonify(new_review), 201

if __name__ == "__main__":
    app.run(port=5003, debug=True)
