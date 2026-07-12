"""
Library AI Agent — Flask Application
======================================
AI-powered library management and book recommendation system
using IBM watsonx.ai with IBM Granite foundation models.

Author  : Library AI Agent Team
Version : 1.0.0
"""

import os
from datetime import datetime
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, flash
)
from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# ──────────────────────────────────────────────────────────────
# AGENT INSTRUCTIONS  (edit this section to customise the agent)
# ──────────────────────────────────────────────────────────────
AGENT_INSTRUCTIONS = {
    # How the agent introduces itself and its tone
    "personality": (
        "You are LibraryBot, a friendly and knowledgeable AI library assistant "
        "at a university library. You are helpful, encouraging, and academic in tone. "
        "You always respond in a structured, easy-to-read format."
    ),

    # How recommendations are presented
    "recommendation_style": (
        "Always recommend books in a numbered list. "
        "For each book include: Title, Author, Why it is recommended, "
        "and Difficulty level (Beginner / Intermediate / Advanced). "
        "If online resources are requested, include free URLs when possible."
    ),

    # Academic rules for recommendations
    "academic_rules": (
        "Tailor recommendations to the student's branch (e.g. CSE, ECE, ME), "
        "semester, and subject. "
        "For 1st and 2nd semester students prefer introductory texts. "
        "For 3rd semester and above include standard textbooks and references. "
        "For final-year or placement preparation include competitive and advanced titles."
    ),

    # Safety and scope rules
    "safety_instructions": (
        "Only answer questions related to books, academics, library services, and learning resources. "
        "If asked about unrelated topics politely redirect the student to library-related queries. "
        "Never provide harmful, offensive, or inappropriate content. "
        "Do not make up ISBNs or publication years you are unsure about."
    ),

    # Tone and language
    "conversation_tone": (
        "Use a warm, polite, and motivating tone. "
        "Address the student respectfully. "
        "Keep responses concise but informative. "
        "Use bullet points and numbered lists for clarity."
    ),

    # Core recommendation logic
    "recommendation_logic": (
        "1. Identify the student's branch, semester, and subject from the query.\n"
        "2. Determine the difficulty level requested or infer it from context.\n"
        "3. Recommend 3–5 primary books with reasons.\n"
        "4. Suggest 2–3 similar/alternate books.\n"
        "5. If the topic is practical (coding, lab work), also recommend online resources.\n"
        "6. If a specific book is requested but unavailable, suggest the closest alternative.\n"
        "7. For placement preparation include aptitude, reasoning, and DS/Algo books."
    ),
}

# ──────────────────────────────────────────────────────────────
# Application Bootstrap
# ──────────────────────────────────────────────────────────────
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")


# ──────────────────────────────────────────────────────────────
# IBM watsonx.ai Client Initialisation
# ──────────────────────────────────────────────────────────────
def get_watsonx_model() -> ModelInference:
    """Return an initialised IBM watsonx.ai ModelInference instance."""
    credentials = Credentials(
        url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
        api_key=os.getenv("IBM_API_KEY"),
    )
    client = APIClient(credentials)
    model = ModelInference(
        model_id=os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct"),
        credentials=credentials,
        project_id=os.getenv("WATSONX_PROJECT_ID"),
        params={
            GenParams.MAX_NEW_TOKENS: 1024,
            GenParams.TEMPERATURE: 0.7,
            GenParams.TOP_P: 0.9,
            GenParams.REPETITION_PENALTY: 1.1,
        },
    )
    return model


