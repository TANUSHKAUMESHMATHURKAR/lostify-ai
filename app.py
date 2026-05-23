import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session

# ---------- AI MATCH (IMPROVED) ----------
def ai_match_score(lost_desc, found_desc):
    lost_words = set(lost_desc.lower().split())
    found_words = set(found_desc.lower().split())

    if not lost_words or not found_words:
        return "0%"

    common = lost_words & found_words
    score = (len(common) / max(len(lost_words), 1)) * 100

    return f"{min(100, round(score))}%"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

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

    match_score = ai_match_score(
        "black wallet card",
        "black leather wallet library"
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

        if image and image.filename:
            filename = secure_filename(image.filename)

            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image.save(image_path)

        new = {
            "item": item,
            "location": location,
            "type": item_type,
            "image": image_path,
            "match": "Processing..."
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
