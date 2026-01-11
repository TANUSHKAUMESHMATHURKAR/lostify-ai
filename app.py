import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session

# ---------- AI MATCH (Gemini-ready MOCK) ----------
def ai_match_score(lost_desc, found_desc):
    """
    Gemini AI ready logic (mocked for hackathon MVP)
    Future scope: Google Gemini API for semantic similarity
    """
    return "87%"

app = Flask(__name__)
app.secret_key = "codestorm-secret"

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- DATA ----------------
USERS = {}
REPORTS = []

REVIEWS = [
    {"name": "Ankit", "rating": "5", "text": "Got my phone back in 2 hours 🔥"},
    {"name": "Neha", "rating": "4", "text": "Perfect for college campus"},
    {"name": "Jury", "rating": "5", "text": "Hackathon winning idea 🚀"}
]

# ---------------- AUTH ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if USERS.get(email) == password:
            session["user"] = email
            return redirect(url_for("home"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        USERS[request.form.get("email")] = request.form.get("password")
        return redirect(url_for("login"))
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- HOME ----------------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    # Demo AI score (for judges explanation)
    match_score = ai_match_score(
        "Black wallet with card",
        "Black leather wallet near library"
    )

    return render_template(
        "home.html",
        reviews=REVIEWS,
        match_score=match_score
    )

# ---------------- REPORT ----------------
@app.route("/report", methods=["GET", "POST"])
def report():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        item = request.form.get("item_name", "").lower()
        location = request.form.get("location", "")
        item_type = request.form.get("type", "")

        image = request.files.get("image")
        image_path = None

        if image and image.filename != "":
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)

        new = {
            "item": item,
            "location": location,
            "type": item_type,   # lost / found
            "image": image_path,
            "match": "—"
        }

        for r in REPORTS:
            if r["item"] == new["item"] and r["type"] != new["type"]:
                score = ai_match_score(r["item"], new["item"])
                r["match"] = score
                new["match"] = score

        REPORTS.append(new)
        return redirect(url_for("feed"))

    return render_template("report.html")

# ---------------- FEED ----------------
@app.route("/feed")
def feed():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("feed.html", reports=REPORTS)

# ---------------- REVIEWS ----------------
@app.route("/add-review", methods=["POST"])
def add_review():
    REVIEWS.append({
        "name": request.form.get("name"),
        "rating": request.form.get("rating"),
        "text": request.form.get("review")
    })
    return redirect(url_for("home"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