# ──────────────────────────────────────────────────────────────
# Sample Book Database  (replace / extend with a real DB)
# ──────────────────────────────────────────────────────────────
BOOKS_DB = [
    {
        "id": 1, "title": "Introduction to Algorithms", "author": "Cormen, Leiserson, Rivest, Stein",
        "category": "Computer Science", "subject": "Data Structures & Algorithms",
        "edition": "4th Edition", "publication": "MIT Press", "available": True,
        "copies": 5, "shelf": "CS-A1", "difficulty": "Intermediate",
        "description": "The most comprehensive and authoritative guide to algorithms used in computer science.",
        "tags": ["algorithms", "data structures", "programming", "CSE"],
        "similar": [2, 3],
    },
    {
        "id": 2, "title": "Data Structures and Algorithms in Python",
        "author": "Michael T. Goodrich", "category": "Computer Science",
        "subject": "Data Structures", "edition": "1st Edition",
        "publication": "Wiley", "available": True, "copies": 3,
        "shelf": "CS-A2", "difficulty": "Beginner",
        "description": "A practical, Python-based approach to learning data structures and algorithm design.",
        "tags": ["python", "data structures", "beginner", "CSE"],
        "similar": [1, 3],
    },
    {
        "id": 3, "title": "Artificial Intelligence: A Modern Approach",
        "author": "Stuart Russell & Peter Norvig", "category": "Artificial Intelligence",
        "subject": "Artificial Intelligence", "edition": "4th Edition",
        "publication": "Pearson", "available": False, "copies": 0,
        "shelf": "AI-B1", "difficulty": "Advanced",
        "description": "The definitive textbook on AI, covering all major sub-fields comprehensively.",
        "tags": ["AI", "machine learning", "search", "CSE", "advanced"],
        "similar": [4, 5],
    },
    {
        "id": 4, "title": "Machine Learning: A Probabilistic Perspective",
        "author": "Kevin P. Murphy", "category": "Machine Learning",
        "subject": "Machine Learning", "edition": "1st Edition",
        "publication": "MIT Press", "available": True, "copies": 2,
        "shelf": "ML-C1", "difficulty": "Advanced",
        "description": "A unified probabilistic approach to machine learning algorithms and theory.",
        "tags": ["machine learning", "probability", "deep learning", "CSE"],
        "similar": [3, 5],
    },
    {
        "id": 5, "title": "Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow",
        "author": "Aurélien Géron", "category": "Machine Learning",
        "subject": "Machine Learning", "edition": "3rd Edition",
        "publication": "O'Reilly", "available": True, "copies": 4,
        "shelf": "ML-C2", "difficulty": "Intermediate",
        "description": "A practical guide to building intelligent systems using modern ML frameworks.",
        "tags": ["machine learning", "python", "tensorflow", "keras", "CSE"],
        "similar": [4, 6],
    },
    {
        "id": 6, "title": "Clean Code", "author": "Robert C. Martin",
        "category": "Software Engineering", "subject": "Software Development",
        "edition": "1st Edition", "publication": "Prentice Hall",
        "available": True, "copies": 6, "shelf": "SE-D1", "difficulty": "Intermediate",
        "description": "A handbook of agile software craftsmanship — write code that is clean, readable, and maintainable.",
        "tags": ["programming", "best practices", "software engineering", "CSE"],
        "similar": [7, 8],
    },
    {
        "id": 7, "title": "The Pragmatic Programmer", "author": "David Thomas & Andrew Hunt",
        "category": "Software Engineering", "subject": "Software Development",
        "edition": "20th Anniversary Edition", "publication": "Addison-Wesley",
        "available": True, "copies": 3, "shelf": "SE-D2", "difficulty": "Intermediate",
        "description": "Timeless advice for programmers on professional development practices.",
        "tags": ["programming", "career", "best practices", "CSE"],
        "similar": [6, 8],
    },
    {
        "id": 8, "title": "Computer Networks", "author": "Andrew S. Tanenbaum",
        "category": "Networking", "subject": "Computer Networks",
        "edition": "5th Edition", "publication": "Pearson",
        "available": True, "copies": 7, "shelf": "NET-E1", "difficulty": "Intermediate",
        "description": "A thorough treatment of computer networking from physical layer to application layer.",
        "tags": ["networking", "protocols", "internet", "CSE", "ECE"],
        "similar": [9],
    },
    {
        "id": 9, "title": "Operating System Concepts", "author": "Silberschatz, Galvin & Gagne",
        "category": "Operating Systems", "subject": "Operating Systems",
        "edition": "10th Edition", "publication": "Wiley",
        "available": False, "copies": 0, "shelf": "OS-F1", "difficulty": "Intermediate",
        "description": "The 'Dinosaur Book' — the standard reference for operating systems education.",
        "tags": ["OS", "processes", "memory", "CSE"],
        "similar": [10],
    },
    {
        "id": 10, "title": "Database System Concepts",
        "author": "Silberschatz, Korth & Sudarshan",
        "category": "Database", "subject": "Database Management Systems",
        "edition": "7th Edition", "publication": "McGraw Hill",
        "available": True, "copies": 5, "shelf": "DB-G1", "difficulty": "Intermediate",
        "description": "Comprehensive coverage of database design, SQL, transactions, and storage.",
        "tags": ["DBMS", "SQL", "database", "CSE"],
        "similar": [8, 9],
    },
    {
        "id": 11, "title": "Python Crash Course", "author": "Eric Matthes",
        "category": "Programming", "subject": "Python Programming",
        "edition": "3rd Edition", "publication": "No Starch Press",
        "available": True, "copies": 8, "shelf": "PY-H1", "difficulty": "Beginner",
        "description": "A fast-paced, thorough introduction to Python programming for absolute beginners.",
        "tags": ["python", "beginner", "programming", "CSE"],
        "similar": [12, 2],
    },
    {
        "id": 12, "title": "Automate the Boring Stuff with Python", "author": "Al Sweigart",
        "category": "Programming", "subject": "Python Programming",
        "edition": "2nd Edition", "publication": "No Starch Press",
        "available": True, "copies": 4, "shelf": "PY-H2", "difficulty": "Beginner",
        "description": "Learn Python automation for real-world tasks — a practical, project-driven guide.",
        "tags": ["python", "automation", "beginner", "CSE"],
        "similar": [11, 2],
    },
    {
        "id": 13, "title": "Cracking the Coding Interview", "author": "Gayle Laakmann McDowell",
        "category": "Competitive Programming", "subject": "Placement Preparation",
        "edition": "6th Edition", "publication": "CareerCup",
        "available": True, "copies": 10, "shelf": "CP-I1", "difficulty": "Intermediate",
        "description": "189 programming interview questions with solutions — the go-to placement prep book.",
        "tags": ["placement", "interviews", "algorithms", "DSA", "CSE"],
        "similar": [1, 14],
    },
    {
        "id": 14, "title": "A Quantitative Aptitude", "author": "R.S. Aggarwal",
        "category": "Aptitude", "subject": "Placement Preparation",
        "edition": "Latest Edition", "publication": "S. Chand",
        "available": True, "copies": 12, "shelf": "AP-J1", "difficulty": "Beginner",
        "description": "The most widely used aptitude book for competitive exams and campus placements.",
        "tags": ["aptitude", "placement", "quantitative", "reasoning"],
        "similar": [13, 15],
    },
    {
        "id": 15, "title": "Digital Electronics", "author": "Morris Mano",
        "category": "Electronics", "subject": "Digital Electronics",
        "edition": "5th Edition", "publication": "Pearson",
        "available": True, "copies": 6, "shelf": "EC-K1", "difficulty": "Beginner",
        "description": "A foundational text on digital logic design, Boolean algebra, and combinational circuits.",
        "tags": ["digital", "electronics", "ECE", "logic"],
        "similar": [8],
    },
]

