
import os
import random
import re
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, flash, session
)
from flask_sqlalchemy import SQLAlchemy
from sentence_transformers import SentenceTransformer, util
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------------------
# Environment Configuration
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")
database_url = os.getenv("DATABASE_URL")

if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")

if not database_url:
    raise RuntimeError("DATABASE_URL is missing from .env")

# ------------------------------
# PostgreSQL Configuration
# ------------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------------------
# User Model
# ------------------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# ------------------------------
# 1. Load and preprocess Q/A corpus
# ------------------------------
qa_pairs = {}

def load_corpus(filename="KnowYourLaw.txt"):
    global qa_pairs

    qa_pairs = {}
    corpus_path = BASE_DIR / filename

    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus file not found: {corpus_path}")

    with open(corpus_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Split the corpus at every question marker
    blocks = re.split(r"(?m)^\s*Q:", content)

    for block in blocks:
        block = block.strip()

        if not block or "A:" not in block:
            continue

        question, answer = block.split("A:", 1)

        question = question.strip().lower()
        answer = answer.strip()

        if question and answer:
            qa_pairs[question] = answer


load_corpus()

# ------------------------------
# 2. Setup semantic model
# ------------------------------
print("Loading semantic model (first run may download it)...")

model = SentenceTransformer("all-MiniLM-L6-v2")

corpus_questions = list(qa_pairs.keys())

if corpus_questions:
    corpus_embeddings = model.encode(
        corpus_questions,
        convert_to_tensor=True
    )
else:
    corpus_embeddings = None
    print("Warning: No valid questions found in the corpus.")


# ------------------------------
# 3. Greeting Logic
# ------------------------------
GREET_INPUTS = (
    "hello", "hi", "greetings", "sup",
    "what's up", "hey"
)

GREET_RESPONSES = [
    "hi",
    "hey",
    "nods",
    "hi there",
    "hello",
    "I am glad! You are talking to me"
]


def greet(sentence):
    if not sentence:
        return None

    text = sentence.strip().lower()

    if text in GREET_INPUTS:
        return random.choice(GREET_RESPONSES)

    return None


# ------------------------------
# 4. Hybrid Response Function
# ------------------------------
def hybrid_response(user_query):
    if not user_query or not user_query.strip():
        return "Please enter a question."

    q = user_query.lower().strip()

    # Step 1: Direct match
    if q in qa_pairs:
        return qa_pairs[q]

    # Step 2: Semantic similarity
    if corpus_embeddings is None:
        return "The knowledge corpus is currently unavailable."

    query_embedding = model.encode(q, convert_to_tensor=True)

    scores = util.cos_sim(
        query_embedding,
        corpus_embeddings
    )[0]

    best_idx = int(scores.argmax())
    best_score = float(scores[best_idx])

    if best_score > 0.60:
        return qa_pairs[corpus_questions[best_idx]]

    return "I'm not sure about that. Could you rephrase or ask something else?"


# ------------------------------
# 5. Home Route
# ------------------------------
@app.route("/")
def home():
    return render_template(
        "index.html",
        username=session.get("username")
    )


# ------------------------------
# 6. Login Route
# ------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username

            flash("Login successful!", "success")
            return redirect(url_for("home"))

        flash("Invalid username or password", "danger")

    return render_template("login.html")


# ------------------------------
# 7. Signup Route
# ------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please fill in all fields.", "danger")
            return render_template("signup.html")

        hashed_password = generate_password_hash(
            password,
            method="pbkdf2:sha256"
        )

        try:
            new_user = User(
                username=username,
                email=email,
                password=hashed_password
            )

            db.session.add(new_user)
            db.session.commit()

            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))

        except Exception:
            db.session.rollback()
            app.logger.exception("Signup failed")
            flash("Signup failed. Please try again.", "danger")

    return render_template("signup.html")


# ------------------------------
# 8. Logout Route
# ------------------------------
@app.route("/logout")
def logout():
    session.clear()

    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ------------------------------
# 9. Forgot Password Route
# ------------------------------
@app.route("/forgetpassword", methods=["GET", "POST"])
def forgetpassword():
    if request.method == "POST":
        flash(
            "Password reset is not configured yet. Please contact the administrator.",
            "warning"
        )
        return redirect(url_for("login"))

    return render_template("forgetpassword.html")


# ------------------------------
# 10. Chatbot AJAX Endpoint
# ------------------------------
@app.route("/get", methods=["POST"])
def get_bot_response():
    data = request.get_json(silent=True) or {}
    user_input = data.get("msg", "")

    if not isinstance(user_input, str) or not user_input.strip():
        return jsonify({"response": "Please enter a question."}), 400

    greet_resp = greet(user_input)

    if greet_resp:
        return jsonify({"response": greet_resp})

    response = hybrid_response(user_input)

    return jsonify({"response": response})


# ------------------------------
# 11. Chatbot Form Endpoint
# ------------------------------
@app.route("/get_answer", methods=["POST"])
def get_answer():
    user_input = request.form.get("user_input", "")

    greet_resp = greet(user_input)

    if greet_resp:
        response = greet_resp
    else:
        response = hybrid_response(user_input)

    return render_template(
        "index.html",
        answer=response,
        username=session.get("username")
    )


# ------------------------------
# 12. Profile Route
# ------------------------------
@app.route("/profile")
def profile():
    if not session.get("user_id"):
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        username=session.get("username")
    )


# ------------------------------
# Run Application
# ------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=False)
