from flask import Flask, request, jsonify
import jwt
from functools import wraps 
import datetime 

app = Flask(__name__)
SECRET_KEY= "your_secret_key_here" #this must match auth service

#database swap later 
BOOKS = [
    {"id": 1, "title": "Harry Potter", "author": "J. K. Rowling"},
    {"id": 2, "title": "Atomic Habits", "author": "James Clear"},
]

# ─────────────  helper: JWT guard (copied from Auth svc) ─────────────
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
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
            return jsonify({"msg": "Bad token"}), 401

        return f(*args, **kwargs)
    return decorated

# ───────────────────────  ENDPOINTS  ─────────────────────────

# 1. LIST all books
@app.route("/books", methods=["GET"])
def list_books():
    return jsonify(BOOKS)

# 2. GET one book by id
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if book:
        return jsonify(book)
    return jsonify({"msg": "Book not found"}), 404

# 3. ADD a new book   (protected)
@app.route("/books", methods=["POST"])
@token_required
def add_book():
    data = request.get_json()
    if not data or "title" not in data or "author" not in data:
        return jsonify({"msg": "Need title and author"}), 400

    new_id = max(b["id"] for b in BOOKS) + 1 if BOOKS else 1
    new_book = {"id": new_id, "title": data["title"], "author": data["author"]}
    BOOKS.append(new_book)
    return jsonify(new_book), 201

# 4. UPDATE existing book   (protected)
@app.route("/books/<int:book_id>", methods=["PUT"])
@token_required
def update_book(book_id):
    data = request.get_json()
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        return jsonify({"msg": "Book not found"}), 404

    book["title"] = data.get("title", book["title"])
    book["author"] = data.get("author", book["author"])
    return jsonify(book)

# ──────────────────────────  RUN  ────────────────────────────
if __name__ == "__main__":
    app.run(port=5001, debug=True)   # runs on http://127.0.0.1:5001 