# In-memory reservation store  {book_id: [student_names]}
RESERVATIONS: dict[int, list[str]] = {}
WAITLIST: dict[int, list[str]] = {}


# ──────────────────────────────────────────────────────────────
# Helper Utilities
# ──────────────────────────────────────────────────────────────
def build_system_prompt() -> str:
    """Assemble the full system prompt from AGENT_INSTRUCTIONS."""
    ai = AGENT_INSTRUCTIONS
    return (
        f"{ai['personality']}\n\n"
        f"RECOMMENDATION STYLE:\n{ai['recommendation_style']}\n\n"
        f"ACADEMIC RULES:\n{ai['academic_rules']}\n\n"
        f"SAFETY:\n{ai['safety_instructions']}\n\n"
        f"TONE:\n{ai['conversation_tone']}\n\n"
        f"RECOMMENDATION LOGIC:\n{ai['recommendation_logic']}"
    )


def format_chat_prompt(history: list[dict], user_message: str) -> str:
    """Format conversation history + new message into a Granite prompt."""
    system_prompt = build_system_prompt()
    prompt = f"<|system|>\n{system_prompt}\n"
    for turn in history[-6:]:          # keep last 6 turns for context
        role = turn.get("role", "user")
        content = turn.get("content", "")
        prompt += f"<|{role}|>\n{content}\n"
    prompt += f"<|user|>\n{user_message}\n<|assistant|>\n"
    return prompt


def search_books(query: str) -> list[dict]:
    """Search the local book database for a query string."""
    query_lower = query.lower()
    results = []
    for book in BOOKS_DB:
        searchable = " ".join([
            book["title"], book["author"], book["category"],
            book["subject"], " ".join(book["tags"])
        ]).lower()
        if query_lower in searchable:
            results.append(book)
    return results


def get_book_by_id(book_id: int) -> dict | None:
    """Return a book dict by its ID."""
    for book in BOOKS_DB:
        if book["id"] == book_id:
            return book
    return None


def get_similar_books(book: dict) -> list[dict]:
    """Return similar book objects for a given book."""
    return [b for b in BOOKS_DB if b["id"] in book.get("similar", [])]


# ──────────────────────────────────────────────────────────────
# Demo Users  (replace with a real DB / auth system in production)
# ──────────────────────────────────────────────────────────────
USERS_DB = {
    "student1": {
        "password": "pass123", "name": "Arjun Sharma",
        "branch": "CSE", "semester": 5, "roll": "21CS001",
        "interests": ["Machine Learning", "Web Development"],
    },
    "student2": {
        "password": "pass123", "name": "Priya Patel",
        "branch": "ECE", "semester": 3, "roll": "21EC042",
        "interests": ["Digital Electronics", "Embedded Systems"],
    },
    "demo": {
        "password": "demo", "name": "Demo Student",
        "branch": "CSE", "semester": 3, "roll": "DEMO001",
        "interests": ["Python", "Data Structures"],
    },
}


# ──────────────────────────────────────────────────────────────
# Route — Login
# ──────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = USERS_DB.get(username)
        if user and user["password"] == password:
            session["username"] = username
            session["user"] = {k: v for k, v in user.items() if k != "password"}
            session["chat_history"] = []
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("home"))
        flash("Invalid credentials. Try demo / demo.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ──────────────────────────────────────────────────────────────
# Route — Home
# ──────────────────────────────────────────────────────────────
@app.route("/home")
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    recent_books = BOOKS_DB[:6]
    return render_template("index.html", user=session["user"], recent_books=recent_books)


# ──────────────────────────────────────────────────────────────
# Route — Dashboard
# ──────────────────────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    reserved_ids = RESERVATIONS.get(session["username"], [])
    reserved_books = [get_book_by_id(bid) for bid in reserved_ids if get_book_by_id(bid)]
    waitlisted_ids = WAITLIST.get(session["username"], [])
    waitlisted_books = [get_book_by_id(bid) for bid in waitlisted_ids if get_book_by_id(bid)]

    # Branch-based personalised picks
    branch = user.get("branch", "CSE")
    branch_books = [b for b in BOOKS_DB if branch in b.get("tags", [])][:4]

    stats = {
        "total_books": len(BOOKS_DB),
        "available": sum(1 for b in BOOKS_DB if b["available"]),
        "reserved": len(reserved_books),
        "waitlisted": len(waitlisted_books),
    }
    return render_template(
        "dashboard.html",
        user=user,
        reserved_books=reserved_books,
        waitlisted_books=waitlisted_books,
        branch_books=branch_books,
        stats=stats,
    )


# ──────────────────────────────────────────────────────────────
# Route — Search
# ──────────────────────────────────────────────────────────────
@app.route("/search")
def search():
    if "username" not in session:
        return redirect(url_for("login"))
    query = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip()
    difficulty_filter = request.args.get("difficulty", "").strip()

    results = search_books(query) if query else list(BOOKS_DB)

    if category_filter:
        results = [b for b in results if b["category"].lower() == category_filter.lower()]
    if difficulty_filter:
        results = [b for b in results if b["difficulty"].lower() == difficulty_filter.lower()]

    categories = sorted({b["category"] for b in BOOKS_DB})
    return render_template(
        "search.html",
        user=session["user"],
        books=results,
        query=query,
        categories=categories,
        category_filter=category_filter,
        difficulty_filter=difficulty_filter,
    )


# ──────────────────────────────────────────────────────────────
# Route — Book Detail
# ──────────────────────────────────────────────────────────────
@app.route("/book/<int:book_id>")
def book_detail(book_id: int):
    if "username" not in session:
        return redirect(url_for("login"))
    book = get_book_by_id(book_id)
    if not book:
        flash("Book not found.", "warning")
        return redirect(url_for("search"))
    similar = get_similar_books(book)
    username = session["username"]
    is_reserved = book_id in RESERVATIONS.get(username, [])
    is_waitlisted = book_id in WAITLIST.get(username, [])
    return render_template(
        "book_detail.html",
        user=session["user"],
        book=book,
        similar=similar,
        is_reserved=is_reserved,
        is_waitlisted=is_waitlisted,
    )


# ──────────────────────────────────────────────────────────────
# Route — AI Chat Page
# ──────────────────────────────────────────────────────────────
@app.route("/chat")
def chat():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("chat.html", user=session["user"])


# ──────────────────────────────────────────────────────────────
# API — AI Chat (JSON endpoint)
# ──────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def api_chat():
    if "username" not in session:
        return jsonify({"error": "Unauthorised"}), 401

    data = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    history: list[dict] = session.get("chat_history", [])
    prompt = format_chat_prompt(history, user_message)

    try:
        model = get_watsonx_model()
        response = model.generate_text(prompt=prompt)
        bot_reply = response.strip() if response else "I'm sorry, I couldn't generate a response."
    except Exception as exc:
        # Graceful fallback so the UI never breaks
        bot_reply = (
            "⚠️ I'm having trouble connecting to the AI service right now. "
            "Please check your IBM API credentials in the .env file and try again.\n\n"
            f"Technical detail: {str(exc)}"
        )

    # Persist history in session (cap at 20 turns)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": bot_reply})
    session["chat_history"] = history[-20:]

    return jsonify({
        "reply": bot_reply,
        "timestamp": datetime.now().strftime("%H:%M"),
    })


# ──────────────────────────────────────────────────────────────
# API — Clear Chat History
# ──────────────────────────────────────────────────────────────
@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    if "username" not in session:
        return jsonify({"error": "Unauthorised"}), 401
    session["chat_history"] = []
    return jsonify({"status": "ok"})


# ──────────────────────────────────────────────────────────────
# API — Reserve a Book
# ──────────────────────────────────────────────────────────────
@app.route("/api/reserve/<int:book_id>", methods=["POST"])
def api_reserve(book_id: int):
    if "username" not in session:
        return jsonify({"error": "Unauthorised"}), 401
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    username = session["username"]
    user_reservations = RESERVATIONS.setdefault(username, [])
    user_waitlist = WAITLIST.setdefault(username, [])

    if book_id in user_reservations:
        return jsonify({"status": "already_reserved", "message": "You have already reserved this book."})

    if book["available"] and book["copies"] > 0:
        user_reservations.append(book_id)
        book["copies"] -= 1
        if book["copies"] == 0:
            book["available"] = False
        return jsonify({"status": "reserved", "message": f"'{book['title']}' has been reserved successfully!"})
    else:
        # Add to waitlist
        if book_id not in user_waitlist:
            user_waitlist.append(book_id)
            return jsonify({"status": "waitlisted", "message": f"Book unavailable. You have been added to the waitlist for '{book['title']}'."})
        return jsonify({"status": "already_waitlisted", "message": "You are already on the waitlist for this book."})


# ──────────────────────────────────────────────────────────────
# API — Cancel Reservation
# ──────────────────────────────────────────────────────────────
@app.route("/api/cancel/<int:book_id>", methods=["POST"])
def api_cancel(book_id: int):
    if "username" not in session:
        return jsonify({"error": "Unauthorised"}), 401
    book = get_book_by_id(book_id)
    username = session["username"]
    user_reservations = RESERVATIONS.get(username, [])
    if book_id in user_reservations:
        user_reservations.remove(book_id)
        if book:
            book["copies"] += 1
            book["available"] = True
        return jsonify({"status": "cancelled", "message": "Reservation cancelled."})
    return jsonify({"status": "not_found", "message": "No reservation found."})


# ──────────────────────────────────────────────────────────────
# API — Quick Book Search (AJAX)
# ──────────────────────────────────────────────────────────────
@app.route("/api/books/search")
def api_books_search():
    query = request.args.get("q", "").strip()
    results = search_books(query) if query else []
    return jsonify(results[:10])


# ──────────────────────────────────────────────────────────────
# Route — Contact Librarian
# ──────────────────────────────────────────────────────────────
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        flash("Your message has been sent to the librarian. We will respond within 24 hours.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html", user=session["user"])


# ──────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
